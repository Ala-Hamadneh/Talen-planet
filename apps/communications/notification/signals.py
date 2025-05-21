from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import Order
from .utils import notify_user

@receiver(post_save, sender=Order)
def new_order_notify(sender, instance, created, **kwargs):
    if created:
        notify_user(
            user=instance.gig.seller,
            title="New Order Received",
            body=f"Order #{instance.id} has been placed.",
            notification_type="order"
        )
