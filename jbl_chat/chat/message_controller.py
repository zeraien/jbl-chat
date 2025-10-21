from django.shortcuts import get_object_or_404
from django_url_framework import ActionController
from django_url_framework.decorators import login_required

from chat.enums import MSG_STATE
from chat.fsm import MessageFlow
from chat.models import Message, Conversation


class MessageController(ActionController):

    @login_required()
    def _before_filter(self, request):
        self.messages = request.user.authored_messages.select_related(
            "author"
        ).not_deleted()
        self.conversations = request.user.conversations.all()

    def list(self, request, conversation_id: int):
        conversation: Conversation = get_object_or_404(
            self.conversations, pk=conversation_id
        )
        return {
            "conversation": conversation,
            "messages": conversation.messages.not_deleted().not_drafts(),
        }

    def compose_box(self, request, conversation_id: int):
        conversation = get_object_or_404(self.conversations, pk=conversation_id)
        draft_message = conversation.messages.filter(
            author=request.user, state=MSG_STATE.DRAFT
        ).first()
        if not draft_message:
            draft_message = Message.objects.create(
                author=request.user, conversation=conversation, content=""
            )

        return {
            "draft_message": draft_message,
            "conversation_name": str(
                conversation.users.all().exclude(pk=request.user.pk).first()
            ),
        }

    def send(self, request):
        message_id = request.POST["message_id"]
        message = get_object_or_404(self.messages, pk=message_id)
        message.content = request.POST.get("message_text", "").strip()
        conversation = message.conversation

        if message.content != "":
            flow = MessageFlow(message)
            flow.mark_sent()
            message.save()

        return self._go(f"/message/compose_box/{conversation.pk}/")

    def update(self, request):
        message_id = request.POST["message_id"]
        message = get_object_or_404(self.messages, pk=message_id)
        message.content = request.POST["message_text"]
        message.save()
        return self._as_json(True)
