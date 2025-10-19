import json

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django_redis import get_redis_connection

from chat.enums import MSG_STATE
from chat.models import Message


@receiver(post_delete, sender=Message)
@receiver(post_save, sender=Message)
def publish_event(instance: Message, **kwargs):
    if instance.state != MSG_STATE.DRAFT:
        content_type = ContentType.objects.get_for_model(instance)
        event = {
            "event_type": content_type.name,
            "message_id": instance.pk,
            "conversation_id": instance.conversation.pk,
            "author_id": instance.author.pk,
            "target_ids": list(
                instance.conversation.users.values_list("pk", flat=True)
            ),
            "message": instance.content,
            "timestamp": instance.created.isoformat(),
        }
        connection = get_redis_connection("default")
        payload = json.dumps(event)
        connection.publish("events", payload)
