from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chat"
    verbose_name = gettext_lazy("Chat")

    def ready(self):
        from chat import signals
