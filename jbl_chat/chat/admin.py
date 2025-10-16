from django.contrib import admin

from .models import Message
from .models import Conversation


class MessageInline(admin.StackedInline):
    model = Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "created", "modified"]
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["author", "conversation", "__str__", "created", "state"]
    ordering = ["-created"]
    search_fields = ["author__first_name", "author__last_name", "author__username"]
    list_filter = ["state"]
