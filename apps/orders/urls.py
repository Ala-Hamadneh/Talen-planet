from django.urls import path
from .views import (
    OrderStatusListView,
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    BuyerOrderListView,
    SellerOrderListView,
    MarkOrderCompletedView,
)

urlpatterns = [
    path('statuses/', OrderStatusListView.as_view(), name='order-status-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('all/', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('my-orders/', BuyerOrderListView.as_view(), name='buyer-order-list'),
    path('seller-orders/', SellerOrderListView.as_view(), name='seller-order-list'),
    path('<int:pk>/complete/', MarkOrderCompletedView.as_view(), name='order-complete'),
]