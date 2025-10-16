from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django.db.models.signals import m2m_changed
from django.utils.translation import gettext as _
from django.db import models


class ConversationManager(models.QuerySet):
    def get_or_create_for_users(self, users: list["User"]):
        ids = [u.pk for u in users]
        conversations = self.annotate(convo_count=models.Count("users")).filter(
            convo_count=len(ids)
        )
        for user_id in ids:
            conversations = conversations.filter(users__id=user_id)

        if conversations.count():
            return conversations.first()
        else:
            conversation = self.create()
            conversation.users.set(users)
            return conversation


class Conversation(TimeStampedModel):
    objects = ConversationManager.as_manager()
    title = models.CharField(_("title"), max_length=100, blank=True)
    users = models.ManyToManyField(
        User, verbose_name=_("users"), related_name="conversations"
    )

    def my_messages(self, author: User):
        return self.messages.filter(author=author)

    def generate_title(self):
        return _("conversation between %s") % ", ".join(
            self.users.values_list("username", flat=True)
        )

    def __str__(self):
        return self.title


def users_changed(sender, instance, **kwargs):
    instance.title = instance.generate_title()
    instance.save()


m2m_changed.connect(users_changed, sender=Conversation.users.through)
