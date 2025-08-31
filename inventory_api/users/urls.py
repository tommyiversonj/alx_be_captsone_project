# apps/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .views import CustomAuthToken

from .views import UserViewSet, register_user, login_user, logout_user

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='logout'),
    path('login/', CustomAuthToken.as_view(), name='user-login'),
]