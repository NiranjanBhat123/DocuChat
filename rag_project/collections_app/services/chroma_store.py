import logging
from typing import List
from django.conf import settings
import chromadb

logger = logging.getLogger('collections_app')

# One persistent client for the whole Django process
_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)


def _get_collection(collection_id: int):
    """
    Each Django Collection gets its own ChromaDB collection namespace.
    Using the ID as the name guarantees uniqueness.
    """
    name = f"collection_{collection_id}"
    return _client.get_or_create_collection(name=name)


def store_chunks(
    collection_id: int,
    document_id: int,
    chunks: List[str],
    embeddings: List[List[float]],
) -> None:
    """
    Stores chunks + embeddings in ChromaDB under the given collection.
    IDs are prefixed with document_id so we can filter or delete by document later.
    """
    chroma_col = _get_collection(collection_id)

    ids = [f"doc{document_id}_chunk{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]

    chroma_col.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    logger.info(f"Stored {len(chunks)} chunks in ChromaDB collection {collection_id}")