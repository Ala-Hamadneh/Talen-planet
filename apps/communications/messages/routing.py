from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/messages/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/messages/rooms/$', consumers.RoomNotificationConsumer.as_asgi()),
]
