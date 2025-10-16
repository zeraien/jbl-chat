from django.contrib.auth.models import User
from django.template.defaultfilters import truncatewords
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext as _
from django.db import models

from chat.enums import MSG_STATE
from chat.models import Conversation


class MessageManager(models.QuerySet):

    def not_deleted(self):
        return self.exclude(state=MSG_STATE.DELETED)

    def not_drafts(self):
        return self.exclude(state=MSG_STATE.DRAFT)


class Message(TimeStampedModel):
    objects = MessageManager.as_manager()

    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        ordering = ["created"]

    author = models.ForeignKey(
        User,
        verbose_name=_("author"),
        related_name="authored_messages",
        on_delete=models.CASCADE,
    )
    conversation = models.ForeignKey(
        Conversation,
        verbose_name=_("conversation"),
        related_name="messages",
        on_delete=models.CASCADE,
    )
    state = models.CharField(
        max_length=10, choices=MSG_STATE.choices, default=MSG_STATE.DRAFT, db_index=True
    )
    content = models.TextField()

    def __str__(self):
        txt = truncatewords(self.content, 5)
        if txt != self.content:
            return f"{txt}..."
        return self.content
