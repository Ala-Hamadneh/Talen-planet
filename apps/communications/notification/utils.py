from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def notify_user(user, title, body, notification_type='info', target_url=None):
    notification = Notification.objects.create(
        user=user,
        title=title,
        body=body,
        notification_type=notification_type,
        target_url=target_url
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "content": {
                "title": title,
                "body": body,
                "type": notification_type,
                "url": target_url,
                "created_at": str(notification.created_at),
            },
        },
    )
    
