from django.contrib.auth import get_user_model
from django_url_framework import ActionController
from django_url_framework.decorators import login_required
from sesame.utils import get_token

from chat.models import Message, Conversation


class DashboardController(ActionController):

    @login_required()
    def _before_filter(self, request):
        self.users = get_user_model().objects.filter(is_active=True)
        self.messages = Message.objects.filter(author=request.user)
        self.conversations = Conversation.objects.filter(users__in=[request.user])

    def index(self, request):
        token = get_token(request.user)
        return {
            "conversations": self.conversations,
            "conversation": self.conversations.first,
            "messages": self.messages,
            "websockets_token": token,
            "users": self.users.exclude(pk=request.user.pk),
        }
