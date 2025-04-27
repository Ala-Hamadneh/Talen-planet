from rest_framework import serializers
from .models import User, UserRoles
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import models

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoles
        fields = ['role_id', 'role_name']

class UserSerializer(serializers.ModelSerializer):
    role = UserRolesSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'role', 'role_id', 'profile_picture', 
            'bio', 'created_at', 'updated_at',
            'is_staff', 'is_superuser'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def validate_role_id(self, value):
        if value == 1 and not self.context['request'].user.is_superuser:
            raise ValidationError("Only admins can create admin accounts")
        return value

    def create(self, validated_data):
        # Ensure role_id is either 2 (Buyer) or 3 (Seller)
        role_id = validated_data.pop('role_id', None)
        if role_id == 1 and not self.context['request'].user.is_superuser:
            role_id = 2  # Default to Buyer
        
        user = User.objects.create_user(
            **validated_data,
            role_id=role_id or 2,  # Default to Buyer if not specified
            is_active=True
        )
        return user

    def update(self, instance, validated_data):
        # Remove password if accidentally included
        validated_data.pop('password', None)
        return super().update(instance, validated_data)

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_admin'] = user.is_superuser
        return token