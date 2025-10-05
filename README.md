# 🧠 RAGnosis AI  
**Retrieval-Augmented Diagnosis for Intelligent Device Troubleshooting**

> _“Where manuals meet intelligence — your laptop’s first-aid AI.”_

---

### 🚀 Overview
**RAGnosis AI** is a Retrieval-Augmented Generation (RAG)–based assistant that diagnoses and guides the repair of laptops using official service manuals and verified troubleshooting data.  
Starting with **Dell** devices, the system retrieves precise instructions from service documentation, LED-code references, and maintenance guides to deliver **accurate, citation-based solutions** — never guesses.

### 🧩 Core Goals
- **Precision:** Ground every answer in official manuals with page-level citations.  
- **Transparency:** Show exactly where information comes from.  
- **Safety:** Never invent solutions beyond verified documentation.  
- **Learning-by-Building:** Designed to explore practical RAG and agentic architectures from scratch.

### ⚙️ Tech Stack (Planned)
| Component | Technology |
|------------|-------------|
| Language | Python |
| Framework | FastAPI / Streamlit |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Store | ChromaDB |
| Reranker | BGE Reranker (optional) |
| Orchestration | Custom Agent + Tool Interface |
| Data Source | Dell Service Manuals (PDF/Text) |

### 🧭 Project Roadmap
1. **Manual Parsing** – Extract and clean Dell service manuals.  
2. **Vector Indexing** – Chunk and embed text for retrieval.  
3. **Hybrid Search** – Combine keyword + semantic matching.  
4. **Grounded Answering** – Generate step-by-step fixes with citations.  
5. **Interactive Agent** – Clarify issues and guide diagnostics conversationally.  
6. **Evaluation** – Measure accuracy, citation coverage, and faithfulness.  
7. **Web UI** – Minimal chat interface for public testing.

---

📘 _RAGnosis AI — turning static manuals into interactive repair intelligence._
