from rest_framework import generics, permissions, status 
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from .models import Categories, Services, Gigs
from .serializers import (
    CategorySerializer, 
    ServiceSerializer,
    GigSerializer,
    GigCreateSerializer
)
from django.db.models import Avg
from rest_framework.response import Response

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
        queryset = Gigs.objects.filter(service_id=service_id, is_active=True)

        sort = self.request.query_params.get('sort')

        if sort == 'highest_rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif sort == 'lowest_price':
            queryset = queryset.order_by('price')
        elif sort == 'highest_price':
            queryset = queryset.order_by('-price')
        elif sort == 'most_recent':
            queryset = queryset.order_by('-created_at')

        return queryset

class GigCreateView(generics.CreateAPIView):
    queryset = Gigs.objects.all()
    serializer_class = GigCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        if self.request.user.id == 3:
             serializer.save(seller=self.request.user)
        else:
            raise PermissionDenied("Only Seller can post a gig.")

class GigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Gigs.objects.all()
    serializer_class = GigSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        if instance.seller != self.request.user:
            raise PermissionDenied("You don't have permission to edit this gig.")

        serializer = self.get_serializer(instance, data=request.data, context={'request': request}, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    
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
    
class AdminToggleGigStatusView(generics.UpdateAPIView):
    """
    Admin-only view to activate/deactivate a gig
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            gig = Gigs.objects.get(pk=pk)
        except Gigs.DoesNotExist:
            return Response({'detail': 'Gig not found.'}, status=status.HTTP_404_NOT_FOUND)

        gig.is_active = not gig.is_active
        gig.save()
        return Response({
            'id': gig.id,
            'title': gig.title,
            'is_active': gig.is_active,
            'message': f'Gig has been {"activated" if gig.is_active else "deactivated"} successfully.'
        })


# Top rated gigs
class TopRatedGigListView(generics.ListAPIView):
    serializer_class = GigSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            Gigs.objects.filter(is_active=True)
            .annotate(avg_rating=Avg('reviews__rating'))
            .filter(avg_rating__gte=3.5)  
            .order_by('avg_rating')
        )