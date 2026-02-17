# Book Value Potential Pipeline Design

## Summary
This design implements the “首版首印精装书升值潜力评分模型” described in `book/book.md`. The pipeline ingests JD (supply/version) and Douban (demand/cultural status) data, normalizes and matches records, computes a structured score, then uses LLM inference to add semantic judgment and a bounded adjustment to the structured score. Outputs include per-book scores, tiers, and an observation pool for periodic review.

## Architecture
- **Data layer**: JSON inputs for JD and Douban. Normalization standardizes ISBN, print info, binding, price, and flags.
- **Structured scoring layer**: Rules compute version scarcity, author/work status, consensus strength, theme durability, and market signals. Non-first edition/print triggers a 0.5 multiplier.
- **LLM layer**: Gemini receives a compact payload and returns `classic_potential`, `era_significance`, `ip_potential`, and `structured_adjustment` (-10 to +10), plus confidence and rationale.
- **Aggregation**: Final score mixes adjusted structured score with LLM sub-scores. Tiers are assigned with clear thresholds.

## Components
- `normalization.py`: field normalization and print parsing.
- `matching.py`: ISBN-first matching with title/author fallback.
- `scoring.py`: structured scoring and consensus percentile buckets.
- `llm.py`: Gemini/Mock LLM clients, JSON parsing, bounded adjustment.
- `pipeline.py`: orchestration and output creation.
- `pipelines/run_pipeline.py`: CLI entrypoint.

## Data Flow
1. Load JD + Douban JSON.
2. Normalize and match records.
3. Compute consensus percentiles and structured score.
4. Select top N for LLM.
5. Apply LLM adjustment and compute final score.
6. Emit `books_scored.json`, `books_scored.csv`, `observation_pool.json`.

## Error Handling
- LLM parse failures fall back to zeros without crashing.
- Missing fields default to safe values.
- If no API key is provided, mock LLM is used.

## Testing
- Run `pipelines/run_pipeline.py --use-sample --mock-llm` to validate the pipeline end-to-end.
- Optional Gemini tests run with `GEMINI_API_KEY` and `GEMINI_MODEL`.
