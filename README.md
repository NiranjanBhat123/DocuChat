


https://github.com/user-attachments/assets/31ddd725-9e9f-4c2b-9cdf-383bbc328a7a



Upload PDF research papers into collections and chat with them using AI. Built with React + shadcn/ui and Django REST Framework.

---

## Architecture

```
┌─────────────────────────────────────────┐
│           React Frontend                │
│  HomePage → CollectionPage              │
│  DocumentPanel (upload) + ChatPanel     │
└──────────────┬──────────────────────────┘
               │ axios  localhost:8000/api
┌──────────────▼──────────────────────────┐
│         Django REST Framework           │
│  CollectionViewSet  ChatSessionViewSet  │
│  collections_app    chat                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       PostgreSQL + pgvector             │
│  Collections / Documents / Chunks       │
│  ChatSessions / Messages                │
└─────────────────────────────────────────┘
```

---

## RAG Pipeline

### Ingestion (background thread on upload)

```
PDF upload
    │
    ▼
Extract text → Chunk → Embed → Store vectors in pgvector
    │
    ▼
Document status: pending → processing → done | failed
```

Frontend polls `GET /documents/` every 3s until status resolves.

### Chat (on each question)

```
User question
    │
    ▼
Embed question → Similarity search (top-K chunks)
    │
    ▼
Build prompt [system + context chunks + question]
    │
    ▼
LLM call → Answer + source chunks returned to UI
```

---

## Data Model

```
Collection ──< Document       Collection ──< ChatSession ──< Message
               status:                        role: user | assistant
               pending                        sources: JSONField
               processing
               done
               failed
```

All IDs use `SnowflakeIDField` and are serialized as **strings** — JS `Number` can't safely represent 64-bit integers.

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/api/collections/` | List / create collections |
| `GET/POST` | `/api/collections/{id}/documents/` | List / upload PDFs |
| `POST` | `/api/collections/{id}/sessions/` | Create chat session |
| `POST` | `/api/collections/{id}/sessions/{sid}/ask/` | Ask a question |

Interactive docs: `http://localhost:8000/api/docs/`

---

## Setup

### Prerequisites
- Python 3.11+, Node.js 18+, PostgreSQL 15+ with pgvector, LLM API key

### Backend

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# PostgreSQL
psql -c "CREATE DATABASE docuchat;"
psql -d docuchat -c "CREATE EXTENSION vector;"

python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd docuchat-ui
npm install
npx shadcn@latest add button card badge dialog input textarea
npm run dev
```

### Environment Variables

```env
SECRET_KEY=...
DATABASE_URL=postgresql://user:pass@localhost:5432/docuchat
GEMINI_API_KEY=...        # or ANTHROPIC_API_KEY / OPENAI_API_KEY
EMBEDDING_MODEL=models/text-embedding-004
RAG_TOP_K=5
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MEDIA_ROOT=media/
```

---

## Project Structure

```
DocuChat/
├── collections_app/        # Collection & Document models, ingestion
│   └── services/ingestion.py
├── chat/                   # ChatSession, Message, RAG pipeline
│   └── services/rag.py
├── config/                 # Django settings & root URLs
└── docuchat-ui/
    └── src/
        ├── api/client.ts
        ├── components/     # ChatPanel, DocumentPanel, modals
        ├── pages/          # HomePage, CollectionPage
        └── types/
```
