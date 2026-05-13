"""
build_index.py
--------------
Loads chunk JSON files, generates embeddings, and populates ChromaDB.
Run once after chunking. Use --force to re-index from scratch.
"""

import argparse
import json
import sys
from pathlib import Path

from tqdm import tqdm

from rag.config import (
    CHROMA_HOST,
    CHROMA_PORT,
    CHUNKS_DIR,
    COLLECTION_NAME,
    EMBED_MODEL,
)
from rag.embeddings import embed_texts
from rag.vectorstore import ChromaStore


def load_chunks(chunks_dir: Path) -> list[dict]:
    all_chunks: list[dict] = []
    json_files = sorted(chunks_dir.glob("*.json"))
    if not json_files:
        print(f"No chunk JSON files found in {chunks_dir}", file=sys.stderr)
        return all_chunks

    for jf in json_files:
        with jf.open(encoding="utf-8") as f:
            data = json.load(f)
        print(f"  Loaded {len(data):>5} chunks from {jf.name}")
        all_chunks.extend(data)

    return all_chunks


def embed_in_batches(chunks: list[dict], batch_size: int = 128) -> list[list[float]]:
    texts = [c["text"] for c in chunks]
    all_vecs: list[list[float]] = []

    for start in tqdm(range(0, len(texts), batch_size), desc="Embedding", unit="batch"):
        batch = texts[start : start + batch_size]
        vecs = embed_texts(batch, model_name=EMBED_MODEL, batch_size=batch_size)
        all_vecs.extend(vecs)

    return all_vecs


def build(chunks_dir: Path, batch_size: int = 128, force: bool = False) -> None:
    print(f"Loading chunks from {chunks_dir}...")
    chunks = load_chunks(chunks_dir)
    if not chunks:
        print("No chunks to index. Run chunker.py first.", file=sys.stderr)
        sys.exit(1)
    print(f"Total chunks: {len(chunks):,}")

    store = ChromaStore(host=CHROMA_HOST, port=CHROMA_PORT, collection_name=COLLECTION_NAME)
    existing = store.count()

    if existing > 0 and not force:
        print(
            f"ChromaDB already has {existing:,} documents. "
            "Use --force to re-index.",
            file=sys.stderr,
        )
        sys.exit(0)

    if existing > 0 and force:
        print(f"--force set. Dropping existing {existing:,} documents and re-indexing.")
        store._client.delete_collection(COLLECTION_NAME)
        store._collection = store._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    print(f"Generating embeddings with {EMBED_MODEL}...")
    embeddings = embed_in_batches(chunks, batch_size)

    print("Adding to ChromaDB...")
    batch_size_add = 500
    for start in tqdm(range(0, len(chunks), batch_size_add), desc="Indexing", unit="batch"):
        store.add_chunks(chunks[start : start + batch_size_add], embeddings[start : start + batch_size_add])

    final_count = store.count()
    print(f"Done. ChromaDB now has {final_count:,} documents.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed chunks and build ChromaDB index.")
    parser.add_argument("--chunks", default=str(CHUNKS_DIR), help="Directory of chunk JSON files")
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--force", action="store_true", help="Drop existing index and re-index")
    args = parser.parse_args()

    build(Path(args.chunks), args.batch_size, args.force)


if __name__ == "__main__":
    main()
