#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    out_dir = Path("output/book")
    json_files = sorted(out_dir.glob("books_scored_*.json"), reverse=True)
    if not json_files:
        raise SystemExit("no books_scored_*.json found")
    latest = json_files[0]
    run_ts = latest.stem.split("books_scored_")[-1]

    books = json.loads(latest.read_text(encoding="utf-8"))
    lines = []
    for b in books:
        title = b.get("title") or ""
        score = b.get("final_score")
        llm = (b.get("llm") or {}).get("rationale") or ""
        lines.append(f"- {title} | {run_ts} | {score} | {llm}")

    md_path = out_dir / "book.md"
    existing = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
    header = "# Book Runs\n\n"
    new_block = "\n".join(lines) + "\n\n"
    md_path.write_text(header + new_block + existing.replace(header, ""), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
