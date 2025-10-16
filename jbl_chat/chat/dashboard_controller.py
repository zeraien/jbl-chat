from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_url_framework import ActionController
from django_url_framework.decorators import json_action, login_required, template_name

from chat.models import Message, Conversation
from jbl_chat.time_helpers import to_epoch


class DashboardController(ActionController):

    @login_required()
    def _before_filter(self, request):
        self.users = User.objects.filter(is_active=True)
        self.messages = Message.objects.filter(author=request.user)
        self.conversations = Conversation.objects.filter(users__in=[request.user])

    def index(self, request):
        return {
            "conversations": self.conversations,
            "conversation": self.conversations.first,
            "messages": self.messages,
            "users": self.users.exclude(pk=request.user.pk),
        }
