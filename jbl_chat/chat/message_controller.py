from django.shortcuts import get_object_or_404
from django_url_framework import ActionController
from django_url_framework.decorators import json_action, login_required

from chat.enums import MSG_STATE
from chat.fsm import MessageFlow
from chat.models import Message, Conversation
from jbl_chat.time_helpers import to_epoch


class MessageController(ActionController):

    @login_required()
    def _before_filter(self, request):
        self.messages = request.user.authored_messages.select_related(
            "author"
        ).not_deleted()
        self.conversations = request.user.conversations.all()

    def index(self, request, id: int):
        message: Message = get_object_or_404(self.messages, pk=id)
        return {"id": id, "content": message.content}

    def list(self, request, conversation_id: int):
        conversation: Conversation = get_object_or_404(
            self.conversations, pk=conversation_id
        )
        return {
            "conversation": conversation,
            "messages": conversation.messages.not_deleted().not_drafts(),
        }

    def get(self, request, id: int):
        message: Message = get_object_or_404(self.messages, pk=id)
        return {"content": message.content}

    @json_action()
    def api__get(self, request, id: int):
        message: Message = get_object_or_404(self.messages, pk=id)
        author = message.author

        return {
            "author": {"id": author.pk, "name": author.get_full_name()},
            "content": message.content,
            "conversation_id": message.conversation_id,
            "created": to_epoch(message.created),
            "modified": to_epoch(message.modified),
            "state": message.state,
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

        return {"draft_message": draft_message}

    def send(self, request):
        message_id = request.POST["message_id"]
        message = get_object_or_404(self.messages, pk=message_id)
        message.content = request.POST["message_text"]
        conversation = message.conversation
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

    def delete(self, request):
        pass
