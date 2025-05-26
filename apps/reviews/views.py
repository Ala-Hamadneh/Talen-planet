from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import Review
from .serializers import ReviewSerializer
from apps.orders.models import Order

class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        try:
            order = Order.objects.get(id=order_id, buyer=self.request.user, status__name="Completed")
        except Order.DoesNotExist:
            raise ValidationError("Order not found or not completed.")

        if hasattr(order, 'review'):
            raise ValidationError("This order has already been reviewed.")

        serializer.save(
            reviewer=self.request.user,
            seller=order.gig.seller,  
            gig=order.gig,
            order=order
        )

class GigReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        gig_id = self.kwargs.get('gig_id')
        return Review.objects.filter(gig_id=gig_id, is_active=True).order_by('-created_at')

class SellerReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        seller_id = self.kwargs.get('seller_id')
        return Review.objects.filter(seller_id=seller_id, is_active=True).order_by('-created_at')