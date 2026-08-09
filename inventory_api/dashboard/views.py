from django.db.models import F, Sum
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from inventory.models import Product
from inventory.serializers import ProductSerializer
from sales.models import Sale, SaleItem

from .serializers import TopProductSerializer, TotalSalesSerializer


@extend_schema(
    responses=ProductSerializer(many=True),
    description="Lists all products whose current stock is at or below their low_stock_threshold.",
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def low_stock(request):
    products = Product.objects.select_related('category').filter(
        quantity_in_stock__lte=F('low_stock_threshold')
    ).order_by('quantity_in_stock')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter('start_date', OpenApiTypes.DATE, description="Inclusive start date (YYYY-MM-DD)."),
        OpenApiParameter('end_date', OpenApiTypes.DATE, description="Inclusive end date (YYYY-MM-DD)."),
    ],
    responses=TotalSalesSerializer,
    description="Total number of sales and total revenue, optionally filtered by date range.",
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def total_sales(request):
    sales = Sale.objects.all()
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    if start_date:
        sales = sales.filter(date__date__gte=start_date)
    if end_date:
        sales = sales.filter(date__date__lte=end_date)

    totals = SaleItem.objects.filter(sale__in=sales).aggregate(
        total_revenue=Sum(F('quantity') * F('unit_price'))
    )
    data = {
        "total_sales_count": sales.count(),
        "total_revenue": totals["total_revenue"] or 0,
    }
    serializer = TotalSalesSerializer(data)
    return Response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter('limit', OpenApiTypes.INT, description="Max number of products to return (default 5, max 50)."),
    ],
    responses=TopProductSerializer(many=True),
    description="Top products ranked by total quantity sold across all sales.",
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def top_products(request):
    try:
        limit = int(request.query_params.get('limit', 5))
    except (TypeError, ValueError):
        return Response({"detail": "limit must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
    limit = max(1, min(limit, 50))

    rows = (
        SaleItem.objects.values('product_id', 'product__name')
        .annotate(
            total_quantity_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price')),
        )
        .order_by('-total_quantity_sold')[:limit]
    )
    data = [
        {
            "product_id": row["product_id"],
            "product_name": row["product__name"],
            "total_quantity_sold": row["total_quantity_sold"],
            "total_revenue": row["total_revenue"],
        }
        for row in rows
    ]
    serializer = TopProductSerializer(data, many=True)
    return Response(serializer.data)
