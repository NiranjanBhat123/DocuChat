from django.contrib import admin
from .models import ChatSession, Message


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'collection', 'title', 'created_at']
    list_filter = ['collection']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'session']

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = 'Content'