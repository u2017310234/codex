# Book Value Potential Pipeline

This project implements the scoring system described in `book/book.md`. It normalizes JD + Douban data, computes a structured score, optionally calls Gemini for semantic judgment and adjustment, and outputs final scores plus an observation pool.

## Quick start (sample data, no LLM)

```bash
python3 /workspaces/codex/book/pipelines/run_pipeline.py --use-sample --mock-llm
```

Outputs are written to `book/output/`.

## Fetch real JD/Douban data

```bash
python3 /workspaces/codex/book/pipelines/fetch_sources.py --keyword "精装 首版" --pages 1 --max-items 20
```

This writes `jd_live.json` and `douban_live.json` to `book/data/`.

Then run the pipeline with these files:

```bash
python3 /workspaces/codex/book/pipelines/run_pipeline.py \
  --jd-data /workspaces/codex/book/data/jd_live.json \
  --douban-data /workspaces/codex/book/data/douban_live.json \
  --mock-llm
```

To avoid network calls (test only):

```bash
python3 /workspaces/codex/book/pipelines/fetch_sources.py --use-sample
```

## JD ranking mode (no search.jd)

By default the fetcher uses JD ranking (phb) pages instead of `search.jd.com`.

```bash
python3 /workspaces/codex/book/pipelines/fetch_sources.py --jd-mode phb --max-items 20
```

You can override the ranking URLs with a comma-separated list or a file:

```bash
python3 /workspaces/codex/book/pipelines/fetch_sources.py --jd-mode phb --rank-urls "https://www.jd.com/phb/key_xxx.html,https://www.jd.com/phb/key_yyy.html"
```

```bash
python3 /workspaces/codex/book/pipelines/fetch_sources.py --jd-mode phb --rank-urls /path/to/jd_rank_urls.txt
```

## Headers / Cookies (optional)

Some runs may require cookies to improve access stability.

```bash
export JD_COOKIE="your_jd_cookie"
export DOUBAN_COOKIE="your_douban_cookie"
```

The fetcher also supports throttling:

```bash
python3 /workspaces/codex/book/pipelines/fetch_sources.py --sleep-min 1.5 --sleep-max 3.0 --retries 3 --timeout 25
```

## LLM mode (Gemini)

Set environment variables and run without `--mock-llm`:

```bash
export GEMINI_API_KEY=... 
export GEMINI_MODEL=gemini-3-flash-preview
python3 /workspaces/codex/book/pipelines/run_pipeline.py --use-sample
```

## CLI options

- `--jd-data` path to JD JSON
- `--douban-data` path to Douban JSON
- `--output-dir` output directory
- `--top-pct` top percentile for LLM analysis (default `0.10`)
- `--mock-llm` use deterministic mock LLM (no network)
- `--max-llm` limit LLM calls

## Data format

See `book/data/jd_sample.json` and `book/data/douban_sample.json` for expected fields.
