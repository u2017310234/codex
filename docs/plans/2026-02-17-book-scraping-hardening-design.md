# Book Scraping Hardening Design

## Summary
This update improves the JD/Douban scraping to be more precise and resilient. It adds request retries with backoff, optional cookies, multi-pattern parsing of JD parameter blocks, a Douban subject-suggest fallback, and a weekly GitHub Actions schedule. Output formats remain compatible with the scoring pipeline.

## Changes
- **HTTP client**: configurable timeout/sleep/retries, retry on 429/5xx with exponential backoff.
- **JD parsing**: extracts metadata from multiple parameter blocks (`parameter2`, `p-parameter-list`, `p-parameter`), supports `title` attributes on `<li>`, and improves stock detection.
- **Douban parsing**: adds robust info-block parsing, tag fallbacks, author-bio extraction, and a `subject_suggest` API fallback when HTML search fails.
- **Cookies**: optional `JD_COOKIE` and `DOUBAN_COOKIE` are injected via headers to improve access stability.
- **Workflow**: scheduled weekly on Friday night (UTC 13:00, CST 21:00) with artifacts uploaded.

## Data Flow
1. JD search → SKU list.
2. JD detail pages → ISBN, print info, binding, publisher, author, stock.
3. Douban ISBN lookup → rating, votes, tags, author bio.
4. If ISBN missing, use subject search + suggest fallback.
5. Save `jd_live.json` + `douban_live.json` for scoring.

## Error Handling
- Single-item failures do not stop the batch.
- Retries only on transient HTTP codes.
- If Douban search fails, the pipeline continues without that record.

## Testing
- `fetch_sources.py --use-sample` validates the end-to-end flow without network.
