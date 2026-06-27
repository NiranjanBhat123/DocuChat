import logging
import threading
from rest_framework import viewsets, parsers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Collection, Document
from .serializers import CollectionSerializer, DocumentSerializer, DocumentUploadSerializer

logger = logging.getLogger('collections_app')


class CollectionViewSet(viewsets.ModelViewSet):
    """CRUD for Collections."""
    queryset = Collection.objects.prefetch_related('documents').all()
    serializer_class = CollectionSerializer

    @extend_schema(methods=['get'], responses=DocumentSerializer(many=True))
    @extend_schema(
        methods=['post'],
        request={'multipart/form-data': DocumentUploadSerializer},
        responses=DocumentSerializer,
    )
    @action(
        detail=True,
        methods=['get', 'post'],      # both methods on same URL
        url_path='documents',
        url_name='documents',
        parser_classes=[parsers.MultiPartParser, parsers.FormParser],
    )
    def documents(self, request, pk=None):
        """
        GET  /api/collections/{id}/documents/ — list documents
        POST /api/collections/{id}/documents/ — upload a PDF
        """
        if request.method == 'GET':
            return self._list_documents(request, pk)
        return self._upload_document(request, pk)

    def _list_documents(self, request, pk):
        collection = self.get_object()
        docs = collection.documents.all()
        return Response(DocumentSerializer(docs, many=True).data)

    def _upload_document(self, request, pk):
        from .services.ingestion import ingest_document

        collection = self.get_object()

        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doc = Document.objects.create(
            collection=collection,
            title=serializer.validated_data['title'],
            file=serializer.validated_data['file'],
        )
        logger.info(f"Document '{doc.title}' uploaded to collection '{collection.name}'")

        thread = threading.Thread(target=ingest_document, args=(doc.id,))
        thread.daemon = True
        thread.start()

        return Response(
            DocumentSerializer(doc).data,
            status=status.HTTP_202_ACCEPTED,
        )