from __future__ import annotations

import math
import re
from typing import Any


_BINDING_MAP = {
    "精装": "hardcover",
    "平装": "paperback",
    "hardcover": "hardcover",
    "paperback": "paperback",
}


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "是", "有", "t"}


def parse_price(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        text = re.sub(r"[^0-9.]", "", str(value))
        return float(text) if text else None


def normalize_binding(value: Any) -> str | None:
    if value is None:
        return None
    text = normalize_text(str(value))
    return _BINDING_MAP.get(text, text)


def parse_print_info(print_info: Any) -> tuple[bool, bool]:
    if not print_info:
        return False, False
    text = str(print_info)
    is_first_edition = bool(re.search(r"首版|一版", text))
    is_first_print = bool(re.search(r"首印|一印", text))
    if "首版首印" in text or "一版一印" in text:
        is_first_edition = True
        is_first_print = True
    return is_first_edition, is_first_print


def normalize_jd_record(record: dict[str, Any]) -> dict[str, Any]:
    is_first_edition, is_first_print = parse_print_info(record.get("print_info"))
    return {
        "title": str(record.get("title", "")).strip(),
        "author": str(record.get("author", "")).strip(),
        "publisher": str(record.get("publisher", "")).strip(),
        "publish_date": record.get("publish_date"),
        "print_info": record.get("print_info"),
        "isbn": str(record.get("isbn", "")).strip() or None,
        "binding": normalize_binding(record.get("binding")),
        "is_first_edition": is_first_edition,
        "is_first_print": is_first_print,
        "is_limited": parse_bool(record.get("is_limited")),
        "is_signed": parse_bool(record.get("is_signed")),
        "price_list": parse_price(record.get("price_list")),
        "price_now": parse_price(record.get("price_now")),
        "stock_status": normalize_text(record.get("stock_status")) or None,
        "listing_date": record.get("listing_date"),
        "jd_url": record.get("jd_url"),
        "second_hand_premium": parse_bool(record.get("second_hand_premium"))
        if record.get("second_hand_premium") is not None
        else None,
    }


def normalize_douban_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": str(record.get("title", "")).strip(),
        "author": str(record.get("author", "")).strip(),
        "isbn": str(record.get("isbn", "")).strip() or None,
        "rating": float(record.get("rating")) if record.get("rating") is not None else None,
        "rating_count": int(record.get("rating_count")) if record.get("rating_count") is not None else 0,
        "tags": list(record.get("tags") or []),
        "awards": list(record.get("awards") or []),
        "adapted": parse_bool(record.get("adapted")),
        "review_keywords": list(record.get("review_keywords") or []),
        "author_bio": record.get("author_bio") or "",
    }


def quality_strength(rating: float | None, rating_count: int | None) -> float:
    if not rating or not rating_count or rating_count <= 0:
        return 0.0
    return float(rating) * math.log(rating_count)
