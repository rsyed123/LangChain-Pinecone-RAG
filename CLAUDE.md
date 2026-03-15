# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Retrieval Augmented Generation (RAG) system using LangChain, Pinecone, and OpenAI. Documents are embedded and indexed into Pinecone, then retrieved at query time to augment LLM responses. There are two UI options: a legacy Streamlit chatbot and a current React + FastAPI app with Google SSO.

## Setup

**Backend:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

**`.env` file** (root):
```
PINECONE_API_KEY=...
OPENAI_API_KEY=...
PINECONE_INDEX_NAME=langchain-sample-index
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
FRONTEND_URL=http://localhost:5173
COOKIE_SECRET=...
```

## Commands

**React + FastAPI app (current):**

| Command | Purpose |
|---------|---------|
| `uvicorn backend.main:app --reload` | Start FastAPI backend (port 8000) |
| `cd frontend && npm run dev` | Start React frontend (port 5173) |

**Ingestion:**

| Command | Purpose |
|---------|---------|
| `python ingestion.py` | Index PDFs from `documents/` into Pinecone |
| `python ingest_url.py <url>` | Fetch a web page and ingest it into Pinecone |

**Legacy Streamlit UI:**

| Command | Purpose |
|---------|---------|
| `streamlit run chatbot_rag.py` | Launch the Streamlit chatbot |

**Demo/dev scripts:**

| Command | Purpose |
|---------|---------|
| `python sample_ingestion.py` | Index hardcoded sample docs into `sample-index` |
| `python sample_retrieval.py` | Query the sample index |
| `python retrieval.py` | Run a single hardcoded retrieval query |

No build step or linting is configured.

## Architecture

### Two UIs, one RAG pipeline

```
React frontend (frontend/, Vite + React 18)
    ↕ HTTP (credentials: 'include')
FastAPI backend (backend/)
    ├── /auth  — Google OAuth via authlib; session stored in signed cookie
    └── /api/chat  — requires auth; delegates to backend/rag.py

Legacy: chatbot_rag.py (Streamlit, no auth)
```

### RAG Pipeline

```
PDF files (documents/)        Web pages
    → PyPDFDirectoryLoader        → ingest_url.py (BeautifulSoup)
    → RecursiveCharacterTextSplitter (chunk_size=800, overlap=400)
    → OpenAI text-embedding-3-large (3072 dims)
    → Pinecone vector store (cosine, serverless AWS us-east-1)

User query
    → Embed with same model
    → similarity_score_threshold retriever (k=3, threshold=0.5)
    → Retrieved chunks injected into system prompt
    → GPT-4o generates response ("I don't know." if no docs retrieved)
```

### Key Files

- [backend/main.py](backend/main.py) — FastAPI app; mounts auth + chat routers, configures CORS and session middleware
- [backend/auth.py](backend/auth.py) — Google OAuth login/callback/logout/me; `get_current_user` dependency
- [backend/chat.py](backend/chat.py) — `POST /api/chat`; validates auth, calls `get_rag_response`
- [backend/rag.py](backend/rag.py) — Core RAG logic: retrieval + GPT-4o invocation; initialized at module load
- [frontend/src/App.jsx](frontend/src/App.jsx) — Root component; checks `/auth/me` on load, routes to `<Login>` or `<Chat>`
- [chatbot_rag.py](chatbot_rag.py) — Legacy Streamlit UI; session state holds message history
- [ingestion.py](ingestion.py) — Creates Pinecone index if absent, loads and chunks PDFs, upserts embeddings
- [ingest_url.py](ingest_url.py) — Fetches a URL, strips HTML, chunks and upserts into Pinecone

### Models & Config

- **Embeddings**: `text-embedding-3-large` (3072 dims)
- **LLM**: `gpt-4o` (temperature=1)
- **Pinecone index**: cosine metric, serverless spec on AWS us-east-1
- **Retriever**: `similarity_score_threshold`, k=3, threshold=0.5

### Auth Flow

Google OAuth is handled entirely by the backend. The frontend redirects to `/auth/login`, Google redirects back to `/auth/callback`, and the backend stores `{email, name, picture}` in a server-side session cookie. The frontend checks `/auth/me` on load to restore session state. All `/api/*` routes require a valid session via the `get_current_user` FastAPI dependency.
