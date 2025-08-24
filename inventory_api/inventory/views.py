from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated] 
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated] 

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


    filterset_fields = ['category', 'price', 'quantity_in_stock', 'low_stock_threshold']


    search_fields = ['name', 'description', 'sku']

    ordering_fields = ['name', 'price', 'quantity_in_stock', 'created_at']

    def get_queryset(self):
        """
        Optionally restricts the returned products to those that have low stock.
        Usage: /products/?low_stock=true
        """
        queryset = super().get_queryset()
        low_stock_filter = self.request.query_params.get('low_stock', None)
        if low_stock_filter and low_stock_filter.lower() == 'true':
            return queryset.filter(quantity_in_stock__lte=models.F('low_stock_threshold'))
        return queryset