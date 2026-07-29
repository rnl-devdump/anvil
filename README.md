# Anvil — LLM-RAG Quiz Application

CPU-friendly quiz generation and document Q&A using Ollama, ChromaDB, Instructor, and CustomTkinter.

## Prerequisites

1. [Ollama](https://ollama.com/) installed and running locally.
2. Pull the required models:

```bash
ollama pull phi4-mini
ollama pull nomic-embed-text
```

## Install

```bash
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python anvil.py
```

## Architecture

| Component | Role |
|-----------|------|
| **PyMuPDF** | PDF text extraction |
| **ChromaDB** | Local vector store + similarity search |
| **Instructor + Pydantic** | Strict JSON quiz schema enforcement |
| **Ollama (phi4-mini)** | Local LLM for quiz generation and RAG answers |
| **CustomTkinter** | Desktop UI |

### Quiz generation (chunk-and-map)

1. PDF/text is split into ~500-token semantic chunks.
2. Each chunk is sent to the LLM separately (1–2 questions per chunk).
3. Results are aggregated into a validated JSON array.

### RAG Q&A

1. User question is embedded with `nomic-embed-text`.
2. ChromaDB returns the top 3 relevant chunks.
3. The LLM answers using only retrieved context.

## Configuration

Optional environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANVIL_LLM_MODEL` | `phi4-mini` | Ollama chat model |
| `ANVIL_EMBED_MODEL` | `nomic-embed-text` | Ollama embedding model |
| `ANVIL_CHUNK_TOKENS` | `500` | Target chunk size |
| `ANVIL_RAG_TOP_K` | `3` | Retrieved chunks for Q&A |
| `ANVIL_CHROMA_PATH` | `./data/chroma_db` | Vector DB path |

## Quiz JSON schema

```json
[
  {
    "type": "MULTIPLE_CHOICE",
    "question": "...",
    "choices": ["...", "...", "...", "..."],
    "answer": "..."
  },
  {
    "type": "IDENTIFICATION",
    "question": "The ___ is ...",
    "answer": "..."
  }
]
```
