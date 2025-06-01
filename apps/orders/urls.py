from django.urls import path
from .views import (
    OrderStatusListView,
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    BuyerOrderActiveListView,
    BuyerOrderCompletedListView,
    SellerOrderActiveListView,
    SellerOrderCompletedListView,
    MarkOrderCompletedView,
)

urlpatterns = [
    path('statuses/', OrderStatusListView.as_view(), name='order-status-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('all/', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('my-orders/active/', BuyerOrderActiveListView.as_view(), name='buyer-order-list-active'),
    path('my-orders/completed/', BuyerOrderCompletedListView.as_view(), name='buyer-order-list-completed'),
    path('seller-orders/active/', SellerOrderActiveListView.as_view(), name='seller-order-list-active'),
    path('seller-orders/completed/', SellerOrderCompletedListView.as_view(), name='seller-order-list-completed'),
    path('<int:pk>/complete/', MarkOrderCompletedView.as_view(), name='order-complete'),
]