from rest_framework import serializers
from .models import ChatSession, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'sources', 'created_at']
        read_only_fields = ['id', 'role', 'sources', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'collection', 'title', 'messages', 'created_at']
        read_only_fields = ['id', 'created_at']


class AskSerializer(serializers.Serializer):
    """What the user sends to the chat endpoint."""
    question = serializers.CharField(min_length=1, max_length=2000)