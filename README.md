# RAGnosis AI
**Manual-Grounded Diagnostic AI for Dell Laptops**

> *"Stop guessing. Start citing."*

---

## What It Does

RAGnosis AI answers hardware diagnostic questions using **only official Dell service manuals** — no hallucinations, no generic advice, no internet lookups at runtime.

Ask it why your laptop is showing a 2-white 2-yellow LED pattern. It will tell you it's a BIOS/ROM failure **and** walk you through the exact recovery steps from page 72 of the service manual, with the citation.

---

## Live Demo

```
User:   My Dell Precision 5560 shows 2 white and 2 yellow lights. What's wrong and how do I fix it?

RAGnosis:
  DIAGNOSIS: LED code 2,2 — System board BIOS or ROM failure.
  [Manual: prec5560-sm-en-us, Section: Troubleshooting > System diagnostic lights, Page 69]

  SOLUTION: Perform BIOS recovery using a USB drive:
  1. Shut down the system and boot to System Setup.
  2. Enable "BIOS Recovery from Hard Drive" in the Maintenance section.
  3. Hold Ctrl + Esc, press Power — hold until BIOS Recovery Menu appears.
  4. Select "Recover BIOS" and click Continue.
  [Manual: prec5560-sm-en-us, Section: Troubleshooting > BIOS recovery > BIOS recovery using USB drive, Page 72]
```

Every answer is structured. Every claim is cited. If the manual doesn't cover it, RAGnosis says so.

---

## Why RAGnosis

| Problem | RAGnosis Solution |
|---|---|
| LLMs hallucinate repair steps | Answers grounded strictly in retrieved manual chunks |
| Generic troubleshooting guides miss model-specific steps | Indexed from official Dell Precision 5560 service manual |
| You don't know which page to look at | Citations include manual name, section, and page number |
| LED codes give diagnosis but no fix | Dual-pass retrieval fetches both diagnosis and recovery steps |

---

## Architecture

```
User Query
    │
    ▼
Policy: validate query
    │
    ▼
Retriever: dual-pass semantic search
  Pass 1 — symptom match  ──┐
  Pass 2 — fix/recovery    ──┤──► top-k chunks (all-MiniLM-L6-v2 + ChromaDB)
                             │
    ▼                        │
Policy: relevance threshold  ◄┘
    │
    ▼
Prompt: constrained system prompt + context blocks
    │
    ▼
LLM: OpenRouter (free models, temperature=0)
    │
    ▼
Answer: Diagnosis + Fix + Citations
    │
    ▼
FastAPI  ──►  Streamlit UI
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers, local) |
| Vector Store | ChromaDB (cosine similarity, persistent) |
| LLM | OpenRouter free models (OpenAI-compatible API) |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| PDF Parsing | PyMuPDF (fitz) |
| Containerization | Docker Compose |

---

## Guardrails (Non-Negotiable)

- Answers drawn **exclusively** from retrieved manual chunks
- Every claim carries a citation: `[Manual, Section, Page]`
- Insufficient evidence → explicit refusal, not a guess
- Temperature locked at `0.0` — deterministic output
- Input validation rejects empty, trivial, and injection-pattern queries

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- OpenRouter API key (free at [openrouter.ai](https://openrouter.ai))

### 1 — Configure

```bash
cp .env.example .env
# Edit .env — add your OPENROUTER_API_KEY
```

### 2 — Ingest Manuals

```bash
docker compose --profile ingest up ingest --build
```

Runs the full pipeline: PDF extraction → section chunking → embedding → ChromaDB indexing. Takes ~2 minutes on first run.

### 3 — Start the Stack

```bash
docker compose up --build -d
```

| Service | URL |
|---|---|
| Chat UI | http://localhost:8501 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Services

```
docker-compose.yml
├── chromadb   — vector store (persistent named volume)
├── ingest     — one-shot pipeline (profile: ingest)
├── api        — FastAPI, POST /chat + GET /health
└── ui         — Streamlit chat interface
```

The `ingest` service is profile-gated — it never starts accidentally with `docker compose up`.

---

## API

### `POST /chat`
```json
{
  "query": "How do I remove the battery?",
  "top_k": 8
}
```

Response:
```json
{
  "answer": "...",
  "citations": [
    { "manual": "prec5560-sm-en-us", "section": "Removing the battery", "page": 42 }
  ],
  "insufficient_evidence": false,
  "model": "nvidia/nemotron-3-super-120b-a12b:free"
}
```

### `GET /health`
```json
{ "status": "ok", "chunks_indexed": 120, "embed_model": "all-MiniLM-L6-v2" }
```

---

## Project Structure

```
ragnosis-ai/
├── data/
│   └── raw/                        # Dell Precision 5560 PDFs (5 manuals)
├── docker/
│   ├── Dockerfile.app              # Shared API + UI image
│   └── Dockerfile.ingest           # Ingest pipeline image
├── ingest/
│   ├── pdf_to_text.py              # PDF → JSONL (page-level, with headings)
│   ├── chunker.py                  # JSONL → section chunks (600-token max, 50-token overlap)
│   ├── build_index.py              # Chunks → ChromaDB (with idempotency guard)
│   └── run_pipeline.py             # Docker entrypoint: runs all 3 steps
├── rag/
│   ├── config.py                   # Central env-var config
│   ├── embeddings.py               # sentence-transformers wrapper (cached model)
│   ├── vectorstore.py              # ChromaDB HttpClient wrapper
│   ├── retriever.py                # Semantic top-k retrieval
│   ├── prompt.py                   # Constrained system prompt + context formatter
│   └── answerer.py                 # OpenRouter call, citation parsing, retry logic
├── agent/
│   ├── policy.py                   # Query validation, retrieval quality, citation coverage
│   ├── tools.py                    # search_manual tool + registry
│   └── agent.py                    # Dual-pass retrieval loop + answer orchestration
├── api/
│   └── main.py                     # FastAPI: /chat, /health, lifespan init
├── ui/
│   └── app.py                      # Streamlit: chat history, citations panel, health sidebar
├── docker-compose.yml
├── requirements-app.txt
├── requirements-ingest.txt
└── .env.example
```

---

## Knowledge Base (v1)

All answers sourced from official Dell Precision 5560 documentation:

| Manual | Coverage |
|---|---|
| Service Manual (`prec5560-sm-en-us`) | Component removal/replacement, BIOS, LED codes, diagnostics |
| Setup & Specifications (`prec5560-ss-en-us`) | Hardware specs, ports, dimensions |
| Owner's Manual | Basic usage, safety |
| Reference Guide | Quick reference |
| Workstation Support | Support resources |

---

## Roadmap

- **v1 (current)** — Single model (Dell Precision 5560), CLI + web UI, manual-grounded RAG
- **v2** — Multi-model Dell support, agentic workflow (diagnose → verify → repair)
- **v3** — Image-based issue identification, BIOS log parsing, multi-brand expansion

---

*RAGnosis AI — turning static service manuals into an intelligent repair assistant.*
