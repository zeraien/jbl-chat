from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django.db.models.signals import m2m_changed
from django.utils.translation import gettext as _
from django.db import models


class Conversation(TimeStampedModel):
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
