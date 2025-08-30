from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Sale
from .serializers import SaleSerializer, SaleCreateSerializer

# Create your views here.
class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.prefetch_related('items').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return SaleCreateSerializer
        return SaleSerializer
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Sale created successfully.", "id": serializer.data['id']},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
