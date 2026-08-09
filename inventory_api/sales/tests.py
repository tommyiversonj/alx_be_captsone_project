import threading
import time

from django.db import connection, models, transaction
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from inventory.models import Category, Product
from stock.models import StockMovement
from users.models import User
from .models import Sale


class SaleCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='clerk', password='password')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Widget", category=self.category, price=10, quantity_in_stock=20
        )
        self.list_url = reverse('sale-list')

    def test_sale_decrements_product_stock(self):
        data = {"items": [{"product": self.product.id, "quantity": 5, "unit_price": "10.00"}]}
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 15)

    def test_sale_creates_out_stock_movement(self):
        data = {"items": [{"product": self.product.id, "quantity": 5, "unit_price": "10.00"}]}
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        movement = StockMovement.objects.get(product=self.product)
        self.assertEqual(movement.movement_type, 'OUT')
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(movement.related_sale_id, response.data['id'])

    def test_sale_rejected_when_stock_insufficient(self):
        data = {"items": [{"product": self.product.id, "quantity": 999, "unit_price": "10.00"}]}
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 20)
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_sale_with_no_items_rejected(self):
        response = self.client.post(self.list_url, {"items": []}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Sale.objects.count(), 0)
        # Previously a bare list (["A sale must have at least one item."])
        # instead of the standardized {"detail": "..."} shape.
        self.assertIn('detail', response.data)

    def test_sale_rolls_back_when_one_of_several_items_is_insufficient(self):
        other_product = Product.objects.create(
            name="Gadget", category=self.category, price=5, quantity_in_stock=3
        )
        data = {
            "items": [
                {"product": self.product.id, "quantity": 5, "unit_price": "10.00"},
                {"product": other_product.id, "quantity": 999, "unit_price": "5.00"},
            ]
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.product.refresh_from_db()
        other_product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 20)
        self.assertEqual(other_product.quantity_in_stock, 3)
        self.assertEqual(Sale.objects.count(), 0)

    def test_sale_rejects_duplicate_line_items_that_together_exceed_stock(self):
        # Two line items for the same product each look affordable in isolation
        # (5 <= 20 available) but together (10) still fit here - should succeed.
        data = {
            "items": [
                {"product": self.product.id, "quantity": 5, "unit_price": "10.00"},
                {"product": self.product.id, "quantity": 5, "unit_price": "10.00"},
            ]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 10)

    def test_sale_rejects_duplicate_line_items_that_together_overrun_stock(self):
        # Each line item is individually within stock (12 <= 20) but the combined
        # total (24) exceeds it - this must be rejected, not partially applied.
        data = {
            "items": [
                {"product": self.product.id, "quantity": 12, "unit_price": "10.00"},
                {"product": self.product.id, "quantity": 12, "unit_price": "10.00"},
            ]
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 20)
        self.assertEqual(Sale.objects.count(), 0)

    def test_total_amount_sums_items(self):
        data = {
            "items": [
                {"product": self.product.id, "quantity": 2, "unit_price": "10.00"},
                {"product": self.product.id, "quantity": 1, "unit_price": "10.00"},
            ]
        }
        response = self.client.post(self.list_url, data, format='json')
        sale = Sale.objects.get(id=response.data['id'])
        self.assertEqual(sale.total_amount, 30)

    def test_unauthenticated_request_rejected(self):
        self.client.force_authenticate(user=None)
        data = {"items": [{"product": self.product.id, "quantity": 1, "unit_price": "10.00"}]}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SaleConcurrencyTest(TransactionTestCase):
    """
    Proves the select_for_update() fix actually serializes concurrent sales
    of the same product, instead of relying on luck/timing to catch a race.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='clerk', password='password')
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Widget", category=self.category, price=10, quantity_in_stock=10
        )
        self.list_url = reverse('sale-list')

    def test_second_sale_blocks_on_lock_and_sees_updated_stock(self):
        lock_acquired = threading.Event()
        release_lock = threading.Event()

        def hold_lock_then_decrement():
            try:
                with transaction.atomic():
                    locked = Product.objects.select_for_update().get(pk=self.product.pk)
                    lock_acquired.set()
                    release_lock.wait(timeout=5)
                    locked.quantity_in_stock = models.F('quantity_in_stock') - 6
                    locked.save(update_fields=['quantity_in_stock'])
            finally:
                connection.close()

        holder = threading.Thread(target=hold_lock_then_decrement)
        holder.start()
        self.assertTrue(
            lock_acquired.wait(timeout=5), "Lock-holding thread never acquired the row lock."
        )

        def release_after_delay():
            time.sleep(0.3)
            release_lock.set()

        threading.Thread(target=release_after_delay).start()

        client = APIClient()
        client.force_authenticate(user=self.user)
        data = {"items": [{"product": self.product.id, "quantity": 8, "unit_price": "10.00"}]}

        started_at = time.monotonic()
        response = client.post(self.list_url, data, format='json')
        elapsed = time.monotonic() - started_at

        holder.join(timeout=5)

        # If the fix weren't in place, this request would run immediately
        # against stale (pre-decrement) stock instead of waiting on the lock.
        self.assertGreaterEqual(elapsed, 0.25, "Second sale did not block on the row lock.")

        self.product.refresh_from_db()
        # First transaction takes stock 10 -> 4. The second sale then asks
        # for 8 against the now-locked, up-to-date value of 4, which is
        # insufficient, so it must be rejected - not double-applied, not
        # allowed to drive stock negative.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.product.quantity_in_stock, 4)
