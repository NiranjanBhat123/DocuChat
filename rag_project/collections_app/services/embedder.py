import logging
from typing import List
from django.conf import settings
from google import genai
from google.genai import types

logger = logging.getLogger('collections_app')

EMBEDDING_MODEL = "gemini-embedding-001"


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """
    Embeds all chunks in a single batch API call instead of one call
    per chunk — much faster and uses fewer API quota units.
    """
    if not chunks:
        logger.warning("embed_chunks called with empty list")
        return []

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    logger.info(f"Batch embedding {len(chunks)} chunks via Gemini ({EMBEDDING_MODEL})")

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=chunks,   # pass the whole list at once
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
        )
    )

    embeddings = [e.values for e in response.embeddings]
    logger.info(f"Batch embedding complete — got {len(embeddings)} vectors")
    return embeddings