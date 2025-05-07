# payments/urls.py

from django.urls import path
from .views import (
    InitPaymentView,
    LahzaWebhookView,
    SellerEarningsView,
    RequestWithdrawalView
    )

urlpatterns = [
    path('initiate/<int:order_id>/', InitPaymentView.as_view()),
    path('webhook/', LahzaWebhookView.as_view()),
    path('my-earnings/', SellerEarningsView.as_view(), name='seller-earnings'),
    path('withdraw/', RequestWithdrawalView.as_view(), name='request-withdrawal'),
]
