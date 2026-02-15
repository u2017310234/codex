# Codex

This repository contains:

1. **米粒太声乐助手 (Music Vocal Assistant)** - A web application for vocal training and audio analysis
2. **TopHub Entertainment Daily** - An automated entertainment news aggregator

## Live Demo

The web application is deployed via GitHub Pages and can be accessed at:
https://u2017310234.github.io/codex/

## TopHub Entertainment Daily (Gemini)

Daily GitHub Action that:

- Fetches `https://tophub.today/c/ent`
- Extracts all titles (best-effort, with noise filtering)
- Sends the full title list to Gemini
- Produces:
  - `output/titles.txt`
  - `output/summary.json`
  - `output/summary.md`

## Local Run

Requirements:

- Node.js 20+ (Node 20 recommended)
- A Gemini API key

Set env vars:

```bash
export GEMINI_API_KEY="..."   # or export GEMINI="..."
export GEMINI_MODEL="gemini-2.5-flash"  # optional
```

Run:

```bash
node scripts/tophub_entertainment.mjs
```

## GitHub Actions Setup

Secrets (one of these must exist):

- `GEMINI_API_KEY` (recommended)
- `GEMINI` (supported as fallback)

Optional secrets:

- `GEMINI_MODEL` (default: `gemini-2.5-flash`)

Optional variables:

- `COMMIT_RESULTS=true` to commit `output/` back into the repo.
  - Default is artifact upload only.

## Notes

- The script has a fetch fallback via `r.jina.ai` in case TopHub blocks direct requests.
- The JSON output is validated to ensure exactly 5 hot event keywords and 5 meme words.
