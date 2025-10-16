from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_url_framework import ActionController
from django_url_framework.decorators import json_action, login_required

from chat.models import Message, Conversation
from jbl_chat.time_helpers import to_epoch


class ConversationController(ActionController):

    @login_required()
    def _before_filter(self, request):
        self.users = User.objects.filter(is_active=True)
        self.messages = request.user.authored_messages.select_related(
            "author"
        ).not_deleted()
        self.conversations = request.user.conversations.all()

    def index(self, request, conversation_id: int):
        conversation: Conversation = get_object_or_404(
            self.conversations, pk=conversation_id
        )
        return {
            "conversation": conversation,
            "title": conversation.title,
            "messages": conversation.messages.not_deleted().not_drafts(),
        }

    def user(self, request, user_id: id):
        user = get_object_or_404(self.users, pk=user_id)
        if user.pk == request.user.pk:
            return self._print("Invalid user"), 400

        conversation: Conversation = Conversation.objects.get_or_create_for_users(
            users=[user, request.user]
        )
        return self._go(f"/conversation/{conversation.pk}/")
