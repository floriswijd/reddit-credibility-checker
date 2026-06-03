# Reddit Credibility Checker

A local-first Python MVP that analyzes a Reddit user's historical stock-related posts and comments, extracts concrete market claims, validates approved claims against later market data, and generates a transparent credibility report.

This is **not investment advice**. The tool does not recommend buying or selling securities. It only compares historical Reddit claims against subsequent price data.

## MVP Workflow

1. Fetch recent posts/comments from finance-related subreddits.
2. Use an LLM to extract concrete stock claims.
3. Export extracted claims to CSV for manual review.
4. Validate approved claims against historical adjusted-close price data.
5. Compare stock returns against a benchmark, `SPY` by default.
6. Generate a Markdown credibility report.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Fill in `.env` with Reddit API credentials and an OpenAI API key.

## CLI

```bash
python -m reddit_credibility.cli fetch --username USERNAME --limit 100
python -m reddit_credibility.cli extract --username USERNAME
python -m reddit_credibility.cli export-review --username USERNAME
python -m reddit_credibility.cli validate --username USERNAME --review-file data/processed/USERNAME_review.csv
python -m reddit_credibility.cli report --username USERNAME
```

## Outputs

- Raw Reddit posts/comments: `data/raw/USERNAME_reddit.json`
- Extracted claims: `data/processed/USERNAME_claims.json` and `.csv`
- Manual review CSV: `data/processed/USERNAME_review.csv`
- Validated claims: `data/processed/USERNAME_validated.csv`
- Final report: `data/reports/USERNAME_report.md`

## Manual Review

Review CSV rows start with `manual_status=pending`. Before validation, change `manual_status` to `approved` for claims you want included. Use `rejected` for claims that should be ignored.

Review columns:

```text
username, reddit_id, created_at, subreddit, ticker, claim_text, claim_type,
direction, target_price, time_horizon_days, measurable, ai_confidence,
manual_status, manual_notes
```

## Scoring

The MVP score is intentionally simple and deterministic:

```text
credibility_score =
35% hit_rate_score
25% average_excess_return_score
20% specificity_score
10% sample_size_confidence
10% red_flag_adjustment
```

Only approved, measurable price/direction claims with a clear ticker and direction are validated. The MVP calculates 30-day, 90-day, and 180-day returns, uses adjusted close prices, compares against `SPY`, and skips claims that are too recent to validate.
