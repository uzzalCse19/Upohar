
from django.apps import AppConfig

class NotifyChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notify_chat"

    def ready(self):
        import notify_chat.signals   # ✅ This line is missing
