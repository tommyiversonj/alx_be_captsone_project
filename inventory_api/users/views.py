from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework.authtoken.views import ObtainAuthToken

from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, AuthTokenSerializer

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):

# A ViewSet for managing user accounts by administrators.
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

# --- Function-based authentication views ---

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    
    # Registers a new user account.
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key, "message": "User registered successfully."},
                status=status.HTTP_201_CREATED
            )
        except IntegrityError:
            return Response(
                {"detail": "A user with that username or email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    
    # Authenticates a user and returns a token.
    serializer = AuthTokenSerializer(data=request.data)
    if serializer.is_valid():
            user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
            if user:
                token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    # Logs a user out by deleting their authentication token.
    try:
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    except AttributeError:
        return Response({"detail": "No token found for this user."}, status=status.HTTP_400_BAD_REQUEST)
    
class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
        'token': token.key,
        'user_id': user.pk,
        'email': user.email
})