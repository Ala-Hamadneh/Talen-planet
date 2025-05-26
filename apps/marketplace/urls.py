from django.urls import path
from .views import (
    CategoryListView,
    ServiceListView,
    GigListView,
    GigCreateView,
    GigDetailView,
    MyGigsListView,
    MyFilteredGigsListView,
    AdminGigListView,
    TopRatedGigListView,
    AdminToggleGigStatusView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/services/', ServiceListView.as_view(), name='service-list'),
    path('services/<int:service_id>/gigs/', GigListView.as_view(), name='gig-list'),
    path('gigs/top-rated/', TopRatedGigListView.as_view(), name='top-rated-gigs'),
    path('gigs/create/', GigCreateView.as_view(), name='gig-create'),
    path('gigs/<int:pk>/', GigDetailView.as_view(), name='gig-detail'),
    path('my-gigs/', MyGigsListView.as_view(), name='my-gigs'),
    path('my-gigs/service/<int:service_id>/', MyFilteredGigsListView.as_view(), name='my-gigs-filtered'),
    path('admin/gigs/', AdminGigListView.as_view(), name='admin-gig-list'),
    path('admin/gigs/<int:pk>/toggle-status/', AdminToggleGigStatusView.as_view(), name='admin-toggle-gig-status'),
]