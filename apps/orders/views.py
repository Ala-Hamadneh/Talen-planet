from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.accounts import models
from .models import Order, OrderStatus
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderStatusSerializer
)

# Create your views here.

class OrderStatusListView(generics.ListAPIView):
    """Public endpoint to list all order statuses"""
    queryset = OrderStatus.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [permissions.AllowAny]

class OrderCreateView(generics.CreateAPIView):
    """Endpoint for buyers to create new orders"""
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Set initial status to "In Progress" or whatever your first status is
        in_progress_status = OrderStatus.objects.get(name='In Progress')
        serializer.save(
            buyer=self.request.user,
            status=in_progress_status
        )

class OrderListView(generics.ListAPIView):
    """Endpoint to list all orders (with filters)"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.filter(
            is_active=True
        ).select_related('gig', 'status', 'buyer', 'gig__seller')
    
    
 

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint for order details and updates"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderUpdateSerializer
        return OrderSerializer
    
    def perform_update(self, serializer):
        order = self.get_object()
        user = self.request.user
        
        # Only allow updates by the seller or the buyer (with different permissions)
        if user == order.gig.seller:
            # Seller can update status and delivery date
            serializer.save()
        elif user == order.buyer:
            # Buyer can only update requirements
            if 'status' in serializer.validated_data or 'delivery_date' in serializer.validated_data:
                raise PermissionDenied("Buyers can only update requirements.")
            serializer.save()
        else:
            raise PermissionDenied("You don't have permission to update this order.")
    
    def perform_destroy(self, instance):
        # Soft delete
        if self.request.user == instance.buyer or self.request.user == instance.gig.seller:
            instance.is_active = False
            instance.save()
        else:
            raise PermissionDenied("You don't have permission to delete this order.")

class BuyerOrderListView(generics.ListAPIView):
    """Endpoint for a buyer to see all their orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            buyer=self.request.user,
            is_active=True
        ).select_related('gig', 'status', 'gig__seller')

class SellerOrderListView(generics.ListAPIView):
    """Endpoint for a seller to see all orders for their gigs"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            gig__seller=self.request.user,
            is_active=True
        ).select_related('gig', 'status', 'buyer')