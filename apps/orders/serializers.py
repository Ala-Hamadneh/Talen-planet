from rest_framework import serializers
from .models import Order, OrderStatus
from apps.marketplace.serializers import GigSerializer
from apps.reviews.models import Review


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'description']

class OrderSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(source='status.name', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    buyer_id = serializers.CharField(source='buyer.id', read_only=True)
    seller_username = serializers.CharField(source='gig.seller.username', read_only=True)
    seller_id = serializers.CharField(source='gig.seller.id', read_only=True)
    gig_title = serializers.CharField(source='gig.title', read_only=True)
    gig_description = serializers.CharField(source='gig.description', read_only=True)
    gig_price = serializers.CharField(source='gig.price', read_only=True)
    delivery_time = serializers.CharField(source='gig.delivery_time', read_only=True)
    profile_picture = serializers.ImageField(source='gig.seller.profile_picture', read_only=True)

    has_review = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'buyer_username', 'buyer_id', 'seller_username', 'seller_id', 'profile_picture',
            'gig', 'gig_title', 'gig_description', 'gig_price', 'delivery_time',
            'order_status', 'requirements',
            'created_at', 'updated_at', 'delivery_date', 'is_active',
            'is_paid', 'lahza_transaction_id',
            'platform_fee', 'seller_payout', 'payout_sent',

            'has_review', 'rating', 'comment',
        ]
        read_only_fields = [
            'buyer', 'created_at', 'updated_at',
            'is_paid', 'lahza_transaction_id',
            'platform_fee', 'seller_payout', 'payout_sent'
        ]

    def get_has_review(self, obj):
        return hasattr(obj, 'review')

    def get_rating(self, obj):
        return obj.review.rating if hasattr(obj, 'review') else None

    def get_comment(self, obj):
        return obj.review.comment if hasattr(obj, 'review') else None

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'gig', 'requirements']

    def validate(self, data):
        # Prevent users from ordering their own gigs
        if self.context['request'].user == data['gig'].seller:
            raise serializers.ValidationError("You cannot order your own gig.")
        return data

    def create(self, validated_data):
        return Order.objects.create(**validated_data)

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'requirements', 'delivery_date']
