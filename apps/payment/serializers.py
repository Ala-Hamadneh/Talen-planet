from rest_framework import serializers
from apps.orders.models import Order

class PayoutApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'seller_payout', 'payout_sent']
        read_only_fields = ['id', 'seller_payout']

    def update(self, instance, validated_data):
        instance.payout_sent = True
        instance.save()
        return instance
