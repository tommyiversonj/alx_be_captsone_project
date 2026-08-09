from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from inventory.models import Category, Product, Supplier
from stock.models import StockMovement
from users.models import User
from .models import Purchase


class PurchaseCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='clerk', password='password')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Test Category")
        self.supplier = Supplier.objects.create(name="Acme Supplies")
        self.product = Product.objects.create(
            name="Widget", category=self.category, price=10, quantity_in_stock=5
        )
        self.list_url = reverse('purchase-list')

    def test_purchase_increments_product_stock(self):
        data = {
            "supplier": self.supplier.id,
            "items": [{"product": self.product.id, "quantity": 7, "unit_price": "8.00"}],
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 12)

    def test_purchase_creates_in_stock_movement(self):
        data = {
            "supplier": self.supplier.id,
            "items": [{"product": self.product.id, "quantity": 7, "unit_price": "8.00"}],
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        movement = StockMovement.objects.get(product=self.product)
        self.assertEqual(movement.movement_type, 'IN')
        self.assertEqual(movement.quantity, 7)
        self.assertEqual(movement.related_purchase_id, response.data['id'])

    def test_purchase_with_multiple_items_increments_each_product(self):
        other_product = Product.objects.create(
            name="Gadget", category=self.category, price=5, quantity_in_stock=0
        )
        data = {
            "supplier": self.supplier.id,
            "items": [
                {"product": self.product.id, "quantity": 3, "unit_price": "8.00"},
                {"product": other_product.id, "quantity": 10, "unit_price": "4.00"},
            ],
        }
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        other_product.refresh_from_db()
        self.assertEqual(self.product.quantity_in_stock, 8)
        self.assertEqual(other_product.quantity_in_stock, 10)

    def test_purchase_with_no_items_rejected(self):
        data = {"supplier": self.supplier.id, "items": []}
        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Purchase.objects.count(), 0)
        # Previously a bare list instead of the standardized {"detail": "..."} shape.
        self.assertIn('detail', response.data)

    def test_total_amount_sums_items(self):
        data = {
            "supplier": self.supplier.id,
            "items": [
                {"product": self.product.id, "quantity": 2, "unit_price": "8.00"},
                {"product": self.product.id, "quantity": 1, "unit_price": "8.00"},
            ],
        }
        response = self.client.post(self.list_url, data, format='json')
        purchase = Purchase.objects.get(id=response.data['id'])
        self.assertEqual(purchase.total_amount, 24)

    def test_unauthenticated_request_rejected(self):
        self.client.force_authenticate(user=None)
        data = {
            "supplier": self.supplier.id,
            "items": [{"product": self.product.id, "quantity": 1, "unit_price": "8.00"}],
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
