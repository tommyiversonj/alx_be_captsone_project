from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import StockMovement
from .serializers import StockMovementSerializer

# Create your views here.
class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = StockMovement.objects.select_related('product').all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = ['product', 'movement_type']
    
    ordering_fields = ['timestamp', 'quantity']