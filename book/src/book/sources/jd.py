from __future__ import annotations

import re
import os
from dataclasses import dataclass
from typing import Any

from .http_client import HttpClient


@dataclass
class JDConfig:
    keyword: str = "精装 首版"
    pages: int = 1
    max_items: int = 40


@dataclass
class JDClient:
    client: HttpClient

    def search(self, keyword: str, pages: int = 1, max_items: int = 40) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in range(1, pages + 1):
            url = "https://search.jd.com/Search"
            params = {
                "keyword": keyword,
                "enc": "utf-8",
                "page": page,
            }
            html = self.client.get_text(url, params=params, headers=_jd_headers())
            for entry in parse_search(html):
                items.append(entry)
                if len(items) >= max_items:
                    return items
        return items

    def fetch_rankings(self, rank_urls: list[str], max_items: int = 40) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for url in rank_urls:
            html = self.client.get_text(url, headers=_jd_headers())
            for entry in parse_rankings(html):
                sku = entry.get("sku")
                if not sku or sku in seen:
                    continue
                seen.add(sku)
                items.append(entry)
                if len(items) >= max_items:
                    return items
        return items

    def fetch_detail(self, sku: str, item_url: str | None = None) -> dict[str, Any]:
        url = item_url or f"https://item.jd.com/{sku}.html"
        html = self.client.get_text(url, headers=_jd_headers())
        specs = parse_specs(html)
        title = parse_title(html)
        stock_status = _parse_stock_status(html)
        price_now, price_list = fetch_price(self.client, sku)
        is_signed = "签名" in (title or "")
        is_limited = "限量" in (title or "")
        record = {
            "title": title or specs.get("title"),
            "author": specs.get("author"),
            "publisher": specs.get("publisher"),
            "publish_date": specs.get("publish_date"),
            "print_info": specs.get("print_info"),
            "isbn": specs.get("isbn"),
            "binding": specs.get("binding"),
            "is_limited": is_limited,
            "is_signed": is_signed,
            "price_list": price_list or price_now,
            "price_now": price_now,
            "stock_status": stock_status,
            "jd_url": url,
        }
        return record


def fetch_price(client: HttpClient, sku: str) -> tuple[float | None, float | None]:
    url = "https://p.3.cn/prices/mgets"
    params = {"skuIds": f"J_{sku}"}
    try:
        data = client.get_json(url, params=params, headers=_jd_headers())
    except Exception:
        return None, None
    if not data:
        return None, None
    item = data[0]
    price_now = float(item.get("p")) if item.get("p") else None
    price_list = float(item.get("m")) if item.get("m") else None
    return price_now, price_list


def parse_search(html: str) -> list[dict[str, Any]]:
    items = []
    seen: set[str] = set()
    for match in re.finditer(r"<li[^>]+class=\"gl-item\"[^>]*data-sku=\"(\d+)\"[^>]*>(.*?)</li>", html, re.S):
        sku = match.group(1)
        if sku in seen:
            continue
        seen.add(sku)
        block = match.group(2)
        link_match = re.search(r"href=\"(//item\.jd\.com/\d+\.html)\"", block)
        url = f"https:{link_match.group(1)}" if link_match else f"https://item.jd.com/{sku}.html"
        title_match = re.search(r"<em>(.*?)</em>", block, re.S)
        title = _clean_text(title_match.group(1)) if title_match else None
        items.append({"sku": sku, "title": title, "jd_url": url})

    if not items:
        for sku in re.findall(r"data-sku=\"(\d+)\"", html):
            if sku in seen:
                continue
            seen.add(sku)
            items.append({"sku": sku, "title": None, "jd_url": f"https://item.jd.com/{sku}.html"})
    return items


def parse_rankings(html: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in re.finditer(r"href=\"(//item\.jd\.com/(\d+)\.html)\"[^>]*>(.*?)</a>", html, re.S):
        sku = match.group(2)
        if sku in seen:
            continue
        seen.add(sku)
        title = _clean_text(match.group(3))
        url = f"https:{match.group(1)}"
        items.append({"sku": sku, "title": title or None, "jd_url": url})
    if not items:
        for sku in re.findall(r"//item\.jd\.com/(\d+)\.html", html):
            if sku in seen:
                continue
            seen.add(sku)
            items.append({"sku": sku, "title": None, "jd_url": f"https://item.jd.com/{sku}.html"})
    return items


def parse_title(html: str) -> str | None:
    match = re.search(r"<div class=\"sku-name\">\s*([^<]+)", html)
    if match:
        return _clean_text(match.group(1))
    match = re.search(r"<title>(.*?)</title>", html, re.S)
    if match:
        return _clean_text(match.group(1))
    return None


def parse_specs(html: str) -> dict[str, Any]:
    specs: dict[str, Any] = {}
    for key, value in _extract_param_pairs(html):
        if key in {"出版社"}:
            specs["publisher"] = value
        elif key in {"出版时间", "出版日期", "出版年"}:
            specs["publish_date"] = value
        elif key in {"印次", "版次"}:
            specs["print_info"] = value
        elif key in {"装帧", "包装"}:
            specs["binding"] = value
        elif key in {"ISBN", "ISBN编号"}:
            specs["isbn"] = normalize_isbn(value)
        elif key in {"作者"}:
            specs["author"] = value
    return specs


def normalize_isbn(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"[^0-9Xx]", "", value)
    return cleaned.upper() if cleaned else None


def _clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _parse_stock_status(html: str) -> str:
    lowered = html.lower()
    if any(token in html for token in ["无货", "缺货", "售罄", "暂时无货"]):
        return "out_of_stock"
    if "无货" in lowered or "sold out" in lowered:
        return "out_of_stock"
    return "in_stock"


def _extract_param_pairs(html: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for block in _extract_parameter_blocks(html):
        for match in re.finditer(r"<li([^>]*)>(.*?)</li>", block, re.S):
            attrs = match.group(1)
            inner = match.group(2)
            attr_title = re.search(r"title=[\"']([^\"']+)[\"']", attrs)
            raw = attr_title.group(1) if attr_title else inner
            text = _clean_text(raw)
            if not text:
                continue
            if "：" in text:
                key, value = text.split("：", 1)
            elif ":" in text:
                key, value = text.split(":", 1)
            else:
                continue
            pairs.append((key.strip(), value.strip()))
    # Fallback: scan any remaining li tags
    if not pairs:
        for match in re.finditer(r"<li[^>]*>(.*?)</li>", html, re.S):
            text = _clean_text(match.group(1))
            if "：" in text:
                key, value = text.split("：", 1)
            elif ":" in text:
                key, value = text.split(":", 1)
            else:
                continue
            pairs.append((key.strip(), value.strip()))
    return pairs


def _extract_parameter_blocks(html: str) -> list[str]:
    blocks: list[str] = []
    patterns = [
        r"<ul[^>]*class=\"parameter2[^\\\"]*\"[^>]*>(.*?)</ul>",
        r"<ul[^>]*class=\"p-parameter-list[^\\\"]*\"[^>]*>(.*?)</ul>",
        r"<div[^>]*class=\"p-parameter\"[^>]*>(.*?)</div>",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, html, re.S):
            blocks.append(match.group(1))
    return blocks


def _jd_headers() -> dict[str, str] | None:
    cookie = os.getenv("JD_COOKIE")
    if not cookie:
        return None
    return {"Cookie": cookie}


DEFAULT_RANK_URLS = [
    "https://www.jd.com/phb/key_1713781d2e2b0dbd6b75.html",  # 所有书籍排行榜
    "https://www.jd.com/phb/key_17132d5019343477b734.html",  # 新书籍排行榜
    "https://www.jd.com/phb/key_1713ca182abf6b552813.html",  # 畅销新书排行榜
    "https://www.jd.com/phb/key_1713f0ca5fab71bad85c.html",  # 图书榜单排行榜
]
