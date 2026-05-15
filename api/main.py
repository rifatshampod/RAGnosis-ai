from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.agent import DiagnosticAgent
from rag.answerer import Answerer, Citation
from rag.config import CHROMA_HOST, CHROMA_PORT, COLLECTION_NAME, EMBED_MODEL, TOP_K
from rag.retriever import Retriever
from rag.vectorstore import ChromaStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = ChromaStore(host=CHROMA_HOST, port=CHROMA_PORT, collection_name=COLLECTION_NAME)
    retriever = Retriever(store, top_k=TOP_K)
    answerer = Answerer()
    app.state.agent = DiagnosticAgent(retriever, answerer, top_k=TOP_K)
    app.state.store = store
    yield


app = FastAPI(title="RAGnosis AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    top_k: int = TOP_K


class CitationOut(BaseModel):
    manual: str
    section: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationOut]
    insufficient_evidence: bool
    model: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    agent: DiagnosticAgent = app.state.agent
    result = agent.run(req.query)
    return ChatResponse(
        answer=result.answer,
        citations=[
            CitationOut(manual=c.manual, section=c.section, page=c.page)
            for c in result.citations
        ],
        insufficient_evidence=result.insufficient_evidence,
        model=result.model,
    )


@app.get("/health")
async def health() -> dict:
    store: ChromaStore = app.state.store
    try:
        count = store.count()
    except Exception:
        count = -1
    return {
        "status": "ok",
        "chunks_indexed": count,
        "embed_model": EMBED_MODEL,
    }
