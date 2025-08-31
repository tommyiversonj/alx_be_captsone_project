from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from inventory.models import Product, Category
from inventory.serializers import ProductSerializer, ProductUpdateSerializer
from users.models import User

# Create your tests here.
class ProductSerializerTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_valid_product_serializer(self):
        data = {
            "name": "Test Item",
            "category_id": self.category.id,
            "price": "10.00",
            "quantity_in_stock": 50,
            "low_stock_threshold": 10,
            "description": "A new test item."
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), "Serializer should be valid with correct data.")
        self.assertEqual(serializer.validated_data['name'], 'Test Item')
    
    def test_invalid_product_serializer(self):
        data = {
            "category": self.category.id,
            "price": "10.00",
            "quantity_in_stock": 50,
        }
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid(), "Serializer should be invalid with missing 'name' field.")
        self.assertIn('name', serializer.errors)

class ProductUpdateSerializerTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Old Name",
            category=self.category,
            price=10.00,
            quantity_in_stock=50,
            low_stock_threshold=10,
            description="Old Description"
        )
    
    def test_partial_update_valid_data(self):
        data = {"price": 15.00, "name": "New Name"}
        serializer = ProductUpdateSerializer(self.product, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), "Serializer should be valid for a partial update.")
        updated_product = serializer.save()
        
        self.assertEqual(updated_product.price, 15.00)
        self.assertEqual(updated_product.name, "New Name")
        self.assertEqual(updated_product.quantity_in_stock, 50) 
        self.assertEqual(updated_product.description, "Old Description")

class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='password', is_staff=True)
        self.regular_user = User.objects.create_user(username='user', password='password')
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Product A", category=self.category, price=10)
        self.list_url = reverse('product-list')

    def test_list_products(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "New Product",
            "category_id": self.category.id,
            "price": 25.00,
            "quantity_in_stock": 20,
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "name": "Forbidden Product",
            "category_id": self.category.id,
            "price": 25.00,
            "quantity_in_stock": 20,
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)
