import logging
from typing import List, Dict
from django.conf import settings
from google import genai
from google.genai import types
from google.genai.errors import ClientError

logger = logging.getLogger('chat')

EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "gemini-3.5-flash"   
TOP_K = 5


def embed_query(question: str) -> List[float]:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return response.embeddings[0].values


def retrieve_chunks(collection_id: int, query_embedding: List[float]) -> List[Dict]:
    import chromadb
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    chroma_col = client.get_or_create_collection(f"collection_{collection_id}")

    results = chroma_col.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas"],
    )

    chunks = []
    for text, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({
            "text": text,
            "chunk_index": meta.get("chunk_index"),
            "document_id": meta.get("document_id"),
        })

    logger.info(f"Retrieved {len(chunks)} chunks from collection {collection_id}")
    return chunks


def build_prompt(question: str, chunks: List[Dict]) -> str:
    context = "\n\n---\n\n".join([c["text"] for c in chunks])
    return f"""You are a helpful assistant that answers questions strictly based on the provided context.
If the answer cannot be found in the context, say "I don't have enough information in the provided documents to answer this."

Context:
{context}

Question: {question}

Answer:"""


def generate_answer(prompt: str) -> str:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )
    return response.text


def answer_question(collection_id: int, question: str) -> Dict:
    logger.info(f"RAG query for collection {collection_id}: '{question}'")

    query_embedding = embed_query(question)
    chunks = retrieve_chunks(collection_id, query_embedding)
    prompt = build_prompt(question, chunks)
    answer = generate_answer(prompt)

    logger.info(f"Answer generated — {len(answer)} chars")
    return {
        "answer": answer,
        "sources": chunks,
    }