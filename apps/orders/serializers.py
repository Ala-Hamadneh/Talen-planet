from rest_framework import serializers
from .models import Order, OrderStatus
from apps.marketplace.serializers import GigSerializer

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'description']

class OrderSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(source='status.name', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='gig.seller.username', read_only=True)
    gig_title = serializers.CharField(source = 'gig.title', read_only=True)
    gig_description = serializers.CharField(source = 'gig.description', read_only=True)
    gig_price = serializers.CharField(source = 'gig.price', read_only=True)


    class Meta:
        model = Order
        fields = [
            'id', 'buyer_username', 'seller_username',
            'gig', 'gig_title', 'gig_description', 'gig_price',
            'order_status', 'requirements',
            'created_at', 'updated_at', 'delivery_date', 'is_active',
              

            # Payment-related fields (read-only for frontend)
            'is_paid', 'lahza_transaction_id',
            'platform_fee', 'seller_payout', 'payout_sent',
        ]
        read_only_fields = [
            'buyer', 'created_at', 'updated_at',
            'is_paid', 'lahza_transaction_id',
            'platform_fee', 'seller_payout', 'payout_sent'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['gig', 'requirements']

    def validate(self, data):
        # Prevent users from ordering their own gigs
        if self.context['request'].user == data['gig'].seller:
            raise serializers.ValidationError("You cannot order your own gig.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        order = Order.objects.create(
            buyer=user,
            gig=validated_data['gig'],
            requirements=validated_data['requirements']
            # amount will be auto-set from gig in model.save()
        )
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'requirements', 'delivery_date']
