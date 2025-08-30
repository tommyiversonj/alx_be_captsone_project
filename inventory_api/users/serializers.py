from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    
    # Serializer for managing user accounts by an admin.
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
        read_only_fields = ['is_staff', 'is_superuser']
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    
# Serializer for new user registration.
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class AuthTokenSerializer(serializers.Serializer):
    
# Serializer for user login and token generation.
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)