import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from apps.communications.notification.utils import notify_user

from django.contrib.auth import get_user_model
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = self.scope['user'].id

        # Save message to DB
        await self.save_message(sender_id, self.room_id, message)

        # Broadcast message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, room_id, content):
        sender = User.objects.get(id=sender_id)
        room = Room.objects.get(id=room_id)
        message = Message.objects.create(sender=sender, room=room, content=content)

        receiver = room.user1 if room.user2 == sender else room.user2
        notify_user(
            user=receiver,
            title="New Message",
            body=f"You received a message from {sender.username}",
            notification_type="message"
        )
        print(f"Notifying {receiver.username}")


        return message

