from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from .models import Categories, Services, Gigs

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'name']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['id', 'name', 'category']

class GigSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='seller.username', read_only=True)
    email = serializers.CharField(source='seller.email', read_only=True)
    is_active = serializers.BooleanField(read_only=True)  # Only shown to admin
    
    class Meta:
        model = Gigs
        fields = ['id', 'title', 'description', 'price', 
                 'delivery_time', 'created_at', 'service', 
                 'username', 'email', 'is_active']  # Added is_active

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show sensitive fields only to admin
        if not self.context.get('show_admin_fields', False):
            self.fields.pop('is_active', None)

class GigCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gigs
        fields = ['title', 'description', 'price', 
                 'delivery_time', 'service']