from __future__ import annotations

import chromadb
from chromadb.config import Settings


class ChromaStore:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "ragnosis_v1",
    ) -> None:
        self._client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {k: v for k, v in c.items() if k != "text"}
            for c in chunks
        ]
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None,
    ) -> list[dict]:
        kwargs: dict = dict(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        if where:
            kwargs["where"] = where

        result = self._collection.query(**kwargs)

        docs = result["documents"][0]
        metas = result["metadatas"][0]
        distances = result["distances"][0]

        merged: list[dict] = []
        for doc, meta, dist in zip(docs, metas, distances):
            item = dict(meta)
            item["text"] = doc
            item["distance"] = dist
            merged.append(item)

        return merged

    def count(self) -> int:
        return self._collection.count()
