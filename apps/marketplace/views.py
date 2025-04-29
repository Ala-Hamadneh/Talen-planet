from rest_framework import generics, permissions 
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from .models import Categories, Services, Gigs
from .serializers import (
    CategorySerializer, 
    ServiceSerializer,
    GigSerializer,
    GigCreateSerializer
)

# Create your views here.

class CategoryListView(generics.ListAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ServiceListView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Services.objects.filter(category_id=category_id)

class GigListView(generics.ListAPIView):
    serializer_class = GigSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        service_id = self.kwargs['service_id']
        return Gigs.objects.filter(service_id=service_id, is_active=True)

class GigCreateView(generics.CreateAPIView):
    queryset = Gigs.objects.all()
    serializer_class = GigCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class GigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Gigs.objects.all()
    serializer_class = GigSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_update(self, serializer):
        # Ensure only the owner can update
        if serializer.instance.seller == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied("You don't have permission to edit this gig.")
    
    def perform_destroy(self, instance):
        # Soft delete instead of actual deletion
        if instance.seller == self.request.user:
            instance.is_active = False
            instance.save()
        else:
            raise PermissionDenied("You don't have permission to delete this gig.")
        
class MyGigsListView(generics.ListAPIView):
    serializer_class = GigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return only the authenticated seller's active gigs
        return Gigs.objects.filter(
            seller=self.request.user,
            is_active=True
        ).select_related('service', 'seller')
    

class MyFilteredGigsListView(generics.ListAPIView):
    serializer_class = GigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Returns seller's gigs filtered by service ID"""
        service_id = self.kwargs.get('service_id')  # From URL
        
        return Gigs.objects.filter(
            seller=self.request.user,
            service_id=service_id,
            is_active=True
        ).select_related('service', 'seller')


class AdminGigListView(generics.ListAPIView):
    """
    Admin-only view to list ALL gigs (including inactive ones)
    """
    serializer_class = GigSerializer
    permission_classes = [IsAdminUser]  # Only accessible by admin users
    queryset = Gigs.objects.all().select_related('seller', 'service').order_by('id')

    def get_serializer_context(self):
        """Adds extra context for the serializer"""
        return {
            'show_admin_fields': True,  # Flag to show sensitive fields to admin
            'request': self.request
        }