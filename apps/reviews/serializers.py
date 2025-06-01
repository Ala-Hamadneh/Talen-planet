from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.CharField(source='reviewer.username', read_only=True)
    reviewer_image = serializers.ImageField(source='reviewer.profile_picture', read_only=True)
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('reviewer', 'reviewer_image', 'seller', 'gig', 'order', 'created_at', 'is_active')
