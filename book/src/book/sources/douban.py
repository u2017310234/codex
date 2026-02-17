from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from .http_client import HttpClient


@dataclass
class DoubanClient:
    client: HttpClient

    def fetch_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        url = f"https://book.douban.com/isbn/{isbn}/"
        html = self.client.get_text(url, headers=_douban_headers())
        return parse_subject(html, url)

    def search_by_title(self, title: str, author: str | None = None) -> dict[str, Any] | None:
        query = title if not author else f"{title} {author}"
        url = "https://book.douban.com/subject_search"
        params = {"search_text": query, "cat": "1001"}
        html = self.client.get_text(url, params=params, headers=_douban_headers())
        subject_url = parse_first_subject_url(html)
        if not subject_url:
            subject_url = search_by_suggest(self.client, query)
        if not subject_url:
            return None
        html = self.client.get_text(subject_url, headers=_douban_headers())
        return parse_subject(html, subject_url)


def parse_first_subject_url(html: str) -> str | None:
    match = re.search(r"href=\"(https://book\.douban\.com/subject/\d+/)\"", html)
    if match:
        return match.group(1)
    return None


def search_by_suggest(client: HttpClient, query: str) -> str | None:
    url = "https://book.douban.com/j/subject_suggest"
    params = {"q": query}
    try:
        data = client.get_json(url, params=params, headers=_douban_headers())
    except Exception:
        return None
    if not data:
        return None
    first = data[0]
    return first.get("url")


def parse_subject(html: str, url: str) -> dict[str, Any]:
    rating = _extract_first(html, [r"class=\"rating_num\"[^>]*>([0-9.]+)", r"class=\"rating_nums\"[^>]*>([0-9.]+)"])
    rating_count = _extract_first(html, [r"property=\"v:votes\"[^>]*>(\d+)", r"class=\"rating_people\"[^>]*>\s*<span[^>]*>(\d+)"])
    tags = _extract_tags(html)
    info = _extract_info(html)
    adapted = any(keyword in " ".join(tags) for keyword in ["影视", "改编", "电影", "电视剧"])
    author_bio = _extract_author_bio(html) or info.get("author_bio", "")
    return {
        "title": info.get("title"),
        "author": info.get("author"),
        "isbn": info.get("isbn"),
        "rating": float(rating) if rating else None,
        "rating_count": int(rating_count) if rating_count else 0,
        "tags": tags,
        "awards": info.get("awards", []),
        "adapted": adapted,
        "review_keywords": tags[:3],
        "author_bio": author_bio,
        "douban_url": url,
    }


def _extract_first(html: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    return None


def _extract_tags(html: str) -> list[str]:
    tags_section = re.search(r"class=\"tags-body\"[^>]*>(.*?)</div>", html, re.S)
    if not tags_section:
        # Fallback to generic tags
        tags = re.findall(r"class=\"tag\"[^>]*>([^<]+)</a>", html)
        return [t.strip() for t in tags if t.strip()]
    tags = re.findall(r">([^<]+)</a>", tags_section.group(1))
    return [t.strip() for t in tags if t.strip()]


def _extract_info(html: str) -> dict[str, Any]:
    info = {}
    title_match = re.search(r"<span property=\"v:itemreviewed\">(.*?)</span>", html)
    if title_match:
        info["title"] = _clean_text(title_match.group(1))
    author_match = re.search(r"作者:?\s*</span>\s*<a[^>]*>([^<]+)</a>", html)
    if author_match:
        info["author"] = _clean_text(author_match.group(1))
    isbn_match = re.search(r"ISBN[:：]\s*([0-9Xx-]+)", html)
    if isbn_match:
        info["isbn"] = isbn_match.group(1).replace("-", "").upper()
    awards_match = re.search(r"获奖[:：]\s*([^<]+)", html)
    if awards_match:
        info["awards"] = [_clean_text(awards_match.group(1))]
    info_block = re.search(r"<div id=\"info\"[^>]*>(.*?)</div>", html, re.S)
    if info_block:
        info_lines = _clean_info_block(info_block.group(1))
        for line in info_lines:
            if ":" in line:
                key, value = line.split(":", 1)
            elif "：" in line:
                key, value = line.split("：", 1)
            else:
                continue
            key = key.strip()
            value = value.strip()
            if key in {"作者"} and value:
                info["author"] = value
            if key in {"ISBN"} and value:
                info["isbn"] = value.replace("-", "").upper()
            if key in {"出版年"} and value:
                info["publish_date"] = value
            if key in {"出版社"} and value:
                info["publisher"] = value
    return info


def _clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _clean_info_block(block: str) -> list[str]:
    block = block.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    block = re.sub(r"<[^>]+>", "", block)
    lines = [line.strip() for line in block.split("\n") if line.strip()]
    return lines


def _extract_author_bio(html: str) -> str | None:
    match = re.search(r"class=\"author-intro\"[^>]*>.*?<div class=\"intro\">(.*?)</div>", html, re.S)
    if match:
        return _clean_text(match.group(1))
    return None


def _douban_headers() -> dict[str, str] | None:
    cookie = os.getenv("DOUBAN_COOKIE")
    headers = {"Referer": "https://book.douban.com/"}
    if cookie:
        headers["Cookie"] = cookie
    return headers
