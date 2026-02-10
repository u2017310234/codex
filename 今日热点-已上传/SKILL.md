---
name: tophub-hot-topics
description: Aggregate and summarize tophub.today section rankings into deduplicated, event-level hot topics. Use when a user asks to summarize today's hot topics, trending lists, or tophub.today content, and needs results grouped by tophub sections.
---

# Tophub Hot Topics

## Overview

Aggregate tophub.today section lists into event-level hot topics, deduplicate across sources, and output Chinese paragraphs grouped by section. **Each paragraph must cite information sources (URLs and/or reporting organizations).**

## Workflow

### 1. Collect source lists

- Run `python scripts/fetch_tophub.py --pretty --output tophub.json` to fetch and parse the homepage.
- Run `python scripts/fetch_tophub.py --html-file <saved.html> --pretty --output tophub.json` when working offline.
- Adjust selectors in `scripts/fetch_tophub.py` or manually copy lists when categories are missing or clearly wrong.

### 2. Normalize and deduplicate by event keywords

- Extract event keywords for each item: core entities (people, orgs, places), action, timeframe/impact.
- Merge items across lists when they refer to the same event; treat them as the same event when at least two of the three keyword groups match.
- Choose a canonical event phrasing and fold variant titles into it.
- Assign each merged event to the most relevant section; repeat across sections only when a distinct angle is genuinely needed.

### 3. Write output

- Use the tophub section names as headings and keep the source order.
- Write one paragraph per event (2–4 sentences), in Chinese, without bullet lists.
- Mention key entities, what happened, and why it is hot or impactful.
- **Include information sources in each paragraph** (URLs and/or reporting organizations). Keep citations concise and readable.
- Keep paragraphs standalone; avoid link dumps.

### 4. Save output locally

- Save the final markdown summary to a **relative directory**: `./output/tophub/`.
- File name: `YYYY-MM-DD.md` using local date.
- If the file already exists, append the new summary after a blank line.
- Use `python scripts/save_summary.py` and pass the summary via stdin (preferred) or `--input`.

## Resources

- `scripts/fetch_tophub.py`: Fetch and parse tophub.today sections into JSON.
- `scripts/save_summary.py`: Save the summary markdown to the local archive path.
- Requires Python packages: `requests`, `beautifulsoup4`.
