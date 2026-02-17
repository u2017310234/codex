#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from book.io_utils import load_json, save_json
from book.sources.douban import DoubanClient
from book.sources.http_client import HttpClient
from book.sources.jd import DEFAULT_RANK_URLS, JDClient


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch JD/Douban data")
    parser.add_argument("--keyword", type=str, default="精装 首版")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--max-items", type=int, default=20)
    parser.add_argument("--output-dir", type=str, default=str(ROOT / "data"))
    parser.add_argument("--jd-mode", type=str, default="phb", choices=["phb", "search"])
    parser.add_argument("--rank-urls", type=str, default="")
    parser.add_argument("--sleep-min", type=float, default=1.2)
    parser.add_argument("--sleep-max", type=float, default=2.4)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--use-sample", action="store_true")

    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.use_sample:
        jd_sample = load_json(ROOT / "data" / "jd_sample.json")
        douban_sample = load_json(ROOT / "data" / "douban_sample.json")
        save_json(output_dir / "jd_live.json", jd_sample)
        save_json(output_dir / "douban_live.json", douban_sample)
        print("Wrote sample jd_live.json and douban_live.json")
        return 0

    http_client = HttpClient(
        timeout=args.timeout,
        sleep_min=args.sleep_min,
        sleep_max=args.sleep_max,
        max_retries=args.retries,
    )
    jd_client = JDClient(http_client)
    douban_client = DoubanClient(http_client)

    rank_urls = _load_rank_urls(args.rank_urls)
    if args.jd_mode == "search":
        search_items = jd_client.search(args.keyword, pages=args.pages, max_items=args.max_items)
    else:
        search_items = jd_client.fetch_rankings(rank_urls or DEFAULT_RANK_URLS, max_items=args.max_items)
    jd_records = []
    douban_records = []
    for item in search_items:
        sku = item.get("sku")
        if not sku:
            continue
        detail = jd_client.fetch_detail(sku, item.get("jd_url"))
        jd_records.append(detail)
        isbn = detail.get("isbn")
        if isbn:
            douban = douban_client.fetch_by_isbn(isbn)
        else:
            douban = douban_client.search_by_title(detail.get("title", ""), detail.get("author"))
        if douban:
            douban_records.append(douban)

    save_json(output_dir / "jd_live.json", jd_records)
    save_json(output_dir / "douban_live.json", douban_records)
    print(f"Fetched {len(jd_records)} JD records and {len(douban_records)} Douban records")
    return 0


def _load_rank_urls(raw: str) -> list[str]:
    if not raw:
        return []
    path = Path(raw)
    if path.exists():
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        return [line for line in lines if line and not line.startswith("#")]
    return [item.strip() for item in raw.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
