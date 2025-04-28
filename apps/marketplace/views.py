from rest_framework import generics, permissions 
from rest_framework.exceptions import PermissionDenied
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