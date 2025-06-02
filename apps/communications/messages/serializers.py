from rest_framework import serializers
from .models import Room, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('sender', 'timestamp', 'room')


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()


    class Meta:
        model = Room
        fields = ['id', 'user1',  'created_at', 'last_message', 'other_user', 'unread_count']

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        return MessageSerializer(last_msg).data if last_msg else None

    def get_other_user(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        current_user = request.user
        other_user = obj.user2 if obj.user1 == current_user else obj.user1
        return UserSummarySerializer(other_user).data
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()