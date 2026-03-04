# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Retrieval Augmented Generation (RAG) system using LangChain, Pinecone, and OpenAI. Documents are embedded and indexed into Pinecone, then retrieved at query time to augment LLM responses.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Requires a `.env` file with:
```
PINECONE_API_KEY=...
OPENAI_API_KEY=...
PINECONE_INDEX_NAME=langchain-sample-index
```

## Commands

| Command | Purpose |
|---------|---------|
| `streamlit run chatbot_rag.py` | Launch the interactive chatbot UI |
| `python ingestion.py` | Index PDFs from `documents/` into Pinecone |
| `python retrieval.py` | Run a single hardcoded retrieval query |
| `python sample_ingestion.py` | Index hardcoded sample documents (demo) |
| `python sample_retrieval.py` | Query the sample index (demo) |

No build step or linting is configured.

## Architecture

### RAG Pipeline

```
PDF files (documents/)
    → PyPDFDirectoryLoader
    → RecursiveCharacterTextSplitter (chunk_size=800, overlap=400)
    → OpenAI text-embedding-3-large (3072 dimensions)
    → Pinecone vector store (cosine, serverless AWS us-east-1)

User query
    → Embed with same model
    → similarity_score_threshold retriever (k=3, threshold=0.5)
    → Retrieved chunks injected into system prompt
    → GPT-4o generates response
```

### Key Files

- [chatbot_rag.py](chatbot_rag.py) — Streamlit UI; manages session state, retrieval, and LLM calls
- [ingestion.py](ingestion.py) — Creates Pinecone index if absent, loads and chunks PDFs, upserts embeddings
- [retrieval.py](retrieval.py) — Standalone retrieval demo
- `sample_*.py` — Self-contained demo scripts using hardcoded documents and a separate `sample-index`

### Models & Config

- **Embeddings**: `text-embedding-3-large` (3072 dims)
- **LLM**: `gpt-4o` (temperature=1)
- **Pinecone index**: cosine metric, serverless spec on AWS us-east-1
- **Retriever**: `similarity_score_threshold`, k=3–5, threshold=0.5–0.6

### Chat History

`chatbot_rag.py` stores `messages` in `st.session_state` as a list of `{"role": ..., "content": ...}` dicts. The full history is passed to `ChatOpenAI` on each turn along with a system message containing the retrieved context.
