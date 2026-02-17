# JD + Douban Scraping Design

## Summary
This design adds real data fetching for JD and Douban to the existing pipeline. It introduces a lightweight HTTP client with rate limiting, a JD scraper for search + item detail, and a Douban scraper for ISBN or title-based lookup. Outputs are JSON files compatible with the existing scoring pipeline.

## JD Fetching
- **Search**: request JD search page with keyword, page, and encoding parameters.
- **Parse**: extract product blocks (`gl-item`) with `data-sku`, item URL, and title.
- **Detail**: fetch `item.jd.com/{sku}.html` and parse `li` specs for ISBN, publisher, publish date, print info, binding, author.
- **Price**: fetch price API to get current price and list price.
- **Stock**: infer from presence of “无货/缺货” text.

## Douban Fetching
- **ISBN first**: request `book.douban.com/isbn/{isbn}/` and parse subject page.
- **Fallback search**: if ISBN is missing, call subject search and follow the first subject URL.
- **Parse**: rating, rating count, tags, author, ISBN, and basic awards.

## Error Handling
- Failures on a single book do not abort the batch.
- Missing fields default to empty values; pipeline still runs.
- LLM is optional and can be mocked.

## CLI
`pipelines/fetch_sources.py` outputs `jd_live.json` and `douban_live.json` for downstream scoring.

## Testing
Use `--use-sample` to avoid network calls and validate end-to-end flow.
