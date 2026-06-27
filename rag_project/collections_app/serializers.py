from rest_framework import serializers
from .models import Collection, Document


class DocumentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file',
            'status', 'chunk_count',
            'error_message', 'uploaded_at',
        ]
        read_only_fields = ['status', 'chunk_count', 'error_message', 'uploaded_at']


class DocumentUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError(
                "Only PDF files are supported. Please upload a .pdf file."
            )
        return value

    class Meta:
        ref_name = 'DocumentUpload'


class CollectionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'document_count', 'documents', 'created_at']
        read_only_fields = ['created_at']

    def get_document_count(self, obj) -> int:
        return obj.documents.count()