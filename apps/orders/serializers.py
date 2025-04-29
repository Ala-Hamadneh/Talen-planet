from rest_framework import serializers
from .models import Order, OrderStatus
from apps.marketplace.serializers import GigSerializer

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'description']

class OrderSerializer(serializers.ModelSerializer):
    gig_details = GigSerializer(source='gig', read_only=True)
    status_details = OrderStatusSerializer(source='status', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='gig.seller.username', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'gig', 'status', 'requirements',
            'created_at', 'updated_at', 'delivery_date', 'is_active',
            'gig_details', 'status_details', 'buyer_username', 'seller_username'
        ]
        read_only_fields = ['buyer', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['gig', 'requirements']
    
    def validate(self, data):
        # Prevent users from ordering their own gigs
        if self.context['request'].user == data['gig'].seller:
            raise serializers.ValidationError("You cannot order your own gig.")
        return data

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'requirements', 'delivery_date']