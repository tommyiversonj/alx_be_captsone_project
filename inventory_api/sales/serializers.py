from collections import defaultdict

from rest_framework import serializers
from django.db import transaction, models
from inventory.models import Product
from stock.models import StockMovement, MOVEMENT_CHOICES
from .models import Sale, SaleItem

class SaleItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'date', 'customer_name', 'total_amount', 'items']
        read_only_fields = ['total_amount']

class SaleCreateSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ['id', 'customer_name', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')

        if not items_data:
            raise serializers.ValidationError("A sale must have at least one item.")

        quantities_by_product_id = defaultdict(int)
        for item_data in items_data:
            quantities_by_product_id[item_data['product'].pk] += item_data['quantity']

        with transaction.atomic():
            # Lock the involved product rows, in a stable (pk) order, so that
            # concurrent sales for the same product(s) are serialized instead
            # of both reading stale stock and both passing the check below.
            locked_products = {
                product.pk: product
                for product in Product.objects.select_for_update()
                    .filter(pk__in=quantities_by_product_id)
                    .order_by('pk')
            }

            for product_id, total_quantity in quantities_by_product_id.items():
                product = locked_products[product_id]
                if product.quantity_in_stock < total_quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for product '{product.name}'. "
                        f"Only {product.quantity_in_stock} available."
                    )

            sale = Sale.objects.create(**validated_data)

            for item_data in items_data:
                product = locked_products[item_data['product'].pk]
                quantity = item_data['quantity']

                SaleItem.objects.create(sale=sale, **item_data)

                product.quantity_in_stock = models.F('quantity_in_stock') - quantity
                product.save(update_fields=['quantity_in_stock'])

                StockMovement.objects.create(
                    product=product,
                    movement_type=MOVEMENT_CHOICES[1][0], # 'OUT'
                    quantity=quantity,
                    related_sale=sale
                )
        return sale
