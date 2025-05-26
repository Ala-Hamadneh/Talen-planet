from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserListView,
    UserDetailView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
    RequestEmailVerificationView,
    ConfirmEmailVerificationView,
    AdminDashboardStatsView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path("request-verification/", RequestEmailVerificationView.as_view(), name="request-verification"),
    path("confirm-verification/", ConfirmEmailVerificationView.as_view(), name="confirm-verification"),
    path('admin/dashboard-stats/', AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),

]