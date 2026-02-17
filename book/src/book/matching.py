from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

from .normalization import normalize_text


def _composite_key(title: str, author: str, publisher: str | None) -> str:
    parts = [normalize_text(title), normalize_text(author), normalize_text(publisher or "")]
    return "::".join(parts)


def _title_author_key(title: str, author: str) -> str:
    return "::".join([normalize_text(title), normalize_text(author)])


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def match_records(jd_records: list[dict[str, Any]], douban_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_isbn: dict[str, dict[str, Any]] = {}
    by_key: dict[str, dict[str, Any]] = {}
    for record in douban_records:
        isbn = record.get("isbn")
        if isbn:
            by_isbn[isbn] = record
        key = _composite_key(record.get("title", ""), record.get("author", ""), "")
        by_key[key] = record

    merged: list[dict[str, Any]] = []
    for jd in jd_records:
        isbn = jd.get("isbn")
        douban = None
        if isbn and isbn in by_isbn:
            douban = by_isbn[isbn]
        else:
            key = _composite_key(jd.get("title", ""), jd.get("author", ""), jd.get("publisher"))
            douban = by_key.get(key)
            if not douban:
                candidate_key = _title_author_key(jd.get("title", ""), jd.get("author", ""))
                best = None
                best_score = 0.0
                for d in douban_records:
                    cand = _title_author_key(d.get("title", ""), d.get("author", ""))
                    score = _similar(candidate_key, cand)
                    if score > best_score:
                        best_score = score
                        best = d
                if best_score >= 0.86:
                    douban = best

        merged.append({
            "jd": jd,
            "douban": douban,
        })
    return merged
