from rest_framework import serializers
from django.db import transaction
from inventory.models import Product
from stock.models import StockMovement, MOVEMENT_CHOICES
from .models import Purchase, PurchaseItem

class PurchaseItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_price']

class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'supplier', 'date', 'total_amount', 'items']
        read_only_fields = ['total_amount']

class PurchaseCreateSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = ['supplier', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        if not items_data:
            raise serializers.ValidationError("A purchase must have at least one item.")
        
        with transaction.atomic():
            purchase = Purchase.objects.create(**validated_data)
            
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                
                PurchaseItem.objects.create(purchase=purchase, **item_data)
                
                product.quantity_in_stock += quantity
                product.save()
                
                StockMovement.objects.create(
                    product=product,
                    movement_type=MOVEMENT_CHOICES[0][0], # 'IN'
                    quantity=quantity,
                    related_purchase=purchase
                )
        return purchase