from django.apps import AppConfig

class MessagesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.communications.messages'
    label = 'chat_messages'  
