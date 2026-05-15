from __future__ import annotations

from dataclasses import dataclass, field

from rag.retriever import Retriever


@dataclass
class ToolResult:
    chunks: list[dict] = field(default_factory=list)
    distances: list[float] = field(default_factory=list)
    query_used: str = ""


def search_manual(
    query: str,
    retriever: Retriever,
    top_k: int = 5,
    manual_filter: str | None = None,
) -> ToolResult:
    results_with_scores = retriever.retrieve_with_scores(query, top_k=top_k)
    chunks = [r[0] for r in results_with_scores]
    distances = [r[1] for r in results_with_scores]
    return ToolResult(chunks=chunks, distances=distances, query_used=query)


TOOL_REGISTRY: dict[str, object] = {
    "search_manual": search_manual,
}
