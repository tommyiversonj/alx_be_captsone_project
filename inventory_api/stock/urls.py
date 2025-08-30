from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockMovementViewSet

router = DefaultRouter()
router.register(r'stock-movements', StockMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]