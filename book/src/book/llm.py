from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class LLMResult:
    classic_potential: float
    era_significance: float
    ip_potential: float
    structured_adjustment: float
    confidence: float
    rationale: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _parse_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


class LLMClient:
    def analyze_book(self, payload: dict[str, Any]) -> LLMResult:
        raise NotImplementedError


class MockLLMClient(LLMClient):
    def analyze_book(self, payload: dict[str, Any]) -> LLMResult:
        tags = set(payload.get("tags", []))
        keywords = " ".join(payload.get("review_keywords", []))
        classic = 8.5 if "经典" in keywords else 6.0
        era = 7.0 if tags & {"政治哲学", "经济思想", "历史"} else 4.0
        ip = 6.5 if payload.get("adapted") else 4.0
        adjustment = 5.0 if classic >= 8 else -2.0
        return LLMResult(
            classic_potential=classic,
            era_significance=era,
            ip_potential=ip,
            structured_adjustment=adjustment,
            confidence=70.0,
            rationale="Mock heuristic based on tags and keywords.",
        )


class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", timeout: int = 30) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def analyze_book(self, payload: dict[str, Any]) -> LLMResult:
        prompt = (
            "You are a cultural value analyst. Given the book data, output ONLY JSON with fields: "
            "classic_potential (0-10), era_significance (0-10), ip_potential (0-10), "
            "structured_adjustment (-10 to 10), confidence (0-100), rationale (string).\n"
            "Consider long-term classic potential, era significance, and IP potential. "
            "Adjust structured score mildly for semantic correction.\n\n"
            f"Book data: {json.dumps(payload, ensure_ascii=False)}"
        )
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 512,
            },
        }
        response = requests.post(url, json=body, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        text = ""
        for candidate in data.get("candidates", []):
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                text += part.get("text", "")
        parsed = _parse_json(text)
        if not parsed:
            return LLMResult(0, 0, 0, 0, 0, "LLM parse failed")
        return LLMResult(
            classic_potential=_clamp(float(parsed.get("classic_potential", 0)), 0, 10),
            era_significance=_clamp(float(parsed.get("era_significance", 0)), 0, 10),
            ip_potential=_clamp(float(parsed.get("ip_potential", 0)), 0, 10),
            structured_adjustment=_clamp(float(parsed.get("structured_adjustment", 0)), -10, 10),
            confidence=_clamp(float(parsed.get("confidence", 0)), 0, 100),
            rationale=str(parsed.get("rationale", "")),
        )


def build_llm_client(mock: bool = False) -> LLMClient:
    if mock:
        return MockLLMClient()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return MockLLMClient()
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    return GeminiClient(api_key=api_key, model=model)
