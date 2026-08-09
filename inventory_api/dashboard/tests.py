from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from inventory.models import Category, Product
from sales.models import Sale, SaleItem
from users.models import User


class DashboardTestBase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='clerk', password='password')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Test Category")


class LowStockTest(DashboardTestBase):
    def test_returns_only_products_at_or_below_threshold(self):
        low = Product.objects.create(
            name="Low", category=self.category, price=5,
            quantity_in_stock=2, low_stock_threshold=5,
        )
        Product.objects.create(
            name="Healthy", category=self.category, price=5,
            quantity_in_stock=50, low_stock_threshold=5,
        )
        at_threshold = Product.objects.create(
            name="AtThreshold", category=self.category, price=5,
            quantity_in_stock=5, low_stock_threshold=5,
        )

        response = self.client.get(reverse('dashboard-low-stock'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {row['id'] for row in response.data}
        self.assertEqual(returned_ids, {low.id, at_threshold.id})

    def test_unauthenticated_request_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('dashboard-low-stock'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TotalSalesTest(DashboardTestBase):
    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            name="Widget", category=self.category, price=10, quantity_in_stock=100
        )

    def _make_sale(self, quantity, unit_price):
        sale = Sale.objects.create()
        SaleItem.objects.create(
            sale=sale, product=self.product, quantity=quantity, unit_price=unit_price
        )
        return sale

    def test_totals_across_all_sales(self):
        self._make_sale(3, "10.00")
        self._make_sale(2, "5.00")

        response = self.client.get(reverse('dashboard-total-sales'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sales_count'], 2)
        self.assertEqual(response.data['total_revenue'], '40.00')

    def test_zero_sales_returns_zero_not_error(self):
        response = self.client.get(reverse('dashboard-total-sales'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sales_count'], 0)
        self.assertEqual(response.data['total_revenue'], '0.00')

    def test_date_range_filters_out_of_range_sales(self):
        self._make_sale(1, "10.00")

        response = self.client.get(
            reverse('dashboard-total-sales'), {'start_date': '2999-01-01'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sales_count'], 0)


class TopProductsTest(DashboardTestBase):
    def setUp(self):
        super().setUp()
        self.best_seller = Product.objects.create(
            name="Best Seller", category=self.category, price=10, quantity_in_stock=100
        )
        self.slow_mover = Product.objects.create(
            name="Slow Mover", category=self.category, price=10, quantity_in_stock=100
        )
        sale = Sale.objects.create()
        SaleItem.objects.create(sale=sale, product=self.best_seller, quantity=10, unit_price="10.00")
        SaleItem.objects.create(sale=sale, product=self.slow_mover, quantity=1, unit_price="10.00")

    def test_ranks_by_quantity_sold_descending(self):
        response = self.client.get(reverse('dashboard-top-products'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['product_id'], self.best_seller.id)
        self.assertEqual(response.data[0]['total_quantity_sold'], 10)
        self.assertEqual(response.data[1]['product_id'], self.slow_mover.id)

    def test_limit_query_param_caps_results(self):
        response = self.client.get(reverse('dashboard-top-products'), {'limit': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_invalid_limit_returns_400(self):
        response = self.client.get(reverse('dashboard-top-products'), {'limit': 'not-a-number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
