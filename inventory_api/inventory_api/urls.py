"""
URL configuration for inventory_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'inventory': f"{settings.API_BASE_URL}inventory/",
        'users': f"{settings.API_BASE_URL}users/",
        'purchases': f"{settings.API_BASE_URL}purchases/",
        'stock': f"{settings.API_BASE_URL}stock/",
        'sales': f"{settings.API_BASE_URL}sales/",
        'schema': f"{settings.API_BASE_URL}schema/",
        'swagger-ui': f"{settings.API_BASE_URL}swagger-ui/",
    })

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/inventory/', include('inventory.urls')), 
    path('api/users/', include('users.urls')),
    path('api/purchases/', include('purchases.urls')),
    path('api/stock/', include('stock.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/register/', include('users.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
