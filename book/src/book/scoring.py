from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .normalization import quality_strength


HIGH_DEMAND_TAGS = {
    "政治哲学",
    "经济思想",
    "历史",
    "思想",
    "社会学",
    "政治经济",
    "哲学",
    "重大事件",
}

MEDIUM_DEMAND_TAGS = {
    "传记",
    "文化",
    "学术",
    "理论",
    "社会",
    "城市研究",
}

TOP_AWARDS = {"诺奖", "茅奖", "布克", "普利策"}


@dataclass
class StructuredScore:
    total: float
    version: float
    author: float
    consensus: float
    theme: float
    market: float
    penalized: bool


def score_version(book: dict[str, Any]) -> float:
    score = 0.0
    if book.get("is_first_edition") and book.get("is_first_print"):
        score += 15
    if book.get("binding") == "hardcover":
        score += 5
    if book.get("is_limited"):
        score += 5
    if book.get("is_signed"):
        score += 5
    return score


def score_author_status(book: dict[str, Any]) -> float:
    score = 0.0
    awards = " ".join(book.get("awards", []))
    if any(tag in awards for tag in TOP_AWARDS):
        score += 10
    keywords = " ".join(book.get("tags", []) + book.get("review_keywords", []))
    if "经典" in keywords or "名著" in keywords:
        score += 8
    if any(tag in keywords for tag in {"政治", "哲学", "思想", "经济"}):
        score += 5
    if book.get("adapted"):
        score += 2
    return score


def score_consensus(consensus_bucket: float) -> float:
    if consensus_bucket <= 0.05:
        return 20
    if consensus_bucket <= 0.10:
        return 15
    if consensus_bucket <= 0.20:
        return 10
    return 5 if consensus_bucket > 0 else 0


def score_theme(book: dict[str, Any]) -> float:
    tags = set(book.get("tags", []))
    if tags & HIGH_DEMAND_TAGS:
        return 15
    if tags & MEDIUM_DEMAND_TAGS:
        return 8
    return 2


def score_market(book: dict[str, Any]) -> float:
    score = 0.0
    stock_status = book.get("stock_status") or ""
    if stock_status in {"out_of_stock", "low_stock", "缺货"}:
        score += 5
    price_list = book.get("price_list")
    price_now = book.get("price_now")
    if price_list and price_now and price_now > price_list * 1.15:
        score += 3
    if book.get("second_hand_premium"):
        score += 2
    return score


def compute_consensus_buckets(merged: list[dict[str, Any]]) -> dict[int, float]:
    values = []
    for idx, item in enumerate(merged):
        douban = item.get("douban") or {}
        rating = douban.get("rating")
        rating_count = douban.get("rating_count")
        values.append((idx, quality_strength(rating, rating_count)))

    sorted_vals = sorted(values, key=lambda x: x[1], reverse=True)
    buckets: dict[int, float] = {}
    total = len(sorted_vals) if sorted_vals else 1
    for rank, (idx, _) in enumerate(sorted_vals, start=1):
        percentile = rank / total
        buckets[idx] = percentile
    return buckets


def score_structured(book: dict[str, Any], consensus_bucket: float) -> StructuredScore:
    version_score = score_version(book)
    author_score = score_author_status(book)
    consensus_score = score_consensus(consensus_bucket)
    theme_score = score_theme(book)
    market_score = score_market(book)
    total = version_score + author_score + consensus_score + theme_score + market_score
    penalized = False
    if not (book.get("is_first_edition") and book.get("is_first_print")):
        total *= 0.5
        penalized = True
    total = max(0.0, min(100.0, total))
    return StructuredScore(
        total=round(total, 2),
        version=version_score,
        author=author_score,
        consensus=consensus_score,
        theme=theme_score,
        market=market_score,
        penalized=penalized,
    )
