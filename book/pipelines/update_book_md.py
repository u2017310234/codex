#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Update markdown summary for latest book run")
    parser.add_argument("--out-dir", default="book/output", help="output directory containing books_scored.json")
    parser.add_argument("--run-ts", default=None, help="run timestamp in UTC format YYYYMMDD-HHMMSS")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    latest = out_dir / "books_scored.json"
    if not latest.exists():
        raise SystemExit(f"{latest} not found")

    run_ts = args.run_ts or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

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
