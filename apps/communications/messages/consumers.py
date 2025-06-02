import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from apps.communications.notification.utils import notify_user
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.contrib.auth import get_user_model
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user = self.scope["user"]
        self.room_group_name = f"chat_{self.room_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # ✅ Mark unread messages as read
        await self.mark_messages_as_read()

    @database_sync_to_async
    def mark_messages_as_read(self):
        try:
            room = Room.objects.get(id=self.room_id)
            if self.user in [room.user1, room.user2]:
                Message.objects.filter(room=room, is_read=False).exclude(sender=self.user).update(is_read=True)
        except Room.DoesNotExist:
            pass

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data['message']
        sender_id = self.scope['user'].id

        msg = await self.save_message(sender_id, self.room_id, message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg.content,
                'sender_id': sender_id,
                'timestamp': msg.timestamp.isoformat(),
                'message_id': msg.id,
                'room': self.room_id,
                'is_read': msg.is_read,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
            'room': event['room'],
            'is_read': event['is_read'],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, room_id, content):
        sender = User.objects.get(id=sender_id)
        room = Room.objects.get(id=room_id)
        message = Message.objects.create(sender=sender, room=room, content=content)

        receiver = room.user1 if room.user2 == sender else room.user2

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{receiver.id}_room_updates",
            {
                "type": "room_update",
                "room": room.id,
                "sender": sender.id,
            }
        )
        notify_user(
            user=receiver,
            title="New Message",
            body=f"You received a message from {sender.username}",
            notification_type="message"
        )

        return message
    


class RoomNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}_room_updates"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def room_update(self, event):
        # You can customize this message shape
        await self.send(text_data=json.dumps({
            "type": "room_update",
            "room": event["room"],
            "sender": event["sender"]
        }))
