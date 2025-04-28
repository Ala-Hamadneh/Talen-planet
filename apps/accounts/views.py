from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import PermissionDenied
from .models import User
from .serializers import (
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    UserRolesSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,

)

# Email 

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.encoding import force_bytes
from django.urls import reverse


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
            raise PermissionDenied(
                {'detail': 'You are not allowed to view other users details'},
            )
        return user

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

# class PasswordResetView(generics.GenericAPIView):
#     serializer_class = PasswordResetSerializer
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         email = serializer.data['email']
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"status": "If this email exists, we've sent a reset link"})
            
#         # Generate token
#         token = default_token_generator.make_token(user)
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
        
#         # Build reset URL
#         reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
#         # Send email (configure your email backend in settings.py)
#         send_mail(
#             "Password Reset",
#             f"Click to reset your password: {reset_url}",
#             settings.DEFAULT_FROM_EMAIL,
#             [email],
#             fail_silently=False,
#         )
        
#         return Response({"status": "If this email exists, we've sent a reset link"})


# class PasswordResetConfirmView(generics.GenericAPIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             user = None
        
#         if user and default_token_generator.check_token(user, token):
#             new_password = request.data.get('new_password')
#             if new_password:
#                 user.set_password(new_password)
#                 user.save()
#                 return Response({"status": "Password reset successful"})
#             return Response(
#                 {"new_password": "This field is required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         return Response(
#             {"token": "Invalid token"},
#             status=status.HTTP_400_BAD_REQUEST
#         )