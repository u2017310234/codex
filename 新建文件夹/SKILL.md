---
name: polymarket-finance-questions
description: Fetch and filter active Polymarket markets for finance-related questions (macro, rates, equities, crypto, commodities). Use when the user asks for current finance prediction markets, market expectations, or to list/monitor Polymarket finance questions. Includes offline input, caching, and optional translation.
---

# Polymarket Finance Questions

## Overview

Use this skill to retrieve active Polymarket markets, filter to finance-related questions, and return structured JSON for LLM or agent use. Prefer the provided script for deterministic results and offline testing.

## Quick start

Run the script against the sample input:

```bash
python scripts/polymarket_finance_questions.py --input scripts/sample_input.json --limit 5
```

## Workflow

1. Choose a data source: `--input`, cache, or live API.
2. Set filters: `--tags`, `--keywords`, `--limit`, and `--sort`.
3. Set focus and dedup strategy: `--focus`, `--exclude-keywords`, `--dedup-mode`, `--dedup-threshold`.
4. Optionally enable translation with `--translate` and provider settings.
5. Inspect JSON output and pass to downstream tools.

## Script usage

Script: `scripts/polymarket_finance_questions.py`

Key options:
- `--limit`: Max number of questions to return.
- `--keywords`: Comma-separated or repeated keyword list.
- `--exclude-keywords`: Comma-separated or repeated keyword exclusion list.
- `--focus`: `all`, `macro`, or `micro`.
- `--tags`: Comma-separated or repeated tag list.
- `--sort`: `volume`, `endDate`, or `none`.
- `--dedup-mode`: `coarse`, `fuzzy`, `exact`, or `none`.
- `--dedup-threshold`: Fuzzy dedup Jaccard threshold in `[0, 1]`.
- `--input`: Path to local JSON file (offline mode).
- `--cache-ttl`: Cache time-to-live in seconds.
- `--cache-path`: Custom cache location.
- `--no-cache`: Disable cache read/write.
- `--translate`: Enable optional translation.
- `--translate-provider`: Translation provider name (default: `deepl`).
- `--translate-to`: Target language (default: `ZH`).
- `--translate-endpoint`: Override translation API endpoint.
- `--translate-api-key`: Override translation API key.

Translation notes:
- Set `POLYMARKET_TRANSLATE_API_KEY` (or use `--translate-api-key`).
- Set `POLYMARKET_TRANSLATE_ENDPOINT` to override DeepL endpoint if needed.

## Output schema

The script prints JSON with the following shape:

```json
{
  "questions": [
    {
      "title": "Will the Fed cut interest rates before July 2026?",
      "url": "https://polymarket.com/market/fed-rate-cut-2026",
      "category": "finance",
      "endDate": "2026-07-01",
      "yesPrice": 0.63,
      "noPrice": 0.37,
      "titleTranslated": "...",
      "translatedLang": "ZH"
    }
  ],
  "meta": {
    "source": "api",
    "cached": false,
    "totalCount": 120,
    "filteredCount": 12,
    "usedTags": ["finance", "macro"],
    "usedKeywords": ["inflation", "gdp"],
    "excludedKeywords": ["fed", "cpi"],
    "focus": "micro",
    "sort": "volume",
    "sortField": "volume24hr",
    "dedupMode": "coarse",
    "dedupThreshold": 0.82,
    "dedupRemoved": 6,
    "warnings": []
  }
}
```

`titleTranslated` and `translatedLang` appear only when translation is enabled and succeeds.

## Offline and cache behavior

- Use `--input` to bypass network access.
- Cache is stored as raw markets and reused if fresh.
- Use `--no-cache` to disable cache reads and writes.

## References

- `references/polymarket-api.md`
