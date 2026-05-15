from __future__ import annotations

import re

from rag.answerer import Answer, Citation
from rag.config import RELEVANCE_THRESHOLD

_INJECTION_PATTERNS = re.compile(
    r"(ignore (previous|all|above|prior)|disregard|forget (the|your)|"
    r"you are now|act as|pretend (you are|to be)|new instructions)",
    re.IGNORECASE,
)


def validate_query(query: str) -> tuple[bool, str]:
    if not query or not query.strip():
        return False, "Query is empty."
    if len(query.strip()) < 10:
        return False, "Query is too short to be a diagnostic question."
    if _INJECTION_PATTERNS.search(query):
        return False, "Query contains disallowed patterns."
    return True, ""


def check_retrieval_quality(
    chunks: list[dict],
    distances: list[float],
    threshold: float = RELEVANCE_THRESHOLD,
) -> tuple[bool, str]:
    if not chunks:
        return False, "No relevant manual sections found for this query."
    relevant = [d for d in distances if d <= threshold]
    if not relevant:
        return False, "Retrieved sections are not sufficiently relevant to the query."
    return True, ""


def enforce_citation_coverage(answer: Answer, chunks: list[dict]) -> bool:
    chunk_pages = {c.get("page") for c in chunks}
    for citation in answer.citations:
        if citation.page not in chunk_pages:
            return False
    return True


def build_refusal(reason: str) -> Answer:
    return Answer(
        query="",
        answer=(
            f"I cannot answer this question from the available Dell Precision 5560 manuals. "
            f"Reason: {reason}"
        ),
        citations=[],
        chunks_used=0,
        model="none",
        insufficient_evidence=True,
    )
