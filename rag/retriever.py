from __future__ import annotations

from rag.config import EMBED_MODEL, RELEVANCE_THRESHOLD, TOP_K
from rag.embeddings import embed_query
from rag.vectorstore import ChromaStore


class Retriever:
    def __init__(
        self,
        store: ChromaStore,
        embed_model: str = EMBED_MODEL,
        top_k: int = TOP_K,
    ) -> None:
        self._store = store
        self._embed_model = embed_model
        self._top_k = top_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        manual_filter: str | None = None,
    ) -> list[dict]:
        k = top_k if top_k is not None else self._top_k
        vec = embed_query(query, model_name=self._embed_model)
        where = {"manual": manual_filter} if manual_filter else None
        return self._store.query(vec, n_results=k, where=where)

    def retrieve_with_scores(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[tuple[dict, float]]:
        chunks = self.retrieve(query, top_k=top_k)
        return [(c, c.get("distance", RELEVANCE_THRESHOLD)) for c in chunks]
