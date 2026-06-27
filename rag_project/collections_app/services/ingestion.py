import logging
from collections_app.models import Document
from .pdf_processor import extract_text
from .chunker import split_into_chunks
from .embedder import embed_chunks
from .chroma_store import store_chunks

logger = logging.getLogger('collections_app')


def ingest_document(document_id: int) -> None:
    """
    Full ingestion pipeline for a single Document:
      1. Extract text from PDF
      2. Split into chunks
      3. Embed each chunk via Gemini
      4. Store chunks + embeddings in ChromaDB
      5. Update Document status in SQLite

    This function is designed to be called from a background task
    (Celery, Django-Q, or even a thread for now).
    """
    doc = Document.objects.get(pk=document_id)
    logger.info(f"Starting ingestion for Document id={document_id} title='{doc.title}'")

    try:
        doc.status = Document.Status.PROCESSING
        doc.save(update_fields=['status'])

        # Step 1: extract
        text = extract_text(doc.file.path)

        # Step 2: chunk
        chunks = split_into_chunks(text)
        if not chunks:
            raise ValueError("No text could be extracted from this PDF")

        # Step 3: embed
        embeddings = embed_chunks(chunks)

        # Step 4: store in ChromaDB
        store_chunks(
            collection_id=doc.collection_id,
            document_id=doc.id,
            chunks=chunks,
            embeddings=embeddings,
        )

        # Step 5: mark done
        doc.status = Document.Status.DONE
        doc.chunk_count = len(chunks)
        doc.save(update_fields=['status', 'chunk_count'])

        logger.info(f"Ingestion complete for Document id={document_id} — {len(chunks)} chunks stored")

    except Exception as e:
        logger.exception(f"Ingestion failed for Document id={document_id}: {e}")
        doc.status = Document.Status.FAILED
        doc.error_message = str(e)
        doc.save(update_fields=['status', 'error_message'])
        raise