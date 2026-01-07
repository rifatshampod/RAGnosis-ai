#!/usr/bin/env python3
"""
pdf_to_text.py
--------------
Extracts page-wise text and headings from PDFs using PyMuPDF (fitz) and writes
JSON Lines files per manual to the output directory.

Output schema per line:
{
  "page": <int, 1-based>,
  "headings": [<str>, ...],   # best-effort heading path for that page
  "text": "<page text>"
}

Heuristics:
- Prefer the document outline (TOC) via doc.get_toc(simple=False) to infer headings.
- If the PDF has no TOC, fall back to a font-size heuristic per page:
  headings are lines composed of spans whose font size is > 1.25 * median
  span size for the page and whose text is shortish (<= 120 chars).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import fitz  # PyMuPDF
except Exception as e:
    print("ERROR: PyMuPDF (fitz) is required. Install with: pip install pymupdf", file=sys.stderr)
    raise


def normalize_whitespace(s: str) -> str:
    return " ".join(s.split())


def extract_page_text(page: "fitz.Page") -> str:
    """
    Extract text in reading order. Blocks->lines->spans with simple ordering.
    """
    blocks = page.get_text("dict").get("blocks", [])
    # sort blocks by y, then x
    blocks_sorted = sorted(blocks, key=lambda b: (b.get("bbox", [0, 0])[1], b.get("bbox", [0, 0])[0]))
    lines_out = []
    for b in blocks_sorted:
        for l in b.get("lines", []):
            # concatenate spans
            spans_text = "".join(s.get("text", "") for s in l.get("spans", []))
            if spans_text.strip():
                lines_out.append(spans_text.rstrip())
        # blank line between blocks to preserve structure
        if lines_out and lines_out[-1] != "":
            lines_out.append("")
    # remove trailing blank
    if lines_out and lines_out[-1] == "":
        lines_out.pop()
    return "\n".join(lines_out)


def build_page_headings_from_toc(doc: "fitz.Document") -> Dict[int, List[str]]:
    """
    Build a mapping of 1-based page number -> heading path using the document TOC.
    Returns empty dict if no TOC found.
    """
    toc = doc.get_toc(simple=False)  # list of dicts: {"level": int, "title": str, "page": int, ...}
    if not toc:
        return {}

    # Sort by (page, level) to process in order
    toc_sorted = sorted(toc, key=lambda e: (e.get("page", 1), e.get("level", 1)))
    page_to_headings: Dict[int, List[str]] = {}
    stack: List[str] = []  # current heading path

    # We will generate heading path for each page range until next TOC entry
    for idx, entry in enumerate(toc_sorted):
        level = int(entry.get("level", 1))
        title = normalize_whitespace(entry.get("title", "").strip())
        start_page = max(1, int(entry.get("page", 1)))
        end_page = int(toc_sorted[idx + 1].get("page", doc.page_count)) - 1 if idx + 1 < len(toc_sorted) else doc.page_count

        # Maintain stack depth = level
        while len(stack) >= level:
            stack.pop()
        stack.append(title)

        # Assign heading path to pages in [start_page, end_page]
        for p in range(start_page, end_page + 1):
            page_to_headings[p] = list(stack)

    return page_to_headings


def infer_headings_by_fontsize(page: "fitz.Page") -> List[str]:
    """
    Fallback: find likely headings on a page by font size.
    Returns up to three lines considered as heading hierarchy for that page.
    """
    data = page.get_text("dict")
    sizes = []
    lines: List[Tuple[float, float, str]] = []  # (y_top, size, text)

    for b in data.get("blocks", []):
        y_top = b.get("bbox", [0, 0, 0, 0])[1]
        for ln in b.get("lines", []):
            # compute a representative size for the line: max span size
            max_span_size = 0.0
            text = "".join(s.get("text", "") for s in ln.get("spans", []))
            text = normalize_whitespace(text)
            if not text:
                continue
            for sp in ln.get("spans", []):
                sz = float(sp.get("size", 0.0))
                sizes.append(sz)
                if sz > max_span_size:
                    max_span_size = sz
            if max_span_size > 0:
                lines.append((y_top, max_span_size, text))

    if not sizes:
        return []
    sizes_sorted = sorted(sizes)
    median = sizes_sorted[len(sizes_sorted)//2]
    threshold = median * 1.25

    # keep short, large-text lines near the top as candidate headings
    candidates = [l for l in lines if l[1] >= threshold and len(l[2]) <= 120]
    candidates.sort(key=lambda t: (t[0], -t[1]))  # top of page first, prefer larger size
    # Deduplicate by text content preserving order
    seen = set()
    dedup = []
    for _, _, txt in candidates:
        if txt not in seen:
            seen.add(txt)
            dedup.append(txt)
        if len(dedup) >= 3:
            break
    return dedup


def process_pdf(pdf_path: Path, out_dir: Path) -> Path:
    doc = fitz.open(pdf_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (pdf_path.stem + ".jsonl")

    page_headings_map = build_page_headings_from_toc(doc)

    with out_path.open("w", encoding="utf-8") as f:
        for i in range(doc.page_count):
            page_no = i + 1  # 1-based
            page = doc.load_page(i)
            text = extract_page_text(page)

            # headings from TOC or fallback
            headings = page_headings_map.get(page_no)
            if not headings:
                headings = infer_headings_by_fontsize(page)

            record = {
                "page": page_no,
                "headings": headings or [],
                "text": text,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    doc.close()
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Extract text + headings from PDFs into JSONL.")
    parser.add_argument("--input", "-i", type=str, default="data/raw", help="Directory containing input PDFs")
    parser.add_argument("--output", "-o", type=str, default="processed", help="Directory to write JSONL files")
    parser.add_argument("--glob", "-g", type=str, default="*.pdf", help="Glob pattern for PDFs (default: *.pdf)")
    args = parser.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)

    if not in_dir.exists():
        print(f"ERROR: input directory does not exist: {in_dir}", file=sys.stderr)
        sys.exit(1)

    pdfs = sorted(in_dir.glob(args.glob))
    if not pdfs:
        print(f"No PDFs found in {in_dir} matching '{args.glob}'.", file=sys.stderr)
        sys.exit(2)

    print(f"Found {len(pdfs)} PDF(s). Writing JSONL to {out_dir.resolve()}")
    for p in pdfs:
        print(f"- Processing {p.name} ...", flush=True)
        out_path = process_pdf(p, out_dir)
        print(f"  -> {out_path.name}")

    print("Done.")


if __name__ == "__main__":
    main()
