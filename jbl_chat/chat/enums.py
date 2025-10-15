from django.utils.translation import gettext as _
from enum import unique

from django.db.models import TextChoices


@unique
class MSG_STATE(TextChoices):
    DRAFT = "DRAFT", _("draft")
    SENDING = "SENDING", _("sending")
    SENT = "SENT", _("sent")
    RECEIVED = "RECEIVED", _("received")
    READ = "READ", _("read")
    ERROR = "ERROR", _("error")
    CANCELLED = "CANCELLED", _("cancelled")
    RETRY = "RETRY", _("retry")
    DELETED = "DELETED", _("deleted")
