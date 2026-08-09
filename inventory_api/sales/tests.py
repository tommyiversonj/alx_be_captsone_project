from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 20)
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_sale_with_no_items_rejected(self):
        response = self.client.post(self.list_url, {"items": []}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Sale.objects.count(), 0)

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
