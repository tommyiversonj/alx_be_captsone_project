from django.urls import path

from . import views

urlpatterns = [
    path('low-stock/', views.low_stock, name='dashboard-low-stock'),
    path('total-sales/', views.total_sales, name='dashboard-total-sales'),
    path('top-products/', views.top_products, name='dashboard-top-products'),
]
