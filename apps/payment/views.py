import requests
from django.conf import settings
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.orders.models import Order, OrderStatus
from .models import LahzaTransaction, WithdrawalRequest



from decimal import Decimal
from django.db.models import Sum
# Create your views here.


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
                "callback_url": "https://e53c-82-213-45-162.ngrok-free.app/payment-success/",
                "webhook_url": "https://e53c-82-213-45-162.ngrok-free.app/api/payment/webhook/"
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
    def post(self, request):
        data = request.data
        tx_id = data.get('transaction_id')
        status = data.get('status')

        try:
            transaction = LahzaTransaction.objects.get(transaction_id=tx_id)
            transaction.status = status
            transaction.save()

            if status == 'success':
                order = transaction.order
                order.is_paid = True
                order.save()

        except LahzaTransaction.DoesNotExist:
            pass  # optionally log error

        return Response({"detail": "Webhook processed."})
    
class SellerEarningsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        seller = request.user

        completed_status = OrderStatus.objects.get(name="Completed")

        orders = Order.objects.filter(
            gig__seller=seller,
            status=completed_status,
            payout_sent=True
        )

        total_earned = orders.aggregate(total=Sum('seller_payout'))['total'] or 0

        return Response({
            "seller": seller.username,
            "total_earned": round(total_earned, 2),
        })
    
class RequestWithdrawalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        seller = request.user
        amount = request.data.get('amount')

        if not amount:
            return Response({"error": "Amount required."}, status=400)

        amount = Decimal(amount)

        completed_status = OrderStatus.objects.get(name="Completed")
        total_earned = Order.objects.filter(
            gig__seller=seller,
            status=completed_status,
            payout_sent=True
        ).aggregate(total=Sum('seller_payout'))['total'] or 0

        total_withdrawn = WithdrawalRequest.objects.filter(
            seller=seller,
            is_processed=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        available_balance = total_earned - (total_withdrawn or 0)

        if amount > available_balance:
            return Response({"error": "Insufficient balance."}, status=400)

        WithdrawalRequest.objects.create(seller=seller, amount=amount)
        return Response({"message": "Withdrawal request submitted."})

