import requests
from django.conf import settings
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.orders.models import Order, OrderStatus
from apps.marketplace.models import Gigs
from .models import LahzaTransaction, WithdrawalRequest
from rest_framework import generics, permissions
from .serializers import PayoutApprovalSerializer, WithdrawalRequestSerializer, WithdrawalRequestStatusSerializer
from apps.communications.notification.utils import notify_user
from rest_framework.permissions import AllowAny


from decimal import Decimal
from django.db.models import Sum
# Create your views here.
from django.contrib.auth import get_user_model
User = get_user_model()  


class InitPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, buyer=request.user)

            if order.is_paid:
                return Response({"detail": "Order already paid."}, status=400)

            payload = {
                "amount": str(int(order.gig.price * 100)),  
                "currency": "ILS",
                "email": request.user.email,
                "callback_url": "http://192.168.56.1:8080/orders",
                "webhook_url": "https://292c-103-206-108-122.ngrok-free.app/api/payment/webhook/"
            }

            headers = {
                "Authorization": f"Bearer {settings.LAHZA_SECRET_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                f"{settings.LAHZA_API_URL}/transaction/initialize",
                json=payload,
                headers=headers
            )


            if response.status_code == 200:
                data = response.json()
                order.lahza_transaction_id = data['data']['reference']
                order.save()

                LahzaTransaction.objects.create(
                    order=order,
                    user=request.user,
                    transaction_type='payment',
                    transaction_id=data['data']['reference'],
                    amount=order.gig.price,
                    status='pending'
                )

                return Response({
                    "checkout_url": data["data"]["authorization_url"],
                    "transaction_id": data['data']['reference']
                    }
                    )
            else:
                print("Lahza raw response:", response.text)
                return Response({"error": "Lahza error", "raw": response.text}, status=response.status_code)

        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=404)
    


class LahzaWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data.get('data', {})
        tx_id = payload.get('reference')  
        status = payload.get('status')

        try:
            transaction = LahzaTransaction.objects.get(transaction_id=tx_id)
            transaction.status = status
            transaction.save()

            if status == 'success':
                order = transaction.order
                order.is_paid = True
                order.save()
        except LahzaTransaction.DoesNotExist:
            pass

        return Response({"detail": "Webhook processed."})
    
class SellerEarningsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        seller = request.user

        completed_status = OrderStatus.objects.get(name="Completed")

        orders = Order.objects.filter(
            gig__seller=seller,
            status=completed_status,
            payout_sent=False
        )

        total_earned = orders.aggregate(total=Sum('seller_payout'))['total'] or 0

        return Response({
            "seller": seller.username,
            "total_earned": round(total_earned, 2),
        })
    
class RequestWithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        seller = request.user
        data = request.data

        # Get fields from request
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        middle_name = data.get('middle_name')
        iban = data.get('iban')
        amount = data.get('amount')

        # Validate required fields
        if not first_name or not last_name or not iban or not amount:
            return Response({
                "error": "first_name, last_name, IBAN, and amount are required."
            }, status=400)

        try:
            amount = Decimal(amount)
        except:
            return Response({"error": "Invalid amount."}, status=400)

        # Get statuses
        status_in_progress = OrderStatus.objects.get(name="In Progress").id
        status_delivered = OrderStatus.objects.get(name="Delivered").id
        status_completed = OrderStatus.objects.get(name="Completed").id

        valid_statuses = [status_in_progress, status_delivered, status_completed]

        # Get seller gigs
        seller_gigs = Gigs.objects.filter(seller=seller)

        # Get orders for seller gigs
        orders = Order.objects.filter(gig__in=seller_gigs, status__in=valid_statuses).select_related('gig')

        # Compute available balance (same logic as SellerEarningsView)
        available_balance = sum(
            order.gig.price for order in orders
            if order.status_id == status_completed and order.is_paid and not order.payout_sent
        )

        if amount > available_balance:
            return Response({"error": "Insufficient balance."}, status=400)

        # Create withdrawal request
        WithdrawalRequest.objects.create(
            seller=seller,
            amount=amount,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            iban=iban
        )

        # Notify admins
        admins = User.objects.filter(is_staff=True, is_active=True)
        for admin in admins:
            notify_user(
                user=admin,
                title="New Withdrawal Request",
                body=f"{seller.username} requested {amount} ILS withdrawal.",
                notification_type="system"
            )

        return Response({"message": "Withdrawal request submitted."}, status=200)
class AdminPayoutApprovalListView(generics.ListAPIView):
    serializer_class = PayoutApprovalSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        completed_status = OrderStatus.objects.get(name="Completed")
        return Order.objects.filter(status=completed_status, payout_sent=False)


class AdminPayoutApproveView(generics.UpdateAPIView):
    serializer_class = PayoutApprovalSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()

    def perform_update(self, serializer):
        instance = self.get_object()
        instance.payout_sent = True
        instance.save()
class AdminWithdrawlRequest(generics.ListAPIView):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = WithdrawalRequest.objects.all()

class WithdrawalRequestStatusUpdateView(generics.UpdateAPIView):
    queryset = WithdrawalRequest.objects.all()
    serializer_class = WithdrawalRequestStatusSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        serializer.save(is_processed=serializer.validated_data.get('is_processed', False))