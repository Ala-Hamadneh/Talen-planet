from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db import models

from .models import User
from .serializers import (
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    EmailVerificationRequestSerializer,
    EmailVerificationConfirmSerializer,
    PasswordResetSerializer,
    PublicUserProfileSerializer
)

from apps.marketplace.models import Gigs  
from apps.orders.models import Order, OrderStatus  
from apps.payment.models import LahzaTransaction, WithdrawalRequest


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data['message'] = "Login successful"
        return response

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        user = super().get_object()
        if not (self.request.user.is_staff or self.request.user == user):
            if self.request.method=='GET':
                raise PermissionDenied(
                {'detail': 'You are not allowed to view other users details'},
            )
            elif self.request.method == 'PUT':
                raise PermissionDenied(
                {'detail': 'You are not allowed to edit other users details'},
            )
        return user
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Redundant check for safety
        if not (request.user.is_staff or request.user == instance):
            raise PermissionDenied({'detail': 'You are not allowed to edit other users details'})

        serializer = self.get_serializer(instance, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # In a real implementation, you'd add token to blacklist
        return Response({"detail": "Successfully logged out."}, 
                       status=status.HTTP_200_OK)
    

# Password change , forget(reset)

class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.data['old_password']):
            return Response(
                {"old_password": "Wrong password"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.set_password(serializer.data['new_password'])
        user.save()
        return Response({"status": "password changed"})


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]  

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request=request)
        return Response({"detail": "Password reset link sent."})

class RequestEmailVerificationView(generics.CreateAPIView):
    serializer_class = EmailVerificationRequestSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Verification code sent."}, status=201)


class ConfirmEmailVerificationView(generics.CreateAPIView):
    serializer_class = EmailVerificationConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({"message": "Email successfully verified."}, status=200)


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        print("USER:", request.user)
        print("IS AUTHENTICATED:", request.user.is_authenticated)
        print("IS STAFF:", request.user.is_staff)

        total_users = User.objects.count()
        active_gigs = Gigs.objects.filter(is_active=True).count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=models.Sum('platform_fee'))['total'] or 0

        total_received = LahzaTransaction.objects.aggregate(total=models.Sum('amount'))['total'] or 0
        total_withdrawn = WithdrawalRequest.objects.aggregate(total=models.Sum('amount'))['total'] or 0
        held_money = total_received - total_withdrawn

        return Response({
            'total_users': total_users,
            'active_gigs': active_gigs,
            'total_orders': total_orders,
            'revenue': total_revenue,
            'held_money': held_money,
        })




class PublicUserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = PublicUserProfileSerializer
    permission_classes = [permissions.AllowAny]  # 👈 public access
    lookup_field = 'id'  # or 'username' if you prefer


class SellerEarningsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        status_in_progress = OrderStatus.objects.get(name="In Progress").id
        status_delivered = OrderStatus.objects.get(name="Delivered").id
        status_completed = OrderStatus.objects.get(name="Completed").id
        valid_statuses = [status_in_progress, status_delivered, status_completed]

        seller_gigs = Gigs.objects.filter(seller=user)
        orders = Order.objects.filter(gig__in=seller_gigs, status__in=valid_statuses).select_related('gig')
        
        total_earnings = sum(order.gig.price for order in orders)

        held_money = sum(
            order.gig.price for order in orders
            if order.status_id in [status_in_progress, status_delivered] and order.is_paid 
        )

        available_money = sum(
            order.gig.price for order in orders
            if order.status_id == status_completed and order.is_paid and not order.payout_sent
        )

        return Response({
            "total_earnings": total_earnings,
            "held_money": held_money,
            "available_money": available_money,
        }, status=200)