#!/usr/bin/env python3
"""
Fetch and filter active Polymarket markets for finance-related questions.

Capabilities:
- Offline input via --input
- Local cache read/write
- Live API fetch with pagination
- Optional DeepL translation
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib import error, parse, request


DEFAULT_API_URL = "https://gamma-api.polymarket.com/markets"
DEFAULT_CACHE_PATH = ".cache/polymarket_markets.json"
DEFAULT_CACHE_TTL = 900
DEFAULT_LIMIT = 20
DEFAULT_REQUEST_TIMEOUT = 20
DEFAULT_TRANSLATE_ENDPOINT = "https://api-free.deepl.com/v2/translate"
USER_AGENT = "polymarket-finance-questions/1.0 (+https://github.com)"

# Broad finance vocabulary used as baseline relevance filter.
DEFAULT_FINANCE_TERMS = [
    "finance",
    "financial",
    "macro",
    "economy",
    "economic",
    "inflation",
    "deflation",
    "recession",
    "gdp",
    "rates",
    "rate cut",
    "rate hike",
    "federal reserve",
    "fed",
    "ecb",
    "boj",
    "stocks",
    "equities",
    "s&p",
    "nasdaq",
    "dow",
    "earnings",
    "crypto",
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "solana",
    "commodities",
    "gold",
    "silver",
    "oil",
    "brent",
    "wti",
    "forex",
    "fx",
    "usd",
    "bond",
    "treasury",
]

DEFAULT_MACRO_TERMS = [
    "macro",
    "economy",
    "economic",
    "gdp",
    "inflation",
    "deflation",
    "recession",
    "federal reserve",
    "fed",
    "ecb",
    "boj",
    "interest rate",
    "rate cut",
    "rate hike",
    "cpi",
    "ppi",
    "unemployment",
    "nonfarm payroll",
    "yield",
    "treasury",
]

DEFAULT_MICRO_TERMS = [
    "stock",
    "stocks",
    "equity",
    "equities",
    "share",
    "shares",
    "earnings",
    "revenue",
    "guidance",
    "eps",
    "ipo",
    "merger",
    "acquisition",
    "buyout",
    "valuation",
    "market cap",
    "company",
    "corporate",
    "bankruptcy",
    "default",
    "tesla",
    "apple",
    "nvidia",
    "microsoft",
    "amazon",
    "meta",
    "netflix",
    "google",
    "btc",
    "bitcoin",
    "eth",
    "ethereum",
    "solana",
    "gold",
    "silver",
    "oil",
]

DEFAULT_DEDUP_STOPWORDS = {
    "will",
    "there",
    "be",
    "by",
    "before",
    "after",
    "in",
    "on",
    "at",
    "to",
    "of",
    "the",
    "a",
    "an",
    "and",
    "or",
    "for",
    "with",
    "from",
    "this",
    "that",
    "is",
    "are",
    "was",
    "were",
    "it",
    "its",
    "as",
    "than",
    "over",
    "under",
    "above",
    "below",
    "between",
    "meeting",
    "quarter",
    "q1",
    "q2",
    "q3",
    "q4",
    "jan",
    "january",
    "feb",
    "february",
    "mar",
    "march",
    "apr",
    "april",
    "may",
    "jun",
    "june",
    "jul",
    "july",
    "aug",
    "august",
    "sep",
    "september",
    "oct",
    "october",
    "nov",
    "november",
    "dec",
    "december",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and filter active Polymarket finance questions."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Max number of questions to return.",
    )
    parser.add_argument(
        "--keywords",
        action="append",
        default=[],
        help="Comma-separated or repeatable keyword filter.",
    )
    parser.add_argument(
        "--exclude-keywords",
        action="append",
        default=[],
        help="Comma-separated or repeatable keyword exclusion filter.",
    )
    parser.add_argument(
        "--focus",
        choices=["all", "macro", "micro"],
        default="all",
        help="Finance focus mode.",
    )
    parser.add_argument(
        "--tags",
        action="append",
        default=[],
        help="Comma-separated or repeatable tag filter.",
    )
    parser.add_argument(
        "--sort",
        choices=["volume", "endDate", "none"],
        default="volume",
        help="Sort mode.",
    )
    parser.add_argument(
        "--dedup-mode",
        choices=["none", "exact", "fuzzy", "coarse"],
        default="fuzzy",
        help="Deduplication mode for similar titles.",
    )
    parser.add_argument(
        "--dedup-threshold",
        type=float,
        default=0.82,
        help="Fuzzy dedup Jaccard threshold in [0,1].",
    )
    parser.add_argument(
        "--input",
        help="Path to local JSON input file (offline mode).",
    )
    parser.add_argument(
        "--cache-ttl",
        type=int,
        default=DEFAULT_CACHE_TTL,
        help="Cache time-to-live in seconds.",
    )
    parser.add_argument(
        "--cache-path",
        default=DEFAULT_CACHE_PATH,
        help="Cache file path.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable cache read and write.",
    )
    parser.add_argument(
        "--translate",
        action="store_true",
        help="Enable optional title translation.",
    )
    parser.add_argument(
        "--translate-provider",
        default="deepl",
        help="Translation provider (currently supports deepl).",
    )
    parser.add_argument(
        "--translate-to",
        default="ZH",
        help="Target translation language code.",
    )
    parser.add_argument(
        "--translate-endpoint",
        help="Override translation API endpoint.",
    )
    parser.add_argument(
        "--translate-api-key",
        help="Override translation API key.",
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help="Polymarket API endpoint.",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=DEFAULT_REQUEST_TIMEOUT,
        help="HTTP request timeout in seconds.",
    )
    return parser.parse_args()


def parse_csv_list(values: Sequence[str]) -> List[str]:
    items: List[str] = []
    seen = set()
    for raw in values:
        for part in str(raw).split(","):
            item = part.strip().lower()
            if not item or item in seen:
                continue
            seen.add(item)
            items.append(item)
    return items


def safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if isinstance(value, str):
            cleaned = value.strip().replace(",", "")
            if not cleaned:
                return None
            return float(cleaned)
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
    return None


def parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 1_000_000_000_000:
            timestamp /= 1000.0
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if raw.isdigit():
            return parse_datetime(int(raw))
        normalized = raw.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
    return None


def normalize_end_date(value: Any) -> Optional[str]:
    dt = parse_datetime(value)
    if not dt:
        return None
    return dt.date().isoformat()


def request_json(url: str, timeout: int) -> Any:
    req = request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            body = resp.read().decode(charset, errors="replace")
            return json.loads(body)
    except error.HTTPError as exc:
        snippet = exc.read(200).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {snippet}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error for {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from {url}: {exc}") from exc


def extract_markets(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        candidates: List[Any] = []
        for key in ("markets", "data", "items", "results"):
            if key in payload:
                candidates.append(payload[key])

        for value in candidates:
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                for nested_key in ("markets", "items", "results"):
                    nested = value.get(nested_key)
                    if isinstance(nested, list):
                        return [item for item in nested if isinstance(item, dict)]

        if all(k in payload for k in ("question", "title")) or "question" in payload:
            return [payload]

    return []


def fetch_live_markets(api_url: str, timeout: int) -> List[Dict[str, Any]]:
    page_size = 500
    max_pages = 20
    collected: List[Dict[str, Any]] = []
    seen_keys = set()

    for page_index in range(max_pages):
        offset = page_index * page_size
        query = parse.urlencode(
            {
                "limit": page_size,
                "offset": offset,
                "active": "true",
                "closed": "false",
                "archived": "false",
            }
        )
        page_url = f"{api_url}?{query}"
        payload = request_json(page_url, timeout=timeout)
        chunk = extract_markets(payload)
        if not chunk:
            break

        new_items = 0
        for index, market in enumerate(chunk):
            dedupe_key = (
                safe_str(market.get("id"))
                or safe_str(market.get("conditionId"))
                or safe_str(market.get("slug"))
                or f"{offset}:{index}"
            )
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)
            collected.append(market)
            new_items += 1

        if len(chunk) < page_size or new_items == 0:
            break

    if collected:
        return collected

    fallback_payload = request_json(api_url, timeout=timeout)
    fallback_markets = extract_markets(fallback_payload)
    if fallback_markets:
        return fallback_markets

    raise RuntimeError("No market records found from live API.")


def load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_input_markets(input_path: str) -> List[Dict[str, Any]]:
    path = Path(input_path)
    if not path.exists():
        raise RuntimeError(f"Input file not found: {path}")
    payload = load_json_file(path)
    markets = extract_markets(payload)
    if not markets:
        raise RuntimeError(f"No market records found in input file: {path}")
    return markets


def load_cache_payload(cache_path: str, warnings: List[str]) -> Optional[Dict[str, Any]]:
    path = Path(cache_path)
    if not path.exists():
        return None
    try:
        payload = load_json_file(path)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        warnings.append(f"cache read failed ({path}): {exc}")
        return None
    if not isinstance(payload, dict):
        warnings.append(f"cache payload must be a JSON object: {path}")
        return None
    return payload


def save_cache_payload(
    cache_path: str,
    api_url: str,
    markets: List[Dict[str, Any]],
    warnings: List[str],
) -> None:
    path = Path(cache_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "fetchedAt": int(time.time()),
            "apiUrl": api_url,
            "markets": markets,
        }
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        warnings.append(f"cache write failed ({path}): {exc}")


def market_url(market: Dict[str, Any]) -> Optional[str]:
    direct = safe_str(market.get("url") or market.get("marketUrl"))
    if direct:
        if direct.startswith("http://") or direct.startswith("https://"):
            return direct
        return f"https://polymarket.com{direct if direct.startswith('/') else '/' + direct}"

    slug = safe_str(market.get("slug") or market.get("marketSlug"))
    if slug:
        return f"https://polymarket.com/market/{slug}"
    return None


def extract_tags(market: Dict[str, Any]) -> List[str]:
    raw_tags = market.get("tags")
    tags: List[str] = []
    seen = set()

    def add_tag(value: Any) -> None:
        text = safe_str(value).lower()
        if not text or text in seen:
            return
        seen.add(text)
        tags.append(text)

    if isinstance(raw_tags, list):
        for item in raw_tags:
            if isinstance(item, dict):
                add_tag(item.get("name"))
                add_tag(item.get("label"))
                add_tag(item.get("slug"))
                add_tag(item.get("title"))
            else:
                add_tag(item)
    elif isinstance(raw_tags, str):
        for piece in raw_tags.split(","):
            add_tag(piece)

    for key in ("category", "subcategory", "groupItemTitle", "marketType"):
        add_tag(market.get(key))

    return tags


def extract_yes_no_prices(market: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    yes = safe_float(market.get("yesPrice"))
    no = safe_float(market.get("noPrice"))
    if yes is not None or no is not None:
        return yes, no

    outcome_prices = market.get("outcomePrices") or market.get("outcome_prices")
    outcomes = market.get("outcomes")

    if isinstance(outcome_prices, str):
        try:
            outcome_prices = json.loads(outcome_prices)
        except json.JSONDecodeError:
            outcome_prices = None

    if isinstance(outcomes, str):
        try:
            outcomes = json.loads(outcomes)
        except json.JSONDecodeError:
            outcomes = None

    if isinstance(outcome_prices, dict):
        yes = safe_float(
            outcome_prices.get("YES")
            or outcome_prices.get("Yes")
            or outcome_prices.get("yes")
        )
        no = safe_float(
            outcome_prices.get("NO")
            or outcome_prices.get("No")
            or outcome_prices.get("no")
        )
        return yes, no

    prices: List[Optional[float]] = []
    if isinstance(outcome_prices, list):
        prices = [safe_float(value) for value in outcome_prices]

    if isinstance(outcomes, list) and prices and len(outcomes) == len(prices):
        for idx, outcome_name in enumerate(outcomes):
            if isinstance(outcome_name, dict):
                label = safe_str(
                    outcome_name.get("name")
                    or outcome_name.get("title")
                    or outcome_name.get("value")
                )
            else:
                label = safe_str(outcome_name)
            lowered = label.lower()
            if lowered == "yes" and yes is None:
                yes = prices[idx]
            if lowered == "no" and no is None:
                no = prices[idx]

    if prices and len(prices) >= 2:
        if yes is None:
            yes = prices[0]
        if no is None:
            no = prices[1]

    return yes, no


def is_market_active(market: Dict[str, Any]) -> bool:
    if parse_bool(market.get("archived")) is True:
        return False
    if parse_bool(market.get("closed")) is True:
        return False
    if "active" in market and parse_bool(market.get("active")) is False:
        return False
    if "acceptingOrders" in market and parse_bool(market.get("acceptingOrders")) is False:
        return False

    end_value = (
        market.get("endDate")
        or market.get("end_date")
        or market.get("endTime")
        or market.get("endDatetime")
        or market.get("resolveDate")
    )
    end_dt = parse_datetime(end_value)
    if end_dt and end_dt < datetime.now(tz=timezone.utc):
        return False
    return True


def normalize_market(market: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not is_market_active(market):
        return None

    title = (
        safe_str(market.get("question"))
        or safe_str(market.get("title"))
        or safe_str(market.get("name"))
    )
    if not title:
        return None

    tags = extract_tags(market)
    yes_price, no_price = extract_yes_no_prices(market)

    end_value = (
        market.get("endDate")
        or market.get("end_date")
        or market.get("endTime")
        or market.get("endDatetime")
        or market.get("resolveDate")
    )
    end_date = normalize_end_date(end_value)

    volume_24 = safe_float(
        market.get("volume24hr")
        or market.get("volume24h")
        or market.get("volume24Hours")
        or market.get("oneDayVolume")
    )
    volume_total = safe_float(market.get("volume") or market.get("totalVolume"))

    normalized = {
        "title": title,
        "url": market_url(market),
        "category": "finance",
        "endDate": end_date,
        "yesPrice": round(yes_price, 6) if yes_price is not None else None,
        "noPrice": round(no_price, 6) if no_price is not None else None,
        "_tags": tags,
        "_volume24hr": volume_24,
        "_volume": volume_total,
    }
    return normalized


def contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term and term in text for term in terms)


def normalize_title_for_exact(title: str) -> str:
    text = safe_str(title).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def normalize_title_for_coarse(title: str) -> str:
    text = safe_str(title).lower()
    text = re.sub(r'"[^"]*"', " ", text)
    text = re.sub(r"'[^']*'", " ", text)
    text = re.sub(r"\b\d+(?:[.,]\d+)?\+?\b", " ", text)
    text = re.sub(r"[^a-z]+", " ", text)
    tokens = []
    for token in text.split():
        if token in DEFAULT_DEDUP_STOPWORDS:
            continue
        if len(token) <= 1:
            continue
        tokens.append(token)
    return " ".join(tokens)


def title_token_set(title: str) -> set:
    normalized = normalize_title_for_coarse(title)
    tokens = []
    for token in normalized.split():
        tokens.append(token)
    return set(tokens)


def token_jaccard_similarity(left: set, right: set) -> float:
    if not left or not right:
        return 0.0
    union_size = len(left | right)
    if union_size == 0:
        return 0.0
    return len(left & right) / union_size


def deduplicate_questions(
    items: List[Dict[str, Any]],
    mode: str,
    threshold: float,
) -> Tuple[List[Dict[str, Any]], int]:
    if mode == "none":
        return list(items), 0

    if mode == "exact":
        kept: List[Dict[str, Any]] = []
        seen = set()
        removed = 0
        for item in items:
            key = normalize_title_for_exact(safe_str(item.get("title")))
            if key and key in seen:
                removed += 1
                continue
            if key:
                seen.add(key)
            kept.append(item)
        return kept, removed

    if mode == "coarse":
        kept: List[Dict[str, Any]] = []
        seen = set()
        removed = 0
        for item in items:
            key = normalize_title_for_coarse(safe_str(item.get("title")))
            if key and key in seen:
                removed += 1
                continue
            if key:
                seen.add(key)
            kept.append(item)
        return kept, removed

    kept_items: List[Dict[str, Any]] = []
    kept_token_sets: List[set] = []
    removed = 0
    for item in items:
        tokens = title_token_set(safe_str(item.get("title")))
        is_duplicate = False
        for existing_tokens in kept_token_sets:
            if token_jaccard_similarity(tokens, existing_tokens) >= threshold:
                is_duplicate = True
                break
        if is_duplicate:
            removed += 1
            continue
        kept_items.append(item)
        kept_token_sets.append(tokens)
    return kept_items, removed


def is_finance_related(
    market: Dict[str, Any],
    user_tags: Sequence[str],
    user_keywords: Sequence[str],
    excluded_keywords: Sequence[str],
    focus: str,
) -> bool:
    combined = " ".join(
        [
            safe_str(market.get("title")).lower(),
            safe_str(market.get("url")).lower(),
            " ".join(market.get("_tags", [])),
        ]
    )

    if not contains_any(combined, DEFAULT_FINANCE_TERMS):
        return False

    if focus == "macro" and not contains_any(combined, DEFAULT_MACRO_TERMS):
        return False
    if focus == "micro" and not contains_any(combined, DEFAULT_MICRO_TERMS):
        return False

    if user_tags and not contains_any(combined, user_tags):
        return False
    if user_keywords and not contains_any(combined, user_keywords):
        return False
    if excluded_keywords and contains_any(combined, excluded_keywords):
        return False
    return True


def sort_questions(items: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:
    if mode == "none":
        return list(items)
    if mode == "endDate":
        return sorted(items, key=lambda it: it.get("endDate") or "9999-12-31")

    def volume_key(item: Dict[str, Any]) -> Tuple[float, float]:
        v24 = item.get("_volume24hr")
        vol = item.get("_volume")
        return (
            float(v24) if v24 is not None else -1.0,
            float(vol) if vol is not None else -1.0,
        )

    return sorted(items, key=volume_key, reverse=True)


def translate_with_deepl(
    text: str,
    target_lang: str,
    endpoint: str,
    api_key: str,
    timeout: int,
) -> str:
    payload = parse.urlencode(
        {
            "auth_key": api_key,
            "text": text,
            "target_lang": target_lang.upper(),
        }
    ).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    with request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        body = resp.read().decode(charset, errors="replace")
        data = json.loads(body)
    translations = data.get("translations")
    if not isinstance(translations, list) or not translations:
        raise RuntimeError("missing translations in provider response")
    translated = safe_str(translations[0].get("text"))
    if not translated:
        raise RuntimeError("empty translated text")
    return translated


def maybe_translate_titles(
    questions: List[Dict[str, Any]],
    args: argparse.Namespace,
    warnings: List[str],
) -> None:
    if not args.translate:
        return

    provider = safe_str(args.translate_provider).lower()
    if provider != "deepl":
        warnings.append(f"unsupported translate provider: {provider}")
        return

    api_key = safe_str(args.translate_api_key) or safe_str(
        os.getenv("POLYMARKET_TRANSLATE_API_KEY")
    )
    if not api_key:
        warnings.append("translation skipped: missing POLYMARKET_TRANSLATE_API_KEY")
        return

    endpoint = (
        safe_str(args.translate_endpoint)
        or safe_str(os.getenv("POLYMARKET_TRANSLATE_ENDPOINT"))
        or DEFAULT_TRANSLATE_ENDPOINT
    )
    target_lang = safe_str(args.translate_to) or "ZH"

    for question in questions:
        title = safe_str(question.get("title"))
        if not title:
            continue
        try:
            translated = translate_with_deepl(
                text=title,
                target_lang=target_lang,
                endpoint=endpoint,
                api_key=api_key,
                timeout=args.request_timeout,
            )
            question["titleTranslated"] = translated
            question["translatedLang"] = target_lang.upper()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            warnings.append(f"translation failed for '{title[:48]}...': {exc}")


def to_public_question(item: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "title": item.get("title"),
        "url": item.get("url"),
        "category": item.get("category") or "finance",
        "endDate": item.get("endDate"),
        "yesPrice": item.get("yesPrice"),
        "noPrice": item.get("noPrice"),
    }
    if "titleTranslated" in item:
        result["titleTranslated"] = item["titleTranslated"]
    if "translatedLang" in item:
        result["translatedLang"] = item["translatedLang"]
    return {key: value for key, value in result.items() if value is not None}


def main() -> int:
    args = parse_args()
    if args.limit <= 0:
        raise RuntimeError("--limit must be greater than 0")
    if args.cache_ttl < 0:
        raise RuntimeError("--cache-ttl must be >= 0")
    if args.request_timeout <= 0:
        raise RuntimeError("--request-timeout must be greater than 0")
    if args.dedup_threshold < 0 or args.dedup_threshold > 1:
        raise RuntimeError("--dedup-threshold must be between 0 and 1")

    used_tags = parse_csv_list(args.tags)
    used_keywords = parse_csv_list(args.keywords)
    excluded_keywords = parse_csv_list(args.exclude_keywords)
    warnings: List[str] = []

    source = "api"
    cached = False

    if args.input:
        markets = load_input_markets(args.input)
        source = "input"
    else:
        cache_payload: Optional[Dict[str, Any]] = None
        cache_markets: List[Dict[str, Any]] = []
        cache_age: Optional[int] = None
        if not args.no_cache:
            cache_payload = load_cache_payload(args.cache_path, warnings)
            if cache_payload:
                cache_markets = extract_markets(cache_payload.get("markets"))
                fetched_at = cache_payload.get("fetchedAt")
                fetched_time = safe_float(fetched_at)
                if fetched_time is not None:
                    cache_age = int(time.time() - fetched_time)

        use_fresh_cache = (
            bool(cache_markets)
            and cache_age is not None
            and cache_age <= args.cache_ttl
            and not args.no_cache
        )
        if use_fresh_cache:
            markets = cache_markets
            source = "cache"
            cached = True
        else:
            try:
                markets = fetch_live_markets(
                    api_url=args.api_url,
                    timeout=args.request_timeout,
                )
                source = "api"
                cached = False
                if not args.no_cache:
                    save_cache_payload(args.cache_path, args.api_url, markets, warnings)
            except Exception as exc:
                if cache_markets:
                    warnings.append(f"live fetch failed, fallback to cache: {exc}")
                    markets = cache_markets
                    source = "cache"
                    cached = True
                else:
                    raise

    normalized: List[Dict[str, Any]] = []
    for market in markets:
        item = normalize_market(market)
        if not item:
            continue
        if not is_finance_related(
            market=item,
            user_tags=used_tags,
            user_keywords=used_keywords,
            excluded_keywords=excluded_keywords,
            focus=args.focus,
        ):
            continue
        normalized.append(item)

    sorted_items = sort_questions(normalized, args.sort)
    deduped_items, dedup_removed = deduplicate_questions(
        items=sorted_items,
        mode=args.dedup_mode,
        threshold=args.dedup_threshold,
    )
    selected_items = deduped_items[: args.limit]
    maybe_translate_titles(selected_items, args, warnings)

    questions = [to_public_question(item) for item in selected_items]
    sort_field = "volume24hr" if args.sort == "volume" else ("endDate" if args.sort == "endDate" else None)
    meta = {
        "source": source,
        "cached": cached,
        "totalCount": len(markets),
        "filteredCount": len(normalized),
        "usedTags": used_tags,
        "usedKeywords": used_keywords,
        "excludedKeywords": excluded_keywords,
        "focus": args.focus,
        "sort": args.sort,
        "sortField": sort_field,
        "dedupMode": args.dedup_mode,
        "dedupThreshold": args.dedup_threshold,
        "dedupRemoved": dedup_removed,
        "warnings": warnings,
    }
    output = {"questions": questions, "meta": meta}
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
