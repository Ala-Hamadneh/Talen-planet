from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')

class MarkNotificationReadSerializer(serializers.Serializer):
    notification_id = serializers.IntegerField()
