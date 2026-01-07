# RAGnosis AI — v1 Development Plan

## Objective
Build a **RAG-based diagnostic AI agent** that provides **exact, manual-backed diagnoses and repair guidance** for Dell laptops (starting with **Dell Precision 5560**), using **only official service manuals and documentation**, with zero speculative reasoning.

---

## v1 Scope (Strict)
- Single brand: **Dell**
- Single model: **Precision 5560**
- Knowledge source: **Official Dell manuals (PDF)**
- Output style: **Citation-backed, step-by-step**
- Interface: **CLI or simple Web UI**
- No general troubleshooting guesses
- No internet search at inference time

---

## High-Level Architecture (v1)

```
    User Query
    ↓
    Intent + Symptom Extraction
    ↓
    Retriever (Vector Search)
    ↓
    Relevant Manual Chunks
    ↓
    LLM (Constrained Prompt)
    ↓
    Diagnosis + Fix (with citations)

```
---

## Tech Stack (Recommended)

### Environment
- **Conda** (Python 3.11)
- OS: Windows / Linux / macOS

### Core Libraries
- LLM API: OpenAI / Azure OpenAI
- PDF Parsing: PyMuPDF
- Embeddings: OpenAI / SentenceTransformers
- Vector Store: FAISS (local)
- Backend: FastAPI
- UI (optional v1): CLI or Streamlit

---


---

## Phase-by-Phase Execution Plan

---

## Phase 0 — Environment Setup
**Goal:** Stable dev environment

- Create conda environment
- Install core dependencies
- Verify PyMuPDF works

Deliverable:
- Working `import fitz`

---

## Phase 1 — Manual Collection
**Goal:** Authoritative knowledge base

Collect **3–5 official Dell PDFs**:
- Service Manual
- Setup & Specifications
- Technical Specification Sheet
- User Guide

Store in:

```bash
data/raw/
```


Deliverable:
- PDFs verified, versioned, and named clearly

---

## Phase 2 — PDF Ingestion
**Goal:** Clean, structured text extraction

Steps:
1. Load PDFs via PyMuPDF
2. Extract text page-by-page
3. Remove noise (headers, footers, page numbers)
4. Preserve:
   - Section titles
   - Step numbers
   - Warning notes

Output:

```bash
data/processed/
```


Deliverable:
- Clean text files per manual

---

## Phase 3 — Chunking Strategy
**Goal:** Precision retrieval (not semantic mush)

Rules:
- Chunk by **logical section**, not tokens
- Include:
  - Section title
  - Manual name
  - Page number
- Max chunk size: ~500–800 tokens

Output:

```bash
data/chunks/
```


Deliverable:
- JSON chunks with metadata

---

## Phase 4 — Embedding + Indexing
**Goal:** Fast, accurate retrieval

Steps:
1. Generate embeddings for each chunk
2. Store in FAISS index
3. Persist index locally

Deliverable:
- Reusable vector index
- Metadata mapping intact

---

## Phase 5 — Retrieval Layer
**Goal:** Deterministic evidence fetching

Features:
- Top-k semantic retrieval
- Optional keyword filtering
- Confidence scoring

Deliverable:
- Retriever returning relevant manual sections

---

## Phase 6 — Diagnostic Agent (Core Intelligence)
**Goal:** Manual-grounded reasoning

Agent rules:
- Answer **only** using retrieved chunks
- If evidence is insufficient → say so
- Cite:
  - Manual name
  - Section title
  - Page number

Deliverable:
- Diagnosis agent with strict grounding

---

## Phase 7 — API / Interface
**Goal:** Usable system

Options:
- CLI (fastest)
- FastAPI JSON endpoint
- Streamlit UI (optional)

Deliverable:
- User can input symptoms
- Receives cited diagnosis + fix

---

## Guardrails (Non-Negotiable)
- No hallucinated steps
- No general advice
- No internet data at runtime
- No assumptions beyond manuals

---

## v1 Success Criteria
- Correct diagnosis for common hardware issues
- Exact step-by-step instructions
- Source citations on every answer
- Deterministic, repeatable output

---

## v2 Preview (Future)
- Multi-model Dell support
- Agentic workflow (diagnose → verify → repair)
- Image-based issue identification
- Tool-using agents (BIOS checks, logs)

---

## Learning Outcome (You)
By completing v1, you will have hands-on mastery of:
- RAG architecture
- Document ingestion pipelines
- Vector retrieval
- Agentic constraints & grounding
- Production AI system design

---

**Project Codename:** RAGnosis AI  
**Version:** v1 (Foundational)
