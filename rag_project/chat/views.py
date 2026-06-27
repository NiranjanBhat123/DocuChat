import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from collections_app.models import Collection
from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer, AskSerializer
from .services.rag import answer_question

logger = logging.getLogger('chat')


class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.prefetch_related('messages').filter(
            collection_id=self.kwargs['collection_pk']
        )

    def perform_create(self, serializer):
        collection = Collection.objects.get(pk=self.kwargs['collection_pk'])
        serializer.save(collection=collection)

    @extend_schema(request=AskSerializer, responses=MessageSerializer)
    @action(detail=True, methods=['post'], url_path='ask')
    def ask(self, request, collection_pk=None, pk=None):
        """
        POST /api/collections/{collection_id}/sessions/{session_id}/ask/
        Send a question, get an answer grounded in the collection's documents.
        """
        session = self.get_object()

        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']

        # Save the user's message
        user_msg = Message.objects.create(
            session=session,
            role=Message.Role.USER,
            content=question,
        )
        logger.info(f"User asked: '{question}' in session {session.id}")

        # Run RAG pipeline
        result = answer_question(session.collection_id, question)

        # Save the assistant's response
        assistant_msg = Message.objects.create(
            session=session,
            role=Message.Role.ASSISTANT,
            content=result['answer'],
            sources=result['sources'],
        )

        return Response(
            MessageSerializer(assistant_msg).data,
            status=status.HTTP_200_OK,
        )