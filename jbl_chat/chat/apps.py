from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chat"
    verbose_name = ugettext_lazy("Chat")
