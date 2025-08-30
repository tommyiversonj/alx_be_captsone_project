from rest_framework import serializers
from .models import StockMovement

class StockMovementSerializer(serializers.ModelSerializer):
    
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = StockMovement
        fields = [
            'id', 
            'product', 
            'product_name', 
            'movement_type', 
            'quantity', 
            'related_purchase', 
            'related_sale', 
            'timestamp'
        ]
        read_only_fields = [
            'movement_type', 
            'quantity', 
            'related_purchase', 
            'related_sale'
        ]