"""
chunker.py
----------
Reads page-level JSONL files from data/processed/ and produces section-level
chunk JSON files in data/chunks/.

Each chunk groups consecutive pages sharing the same heading path. Chunks
exceeding MAX_CHUNK_TOKENS are split at sentence boundaries. A small token
overlap is prepended to each chunk from the previous chunk's tail.
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        return len(_enc.encode(text))

except Exception:
    def count_tokens(text: str) -> int:
        return int(len(text.split()) * 1.3)


def _sentence_split(text: str) -> list[str]:
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\(])', text)
    return [p for p in parts if p.strip()]


def split_at_sentence(text: str, max_tokens: int) -> list[str]:
    if count_tokens(text) <= max_tokens:
        return [text]

    sentences = _sentence_split(text)
    if len(sentences) <= 1:
        words = text.split()
        mid = len(words) // 2
        return split_at_sentence(" ".join(words[:mid]), max_tokens) + \
               split_at_sentence(" ".join(words[mid:]), max_tokens)

    chunks: list[str] = []
    buf: list[str] = []
    buf_tokens = 0

    for sent in sentences:
        st = count_tokens(sent)
        if buf_tokens + st > max_tokens and buf:
            chunks.append(" ".join(buf))
            buf = []
            buf_tokens = 0
        buf.append(sent)
        buf_tokens += st

    if buf:
        chunks.append(" ".join(buf))

    return chunks


def _tail_tokens(text: str, n: int) -> str:
    words = text.split()
    approx_words = max(1, int(n / 1.3))
    return " ".join(words[-approx_words:])


def chunk_jsonl(
    records: list[dict],
    manual_stem: str,
    max_tokens: int = 600,
    overlap_tokens: int = 50,
) -> list[dict]:
    chunks: list[dict] = []
    chunk_idx = 0
    overlap_text = ""

    i = 0
    while i < len(records):
        rec = records[i]
        if not rec.get("text", "").strip():
            i += 1
            continue

        heading_key = tuple(rec.get("headings") or [])
        section_label = " > ".join(rec["headings"]) if rec.get("headings") else "Unknown"
        first_page = rec["page"]
        buf_parts: list[str] = []
        if overlap_text:
            buf_parts.append(overlap_text)

        while i < len(records):
            r = records[i]
            if not r.get("text", "").strip():
                i += 1
                continue
            if tuple(r.get("headings") or []) != heading_key and buf_parts:
                break

            heading_key = tuple(r.get("headings") or [])
            section_label = " > ".join(r["headings"]) if r.get("headings") else "Unknown"

            buf_parts.append(r["text"].strip())
            i += 1

        combined = "\n\n".join(buf_parts)
        sub_texts = split_at_sentence(combined, max_tokens)

        for sub in sub_texts:
            sub = sub.strip()
            if not sub:
                continue
            chunk_id = f"{manual_stem}-p{first_page}-c{chunk_idx}"
            chunks.append({
                "id": chunk_id,
                "manual": manual_stem,
                "section": section_label,
                "page": first_page,
                "text": sub,
                "token_count": count_tokens(sub),
            })
            chunk_idx += 1

        if combined.strip():
            overlap_text = _tail_tokens(combined, overlap_tokens)
        else:
            overlap_text = ""

    return chunks


def process_all(processed_dir: Path, chunks_dir: Path, max_tokens: int = 600, overlap_tokens: int = 50) -> None:
    chunks_dir.mkdir(parents=True, exist_ok=True)
    jsonl_files = sorted(processed_dir.glob("*.jsonl"))

    if not jsonl_files:
        print(f"No JSONL files found in {processed_dir}", file=sys.stderr)
        return

    for jf in jsonl_files:
        records: list[dict] = []
        with jf.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

        records.sort(key=lambda r: r.get("page", 0))
        manual_stem = jf.stem
        print(f"Chunking {jf.name} ({len(records)} pages)...", flush=True)

        chunks = chunk_jsonl(records, manual_stem, max_tokens, overlap_tokens)

        out_path = chunks_dir / f"{manual_stem}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

        total_tokens = sum(c["token_count"] for c in chunks)
        print(f"  -> {len(chunks)} chunks, ~{total_tokens:,} tokens total -> {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk processed JSONL files into section-level JSON chunks.")
    parser.add_argument("--processed", "-p", default="data/processed", help="Directory of JSONL files")
    parser.add_argument("--chunks", "-c", default="data/chunks", help="Output directory for JSON chunks")
    parser.add_argument("--max-tokens", type=int, default=600)
    parser.add_argument("--overlap-tokens", type=int, default=50)
    args = parser.parse_args()

    process_all(
        Path(args.processed),
        Path(args.chunks),
        args.max_tokens,
        args.overlap_tokens,
    )
    print("Chunking complete.")


if __name__ == "__main__":
    main()
