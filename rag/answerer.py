from __future__ import annotations

import re
import time

from openai import OpenAI, RateLimitError
from pydantic import BaseModel

from rag.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL
from rag.prompt import build_messages

_CITATION_RE = re.compile(
    r"\[Manual:\s*(.+?),\s*Section:\s*(.+?),\s*Page:\s*(\d+)\]",
    re.IGNORECASE,
)


class Citation(BaseModel):
    manual: str
    section: str
    page: int


class Answer(BaseModel):
    query: str
    answer: str
    citations: list[Citation]
    chunks_used: int
    model: str
    insufficient_evidence: bool


class Answerer:
    def __init__(
        self,
        model: str = OPENROUTER_MODEL,
        temperature: float = 0.0,
    ) -> None:
        self._model = model
        self._temperature = temperature
        self._client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )

    def answer(self, query: str, chunks: list[dict]) -> Answer:
        messages = build_messages(query, chunks)
        response = None
        for attempt in range(3):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    temperature=self._temperature,
                )
                break
            except RateLimitError:
                if attempt == 2:
                    raise
                time.sleep(25)
        text = response.choices[0].message.content or ""

        insufficient = "INSUFFICIENT_EVIDENCE" in text

        citations = _parse_citations(text, chunks)

        return Answer(
            query=query,
            answer=text,
            citations=citations,
            chunks_used=len(chunks),
            model=self._model,
            insufficient_evidence=insufficient,
        )


def _parse_citations(text: str, chunks: list[dict]) -> list[Citation]:
    found: list[Citation] = []
    seen: set[tuple] = set()

    for m in _CITATION_RE.finditer(text):
        manual = m.group(1).strip()
        section = m.group(2).strip()
        page = int(m.group(3))
        key = (manual, section, page)
        if key not in seen:
            seen.add(key)
            found.append(Citation(manual=manual, section=section, page=page))

    if not found:
        for chunk in chunks:
            key = (chunk.get("manual", ""), chunk.get("section", ""), chunk.get("page", 0))
            if key not in seen:
                seen.add(key)
                found.append(Citation(
                    manual=chunk.get("manual", "unknown"),
                    section=chunk.get("section", "unknown"),
                    page=int(chunk.get("page", 0)),
                ))

    return found
