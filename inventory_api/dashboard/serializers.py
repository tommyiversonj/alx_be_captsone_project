from rest_framework import serializers


class TotalSalesSerializer(serializers.Serializer):
    total_sales_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)


class TopProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    total_quantity_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
