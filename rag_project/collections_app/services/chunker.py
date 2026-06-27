import logging
from typing import List

logger = logging.getLogger('collections_app')

# These values are tunable. 500 tokens ≈ 400 words.
# Overlap ensures context doesn't get cut off at chunk boundaries.
CHUNK_SIZE = 500      # characters per chunk
CHUNK_OVERLAP = 50    # characters shared between consecutive chunks


def split_into_chunks(text: str) -> List[str]:
    """
    Splits a long text into overlapping fixed-size chunks.

    Why overlap? When a sentence spans a chunk boundary, without overlap
    the embedding for each chunk loses half the context. Overlapping
    preserves that continuity so retrieval stays accurate.
    """
    if not text.strip():
        logger.warning("Received empty text for chunking")
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP  # slide with overlap

    logger.info(f"Split text into {len(chunks)} chunks "
                f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks