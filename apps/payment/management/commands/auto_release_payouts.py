from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.orders.models import Order, OrderStatus

class Command(BaseCommand):
    help = "Auto-completes delivered orders older than 5 days and releases payout"

    def handle(self, *args, **kwargs):
        five_days_ago = timezone.now() - timedelta(days=5)
        delivered_status = OrderStatus.objects.get(name="Delivered")
        completed_status = OrderStatus.objects.get(name="Completed")

        orders = Order.objects.filter(
            status=delivered_status,
            delivery_date__lte=five_days_ago,
            is_active=True,
            is_paid=True,
            payout_sent=False
        ).select_related('gig')

        for order in orders:
            gig_price = order.gig.price

            lahza_fee = gig_price * Decimal('0.025')
            after_lahza = gig_price - lahza_fee

            platform_fee = after_lahza * Decimal('0.075')
            seller_payout = after_lahza - platform_fee

            order.status = completed_status
            order.platform_fee = round(platform_fee, 2)
            order.seller_payout = round(seller_payout, 2)
            order.payout_sent = False
            order.save()

            self.stdout.write(self.style.SUCCESS(
                f"Auto-completed order #{order.id}. Payout: {seller_payout}"
            ))
