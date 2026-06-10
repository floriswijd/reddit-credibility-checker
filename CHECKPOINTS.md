# Checkpoints

This file lists manual checks for the current project phase.

## Current Phase

Current phase: **Phase 1 - PullPush prototype pipeline**

Goal for this phase:

```text
Fetch public Reddit activity from PullPush, normalize it, save JSON, and identify simple claim candidates without AI.
```

## Checkpoint 1 - PullPush Pilot Fetch

Purpose:

Verify the original PullPush pilot still fetches submissions and comments.

Command:

```bash
python tests/push_pull_pilot.py
```

Optional one-run override:

```bash
REDDIT_TEST_USERNAME=Where_is_Gabriel REDDIT_TEST_SUBREDDITS=wallstreetbets python3 tests/push_pull_pilot.py
```

Expected output:

- PullPush URLs are printed.
- PullPush status codes are printed, ideally `200`.
- The script prints the number of submissions found.
- The script prints the number of comments found.
- It prints previews of up to 10 submissions and up to 10 comments.

Known test inputs:

- Username: `Where_is_Gabriel`
- Subreddit: `wallstreetbets`

If this fails:

- If status is not `200`, PullPush may be unavailable or rate-limiting.
- If there is a timeout, rerun once before changing code.
- Do not add API keys or switch data sources during Phase 1 without updating `PROJECT_PLAN.md`.

## Checkpoint 2 - PullPush Non-AI Pipeline

Purpose:

Verify the reusable PullPush pipeline works end to end.

Command:

```bash
python tests/test_pullpush_pipeline.py
```

Optional one-run override:

```bash
REDDIT_TEST_USERNAME=Where_is_Gabriel REDDIT_TEST_SUBREDDITS=wallstreetbets REDDIT_TEST_SIZE_PER_SUBREDDIT=10 python3 tests/test_pullpush_pipeline.py
```

Expected output:

- PullPush request URLs are printed.
- PullPush status codes are printed, ideally `200`.
- The selected test username is printed.
- The selected test subreddit list is printed.
- A `Pipeline summary` section is printed.
- Summary includes `Submissions: ...`.
- Summary includes `Comments: ...`.
- Summary includes `Normalized items: ...`.
- Summary includes `Claim candidates: ...`.
- Saved paths include raw PullPush JSON in `data/raw/`.
- Saved paths include normalized JSON in `data/processed/`.
- Saved paths include claim candidate JSON in `data/processed/`.
- The script prints up to 10 claim candidates.
- Candidate previews include item type.
- Candidate previews include created timestamp.
- Candidate previews include candidate reason with possible tickers and matched keywords.
- Candidate previews include text preview.
- Candidate previews include permalink.

Good signs:

- At least one of submissions/comments is greater than zero.
- Normalized item count equals submissions plus comments.
- Candidate count may be zero or greater; if zero, inspect the normalized JSON before changing heuristics.
- Candidate text may include finance language such as Tesla, buying the dip, bullish/bearish comments, forecasts, calls, puts, rallies, dumps, pumps, or price movement language.

If this fails:

- If imports fail, run from the repo root.
- If PullPush status is not `200`, wait and rerun.
- If JSON files are not saved, check `data/raw/` and `data/processed/` permissions.
- If candidate count looks wrong, inspect the saved normalized JSON before editing filters.

## Checkpoint 3 - Manual Review CSV Export

Purpose:

Convert the newest saved claim candidate JSON file into a review-friendly CSV.

Command:

```bash
python tests/test_export_claim_candidates_csv.py
```

Expected output:

- The input claim candidate JSON path is printed.
- The output review CSV path is printed.
- The row count is printed.
- The CSV is saved under `data/processed/`.
- CSV columns include `item_type`, `author`, `subreddit`, `created_at`, `text`, `permalink`, `possible_tickers`, `matched_keywords`, `manual_status`, and `manual_notes`.
- `manual_status` is empty by default.
- `manual_notes` is empty by default.

Good signs:

- Row count matches the number of items in the selected claim candidate JSON file.
- `possible_tickers` and `matched_keywords` are readable text columns.
- The script creates a new timestamped CSV path instead of modifying the source JSON.

If this fails:

- If no claim candidate JSON is found, run `python tests/test_pullpush_pipeline.py` first.
- If imports fail, run from the repo root.
- If row count is zero, inspect the selected input JSON before changing the exporter.

## Checkpoint 4 - Existing Unit Tests

Purpose:

Confirm existing tests still pass after small changes.

Command:

```bash
.venv/bin/python -m pytest
```

Expected output:

- Pytest starts from the project root.
- The existing test suite passes.

Current known result:

```text
8 passed
```

Notes:

- `tests/test_pullpush_pipeline.py` is a manual integration script with a `main()` guard. It should not perform network work during normal pytest collection.
- Network checks should be run manually with `python tests/test_pullpush_pipeline.py`.

## Manual Test Settings

Purpose:

Let manual scripts use another username or subreddit without editing Python files.

Bash one-run example:

```bash
REDDIT_TEST_USERNAME=SomeRedditUser REDDIT_TEST_SUBREDDITS=wallstreetbets python3 tests/test_pullpush_pipeline.py
```

Persistent `.env` example:

```text
REDDIT_TEST_USERNAME=SomeRedditUser
REDDIT_TEST_SUBREDDITS=wallstreetbets
REDDIT_TEST_SIZE_PER_SUBREDDIT=10
```

Defaults:

- `REDDIT_TEST_USERNAME` defaults to `Where_is_Gabriel`.
- `REDDIT_TEST_SUBREDDITS` defaults to `wallstreetbets`.
- `REDDIT_TEST_SIZE_PER_SUBREDDIT` defaults to `10`.

## Command To Run After This Manual Review Export Step

Run:

```bash
python tests/test_export_claim_candidates_csv.py
```

Expected:

- The newest claim candidate JSON path is printed.
- A new review CSV path under `data/processed/` is printed.
- The exported row count is printed.
