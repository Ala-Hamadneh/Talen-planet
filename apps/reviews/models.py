from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from apps.marketplace.models import Gigs
from apps.orders.models import Order

class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    gig = models.ForeignKey(Gigs, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')

    rating = models.PositiveSmallIntegerField()  # 1 to 5
    comment = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)  # for admin moderation

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        unique_together = ('order', 'reviewer')  # Prevent multiple reviews per order

    def __str__(self):
        return f"Review by {self.reviewer} for {self.gig} - {self.rating} stars"
