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

class UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoles
        fields = ['role_id', 'role_name']

class UserSerializer(serializers.ModelSerializer):
    role = UserRolesSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'role', 'role_id', 'profile_picture',
            'bio', 'created_at', 'updated_at',
            'is_staff', 'is_superuser', 'password'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        role_id = validated_data.pop('role_id')

        # Prevent any attempt to create an admin account
        validated_data['is_staff'] = False
        validated_data['is_superuser'] = False

        # Only allow roles Buyer or Seller
        try:
            role = UserRoles.objects.get(pk=role_id)
            if role.role_name.lower() not in ['buyer', 'seller']:
                raise serializers.ValidationError({'role_id': 'Only Buyer or Seller roles are allowed.'})
        except UserRoles.DoesNotExist:
            raise serializers.ValidationError({'role_id': 'Invalid role ID.'})

        user = User(**validated_data)
        user.role = role

        if password:
            user.set_password(password)
        else:
            raise serializers.ValidationError({'password': 'Password is required.'})

        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        validated_data.pop('role_id', None)
        validated_data.pop('is_superuser', None)
        validated_data.pop('is_staff', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation

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