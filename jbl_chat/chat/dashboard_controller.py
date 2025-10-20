from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.shortcuts import get_object_or_404
from django_url_framework import ActionController
from django_url_framework.decorators import login_required, ajax_template_name
from sesame.utils import get_token

from chat.models import Conversation


class DashboardController(ActionController):

    def _before_filter(self, request):
        self.users = get_user_model().objects.filter(is_active=True)
        return {
            "websockets_host": settings.WEBSOCKETS_HOST
            or request.get_host().split(":")[0],
            "websockets_port": settings.WEBSOCKETS_PORT,
        }

    @login_required()
    def index(self, request):
        token = get_token(request.user)
        return {
            "websockets_token": token,
            "users": self.users.exclude(pk=request.user.pk),
        }

    @ajax_template_name("dashboard/_conversation.html")
    def conversation__for_user(self, request, user_id: id):
        user = get_object_or_404(self.users, pk=user_id)
        if user.pk == request.user.pk:
            return self._print("Invalid user"), 400

        conversation: Conversation = Conversation.objects.get_or_create_for_users(
            users=[user, request.user]
        )
        return {"conversation_id": conversation.pk}

    def login(self, request):
        if request.POST.get("user_id", "").strip() not in ("", None):
            user = get_object_or_404(self.users, pk=request.POST["user_id"])
            login(request, user, "django.contrib.auth.backends.ModelBackend")
            return self._go("/dashboard/")
        return {"users": self.users}
