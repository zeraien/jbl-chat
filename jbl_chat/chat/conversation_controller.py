from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_url_framework import ActionController
from django_url_framework.decorators import json_action, login_required

from chat.models import Message, Conversation
from jbl_chat.time_helpers import to_epoch


class ConversationController(ActionController):

    @login_required()
    def _before_filter(self, request):
        self.messages = request.user.authored_messages.select_related(
            "target", "author"
        ).not_deleted()
        self.conversations = request.user.conversations.all()

    def index(self, request, id: int):
        conversation: Conversation = get_object_or_404(self.conversations, pk=id)
        return {
            "id": id,
            "title": conversation.title,
            "messages": conversation.messages.not_deleted(),
        }

    def delete(self, request):
        pass
