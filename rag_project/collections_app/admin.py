from django.contrib import admin
from .models import Collection, Document


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'collection', 'status', 'chunk_count', 'uploaded_at']
    list_filter = ['status', 'collection']
    search_fields = ['title']
    readonly_fields = ['status', 'chunk_count', 'error_message', 'uploaded_at']