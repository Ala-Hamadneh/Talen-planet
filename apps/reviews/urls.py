from django.urls import path
from .views import CreateReviewView, GigReviewListView, SellerReviewListView

urlpatterns = [
    path('create/<int:order_id>/', CreateReviewView.as_view(), name='create-review'),
    path('gig/<int:gig_id>/', GigReviewListView.as_view(), name='gig-reviews'),
    path('seller/<int:seller_id>/', SellerReviewListView.as_view(), name='seller-reviews'),
]
