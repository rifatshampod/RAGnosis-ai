"""
run_pipeline.py
---------------
Orchestrates the full ingest pipeline:
  1. PDF → JSONL  (pdf_to_text.py)
  2. JSONL → JSON chunks  (chunker.py)
  3. JSON chunks → ChromaDB  (build_index.py)

This is the Docker CMD entrypoint for the ingest service.
"""

import argparse
import sys
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
CHUNKS_DIR = Path("data/chunks")


def run_step(name: str, fn, *args, **kwargs) -> None:
    print(f"\n{'='*60}")
    print(f"STEP: {name}")
    print(f"{'='*60}")
    try:
        fn(*args, **kwargs)
    except SystemExit as e:
        if e.code not in (0, None):
            print(f"ERROR: {name} failed with exit code {e.code}", file=sys.stderr)
            sys.exit(e.code)
    except Exception as e:
        print(f"ERROR: {name} failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full RAGnosis ingest pipeline.")
    parser.add_argument("--raw", default=str(RAW_DIR))
    parser.add_argument("--processed", default=str(PROCESSED_DIR))
    parser.add_argument("--chunks", default=str(CHUNKS_DIR))
    parser.add_argument("--force", action="store_true", help="Force re-index even if ChromaDB already has data")
    args = parser.parse_args()

    raw_dir = Path(args.raw)
    processed_dir = Path(args.processed)
    chunks_dir = Path(args.chunks)

    # Step 1: PDF extraction
    from ingest.pdf_to_text import process_pdf
    from ingest.chunker import process_all as chunk_all
    from ingest.build_index import build

    def extract_pdfs():
        processed_dir.mkdir(parents=True, exist_ok=True)
        pdfs = sorted(raw_dir.glob("*.pdf"))
        if not pdfs:
            print(f"No PDFs found in {raw_dir}", file=sys.stderr)
            sys.exit(1)
        print(f"Found {len(pdfs)} PDF(s)")
        for p in pdfs:
            print(f"  Processing {p.name}...")
            out = process_pdf(p, processed_dir)
            print(f"    -> {out.name}")

    run_step("PDF Extraction", extract_pdfs)
    run_step("Chunking", chunk_all, processed_dir, chunks_dir)
    run_step("Building Index", build, chunks_dir, 128, args.force)

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
