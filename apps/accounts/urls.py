from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserListView,
    UserDetailView,
    LogoutView,
    PasswordChangeView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    # path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    # path('reset-password-confirm/<uidb64>/<token>/', 
    #      PasswordResetConfirmView.as_view(), 
    #      name='reset-password-confirm'),
]