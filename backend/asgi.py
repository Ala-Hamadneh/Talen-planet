import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.communications.messages.middleware import JWTAuthMiddleware
import apps.communications.messages.routing
import apps.communications.notification.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            apps.communications.messages.routing.websocket_urlpatterns +
            apps.communications.notification.routing.websocket_urlpatterns
        )
    ),
})
