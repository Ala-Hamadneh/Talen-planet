from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.views import APIView

from decimal import Decimal

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
        data = serializer.validated_data

        if user == order.gig.seller:
            if 'status' in data:
                status_id = data['status'].id
                allowed_status = 2
                if status_id != allowed_status:
                    raise PermissionDenied("Seller can only mark status as Delivered or Cancelled.")    
            serializer.save()

        elif user == order.buyer:
            if 'status' in data or 'delivery_date' in data:
                raise PermissionDenied("Buyers can only update requirements.")

            if 'requirements' in data and data['requirements'] != order.requirements:
                revision_status = OrderStatus.objects.get(id = 5)
                serializer.save(status=revision_status)
            else:
                serializer.save()

        else:
            raise PermissionDenied("You don't have permission to update this order.")
        
    def perform_destroy(self, instance):
        # Soft delete
        if self.request.user == instance.buyer or self.request.user == instance.gig.seller or self.request.user.id == 1:
            instance.is_active = False
            instance.status = OrderStatus.objects.get(id=4)
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
    

class MarkOrderCompletedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        completed_status = OrderStatus.objects.get(name="Completed")
        try:
            order = Order.objects.select_related('gig__seller').get(pk=pk, is_active=True)
        except Order.DoesNotExist:
            raise NotFound("Order not found.")

        if request.user != order.buyer:
            raise PermissionDenied("Only the buyer can complete this order.")

        if not order.is_paid:
            return Response({"detail": "Order is not paid yet."}, status=400)

        if order.status == completed_status:
            return Response({"detail": "Order already marked as completed."}, status=400)

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

        return Response({
            "detail": "Order marked as completed.",
            "lahza_fee": round(lahza_fee, 2),
            "platform_fee": order.platform_fee,
            "seller_payout": order.seller_payout
        }, status=200)