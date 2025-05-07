from django.db import models
from django.conf import settings
from apps.marketplace.models import Gigs

class OrderStatus(models.Model):
    """Tracks possible order statuses (In Progress, Delivered, Completed, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Order Statuses"
        db_table = "order_statuses"
    
    def __str__(self):
        return self.name

class Order(models.Model):
    """Main order model connecting buyers, sellers and gigs"""
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_as_buyer'
    )
    gig = models.ForeignKey(
        Gigs,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    requirements = models.TextField(help_text="Buyer's specific requirements")
    delivery_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # Payment-related fields
    is_paid = models.BooleanField(default=False)  # updated by webhook
    lahza_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    seller_payout = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payout_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.gig.title}"

