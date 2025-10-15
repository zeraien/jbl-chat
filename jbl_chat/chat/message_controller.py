from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_url_framework import ActionController
from django_url_framework.decorators import json_action, login_required

from chat.models import Message
from jbl_chat.time_helpers import to_epoch


class MessageController(ActionController):

    @login_required()
    def _before_filter(self, request):
        self.messages = request.user.authored_messages.select_related(
            "target", "author"
        ).not_deleted()

    def index(self, request, id: int):
        message: Message = get_object_or_404(self.messages, pk=id)
        return {"id": id, "content": message.content}

    def get(self, request, id: int):
        message: Message = get_object_or_404(self.messages, pk=id)
        return {"content": message.content}

    @json_action()
    def api__get(self, request, id: int):
        message: Message = get_object_or_404(self.messages, pk=id)
        author: User = message.author
        target: User = message.target

        return {
            "target": {"id": target.pk, "name": target.get_full_name()},
            "author": {"id": author.pk, "name": author.get_full_name()},
            "content": message.content,
            "conversation_id": message.conversation_id,
            "created": to_epoch(message.created),
            "modified": to_epoch(message.modified),
            "state": message.state,
        }

    def send(self, request):
        pass

    def update(self, request):
        pass

    def delete(self, request):
        pass
