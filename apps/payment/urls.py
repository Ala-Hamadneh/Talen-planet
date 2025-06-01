# payments/urls.py

from django.urls import path
from .views import (
    InitPaymentView,
    LahzaWebhookView,
    SellerEarningsView,
    RequestWithdrawalView,
    AdminPayoutApprovalListView,
    AdminPayoutApproveView,
    AdminWithdrawlRequest,
    WithdrawalRequestStatusUpdateView,
    )

urlpatterns = [
    path('initiate/<int:order_id>/', InitPaymentView.as_view()),
    path('webhook/', LahzaWebhookView.as_view()),
    path('my-earnings/', SellerEarningsView.as_view(), name='seller-earnings'),
    path('withdraw/', RequestWithdrawalView.as_view(), name='request-withdrawal'),
    path('admin/payouts/', AdminPayoutApprovalListView.as_view(), name='admin-payouts-list'),
    path('admin/payouts/<int:pk>/approve/', AdminPayoutApproveView.as_view(), name='admin-payout-approve'),
    path('admin/withdrawals/',AdminWithdrawlRequest.as_view(),name='admin-withdrawal-list'),
    path('admin/withdrawals/<int:id>/status/', WithdrawalRequestStatusUpdateView.as_view(), name='withdrawal-status-update'),
]
