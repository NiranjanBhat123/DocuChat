import logging
from django.db import models
from collections_app.models import Collection
from collections_app.fields import SnowflakeIDField

logger = logging.getLogger('chat')


class ChatSession(models.Model):
    """
    A conversation thread tied to a specific Collection.
    One collection can have many sessions (e.g. different users or topics).
    """
    id = SnowflakeIDField(primary_key=True)
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
    )
    title = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session {self.id} — {self.collection.name}"


class Message(models.Model):
    """
    A single turn in a ChatSession.
    role = 'user' for questions, 'assistant' for Gemini answers.
    sources stores the raw chunk texts used to generate the answer.
    """
    class Role(models.TextChoices):
        USER      = 'user',      'User'
        ASSISTANT = 'assistant', 'Assistant'

    id = SnowflakeIDField(primary_key=True)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    sources = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"