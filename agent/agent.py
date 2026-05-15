from __future__ import annotations

import logging

from agent import policy, tools
from rag.answerer import Answer, Answerer
from rag.config import TOP_K
from rag.retriever import Retriever

logger = logging.getLogger(__name__)


class DiagnosticAgent:
    def __init__(
        self,
        retriever: Retriever,
        answerer: Answerer,
        top_k: int = TOP_K,
    ) -> None:
        self._retriever = retriever
        self._answerer = answerer
        self._top_k = top_k

    def run(self, query: str) -> Answer:
        valid, reason = policy.validate_query(query)
        if not valid:
            return policy.build_refusal(reason)

        result = tools.search_manual(query, self._retriever, top_k=self._top_k)

        sufficient, reason = policy.check_retrieval_quality(result.chunks, result.distances)
        if not sufficient:
            return policy.build_refusal(reason)

        # Second-pass: retrieve fix/solution chunks using enriched query
        # so that diagnostic LED code queries also pull in recovery steps
        fix_query = f"{query} fix repair solution recovery steps"
        fix_result = tools.search_manual(fix_query, self._retriever, top_k=self._top_k)

        # Merge, deduplicate by chunk id, filter by relevance threshold
        from rag.config import RELEVANCE_THRESHOLD
        seen_ids: set[str] = {c.get("id", "") for c in result.chunks}
        extra = [
            c for c in fix_result.chunks
            if c.get("id", "") not in seen_ids
            and c.get("distance", 1.0) <= RELEVANCE_THRESHOLD
        ]
        combined_chunks = result.chunks + extra

        answer = self._answerer.answer(query, combined_chunks)

        if not policy.enforce_citation_coverage(answer, combined_chunks):
            logger.warning("Citation coverage check failed for query: %s", query)

        return answer

    def format_for_display(self, answer: Answer) -> str:
        lines: list[str] = []

        if answer.insufficient_evidence:
            lines.append(answer.answer)
            return "\n".join(lines)

        lines.append(answer.answer)
        lines.append("")
        lines.append("**Sources:**")
        seen: set[tuple] = set()
        for c in answer.citations:
            key = (c.manual, c.section, c.page)
            if key not in seen:
                seen.add(key)
                lines.append(f"  - [{c.manual}] {c.section} — Page {c.page}")

        return "\n".join(lines)
