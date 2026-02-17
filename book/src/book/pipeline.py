from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .io_utils import save_csv, save_json
from .llm import LLMClient, build_llm_client
from .matching import match_records
from .normalization import normalize_douban_record, normalize_jd_record
from .scoring import compute_consensus_buckets, score_structured


def _merge_book(jd: dict[str, Any], douban: dict[str, Any] | None) -> dict[str, Any]:
    merged = {}
    merged.update(jd)
    if douban:
        merged.update(douban)
    return merged


def _llm_payload(book: dict[str, Any], structured_score: float) -> dict[str, Any]:
    return {
        "title": book.get("title"),
        "author": book.get("author"),
        "publisher": book.get("publisher"),
        "isbn": book.get("isbn"),
        "publish_date": book.get("publish_date"),
        "print_info": book.get("print_info"),
        "binding": book.get("binding"),
        "is_limited": book.get("is_limited"),
        "is_signed": book.get("is_signed"),
        "price_list": book.get("price_list"),
        "price_now": book.get("price_now"),
        "stock_status": book.get("stock_status"),
        "rating": book.get("rating"),
        "rating_count": book.get("rating_count"),
        "tags": book.get("tags", []),
        "awards": book.get("awards", []),
        "adapted": book.get("adapted"),
        "review_keywords": book.get("review_keywords", []),
        "author_bio": book.get("author_bio"),
        "structured_score": structured_score,
    }


def _tier_label(score: float) -> str:
    if score >= 80:
        return "高潜力"
    if score >= 60:
        return "可观察"
    return "阅读价值为主"


def run_pipeline(
    jd_records: list[dict[str, Any]],
    douban_records: list[dict[str, Any]],
    output_dir: str,
    top_pct: float = 0.10,
    llm_client: LLMClient | None = None,
    max_llm: int | None = None,
) -> dict[str, Any]:
    jd_norm = [normalize_jd_record(r) for r in jd_records]
    douban_norm = [normalize_douban_record(r) for r in douban_records]
    merged_pairs = match_records(jd_norm, douban_norm)
    buckets = compute_consensus_buckets(merged_pairs)

    books: list[dict[str, Any]] = []
    for idx, item in enumerate(merged_pairs):
        jd = item.get("jd", {})
        douban = item.get("douban") or {}
        merged = _merge_book(jd, douban)
        structured = score_structured(merged, buckets.get(idx, 0.0))
        merged["structured_score"] = structured.total
        merged["structured_components"] = asdict(structured)
        books.append(merged)

    books_sorted = sorted(books, key=lambda x: x.get("structured_score", 0), reverse=True)
    top_count = max(1, int(len(books_sorted) * top_pct)) if books_sorted else 0
    if max_llm is not None:
        top_count = min(top_count, max_llm)

    llm_client = llm_client or build_llm_client(mock=False)
    for idx, book in enumerate(books_sorted):
        llm_result = None
        if idx < top_count:
            payload = _llm_payload(book, book.get("structured_score", 0))
            try:
                llm_result = llm_client.analyze_book(payload)
            except Exception as exc:  # pragma: no cover - safety fallback
                llm_result = None
                book["llm_error"] = str(exc)
        if llm_result:
            book["llm"] = asdict(llm_result)
            structured_adj = max(0.0, min(100.0, book["structured_score"] + llm_result.structured_adjustment))
            llm_classic = llm_result.classic_potential * 10
            llm_era_ip = ((llm_result.era_significance + llm_result.ip_potential) / 2) * 10
            final_score = 0.5 * structured_adj + 0.3 * llm_classic + 0.2 * llm_era_ip
        else:
            structured_adj = book["structured_score"]
            final_score = structured_adj
            book["llm"] = {
                "classic_potential": 0,
                "era_significance": 0,
                "ip_potential": 0,
                "structured_adjustment": 0,
                "confidence": 0,
                "rationale": "",
            }
        book["structured_score_adjusted"] = round(structured_adj, 2)
        book["final_score"] = round(final_score, 2)
        book["tier"] = _tier_label(book["final_score"])

    output_path = output_dir
    rows = [
        {
            "title": b.get("title"),
            "author": b.get("author"),
            "isbn": b.get("isbn"),
            "jd_url": b.get("jd_url"),
            "douban_url": b.get("douban_url"),
            "structured_score": b.get("structured_score"),
            "structured_score_adjusted": b.get("structured_score_adjusted"),
            "final_score": b.get("final_score"),
            "tier": b.get("tier"),
        }
        for b in books_sorted
    ]

    save_json(
        path=__import__("pathlib").Path(output_path) / "books_scored.json",
        data=books_sorted,
    )
    save_csv(
        path=__import__("pathlib").Path(output_path) / "books_scored.csv",
        rows=rows,
    )

    observation_pool = [b for b in books_sorted if b.get("final_score", 0) >= 80]
    save_json(
        path=__import__("pathlib").Path(output_path) / "observation_pool.json",
        data=observation_pool,
    )

    return {
        "count": len(books_sorted),
        "top_count": top_count,
        "output_dir": output_path,
    }
