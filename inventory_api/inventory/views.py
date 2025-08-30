from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError, models

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

# Custom permission 
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_staff

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly] 
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly] 

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price', 'quantity_in_stock', 'low_stock_threshold']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'quantity_in_stock', 'created_at']

    def get_queryset(self):
        
        # Optionally restricts the returned products to those that have low stock.
        # Usage: /products/?low_stock=true
        
        queryset = super().get_queryset()
        low_stock_filter = self.request.query_params.get('low_stock', None)
        if low_stock_filter and low_stock_filter.lower() == 'true':
            return queryset.filter(quantity_in_stock__lte=models.F('low_stock_threshold'))
        return queryset
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(
                status==status.HTTP_400_BAD_REQUEST
            )
            
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )
            return super().destroy(request, *args, **kwargs)