# JD Ranking Source Design

## Summary
This design replaces `search.jd.com` with JD ranking (phb) pages as the primary source for “new book” discovery. Ranking pages are more stable, align with public lists, and avoid search endpoints that may be blocked.

## Approach
- Use a curated list of JD ranking URLs (`phb/key_*.html`).
- Parse each ranking page for `item.jd.com/{sku}.html` links to get SKU lists.
- Fetch each SKU detail page for ISBN/edition/press/binding fields.
- Fetch price via the JD price API.

## Configuration
- `--jd-mode phb` (default)
- `--rank-urls` supports comma-separated URLs or a file of URLs.
- Default ranking URLs are stored in code for convenience.

## Error Handling
- Deduplicate SKUs across multiple ranking pages.
- Skip invalid entries without aborting the batch.

## Testing
- `fetch_sources.py --use-sample` still validates end-to-end integration.
