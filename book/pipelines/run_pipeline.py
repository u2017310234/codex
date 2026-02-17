#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from book.io_utils import load_json
from book.llm import build_llm_client
from book.pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run book value potential pipeline")
    parser.add_argument("--jd-data", type=str, default=str(ROOT / "data" / "jd_sample.json"))
    parser.add_argument("--douban-data", type=str, default=str(ROOT / "data" / "douban_sample.json"))
    parser.add_argument("--output-dir", type=str, default=str(ROOT / "output"))
    parser.add_argument("--top-pct", type=float, default=0.10)
    parser.add_argument("--max-llm", type=int, default=None)
    parser.add_argument("--mock-llm", action="store_true")
    parser.add_argument("--use-sample", action="store_true", help="Use sample data (default).")

    args = parser.parse_args()
    jd_path = Path(args.jd_data)
    douban_path = Path(args.douban_data)

    jd_records = load_json(jd_path)
    douban_records = load_json(douban_path)
    llm_client = build_llm_client(mock=args.mock_llm)

    summary = run_pipeline(
        jd_records=jd_records,
        douban_records=douban_records,
        output_dir=args.output_dir,
        top_pct=args.top_pct,
        llm_client=llm_client,
        max_llm=args.max_llm,
    )
    print(f"Processed {summary['count']} books, LLM analyzed {summary['top_count']}")
    print(f"Outputs written to: {summary['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
