from rest_framework import serializers
from apps.orders.models import Order
from .models import WithdrawalRequest

class PayoutApprovalSerializer(serializers.ModelSerializer):
    seller_id =serializers.CharField(source='gig.seller.id', read_only=True)
    class Meta:
        model = Order
        fields = ['id','seller_id' , 'seller_payout', 'payout_sent']
        read_only_fields = ['id', 'seller_payout']

class WithdrawalRequestSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = WithdrawalRequest
        fields = [
            'id', 'amount', 'is_processed',
            'full_name', 'iban', 'created_at', 'seller']
        read_only_fields = ['id', 'amount']

    def get_full_name(self, obj):
        """Combine first, middle, and last name into full_name"""
        parts = []
        if obj.first_name:
            parts.append(obj.first_name)
        if obj.middle_name:
            parts.append(obj.middle_name)
        if obj.last_name:
            parts.append(obj.last_name)
        return ' '.join(parts) if parts else None  


class WithdrawalRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['id', 'is_processed']
        read_only_fields = ['id']