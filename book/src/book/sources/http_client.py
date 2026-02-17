from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any

import requests


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass
class HttpClient:
    timeout: int = 20
    sleep_min: float = 1.2
    sleep_max: float = 2.4
    max_retries: int = 3
    backoff_base: float = 1.3
    retry_statuses: tuple[int, ...] = (429, 500, 502, 503, 504)
    extra_headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        if self.extra_headers:
            self.session.headers.update(self.extra_headers)

    def _sleep(self) -> None:
        if self.sleep_max <= 0:
            return
        time.sleep(random.uniform(self.sleep_min, self.sleep_max))

    def _backoff(self, attempt: int) -> None:
        delay = self.backoff_base * (2**attempt) + random.uniform(0, 0.3)
        time.sleep(delay)

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            self._sleep()
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                )
                if response.status_code in self.retry_statuses and attempt < self.max_retries - 1:
                    self._backoff(attempt)
                    continue
                response.raise_for_status()
                return response
            except requests.RequestException as exc:  # pragma: no cover - network failure
                last_exc = exc
                if attempt >= self.max_retries - 1:
                    raise
                self._backoff(attempt)
        if last_exc:
            raise last_exc
        raise RuntimeError("HTTP request failed without exception")

    def get_text(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> str:
        return self.get(url, params=params, headers=headers).text

    def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        return self.get(url, params=params, headers=headers).json()
