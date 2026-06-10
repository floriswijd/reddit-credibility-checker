# Worklog

This file tracks what changed, why it changed, and what should be checked next.

## Current Phase

Current phase: **Phase 1 - PullPush prototype pipeline**

The active goal is to stabilize a simple non-AI workflow:

```text
PullPush fetch -> normalize items -> save JSON -> filter claim candidates -> inspect output
```

## Entries

### 2026-06-10 - Manual PullPush test settings added

Changed:

- Updated `tests/push_pull_pilot.py` to read the test username, subreddit, and size from environment variables.
- Updated `tests/test_pullpush_pipeline.py` to read the test username, subreddits, and size from environment variables.
- Added non-secret manual test settings to `.env.example`.

Why:

- It should be easy to test another Reddit username without editing Python files.
- The default remains `Where_is_Gabriel` in `wallstreetbets`.
- Settings can now be supplied from bash for one run or from `.env` for repeated local testing.

Manual check to run next:

```bash
REDDIT_TEST_USERNAME=Where_is_Gabriel REDDIT_TEST_SUBREDDITS=wallstreetbets python3 tests/test_pullpush_pipeline.py
```

Expected output:

- The selected test username is printed.
- The selected test subreddit list is printed.
- PullPush request URLs and status codes are printed.
- Raw, normalized, and claim candidate JSON files are saved.

Notes:

- This step does not add AI, OpenAI, API keys, database, FastAPI, market data, scoring, or frontend.
- For repeated use, copy the manual test settings from `.env.example` into `.env` and edit the username there.

### 2026-06-10 - Manual review CSV export added

Changed:

- Added `src/reddit_credibility/review_export.py`.
- Added `tests/test_export_claim_candidates_csv.py`.
- Added a new manual checkpoint for exporting claim candidates to CSV.

Why:

- We are moving carefully from Phase 1 toward Phase 2.
- The next useful step is a human-reviewable CSV, not AI extraction or validation.
- The exporter keeps `manual_status` and `manual_notes` empty by default so review decisions remain manual.

Manual check to run next:

```bash
python tests/test_export_claim_candidates_csv.py
```

Expected output:

- The newest `*_claim_candidates_*.json` input path is printed.
- A timestamped review CSV path under `data/processed/` is printed.
- The exported row count is printed.

Notes:

- This step does not add AI, OpenAI, API keys, database, FastAPI, market data, scoring, or frontend.
- The script expects at least one claim candidate JSON file in `data/processed/`.
- If no claim candidate JSON exists, run `python tests/test_pullpush_pipeline.py` first.
- Verified locally with `python3 tests/test_export_claim_candidates_csv.py`; it exported 6 rows from the existing `Where_is_Gabriel` claim candidate JSON.
- Existing pytest suite still passes with `8 passed`.

### 2026-06-09 - Workflow documentation added

Changed:

- Added `PROJECT_PLAN.md`.
- Added `WORKLOG.md`.
- Added `CHECKPOINTS.md`.

Why:

- The project needed a clear step-by-step workflow before adding more code.
- Future coding turns should start by reading these files and naming the active phase.
- Manual test commands and expected outputs should live in one predictable place.

Manual check to run next:

```bash
python tests/test_pullpush_pipeline.py
```

Expected output:

- PullPush request URLs are printed.
- PullPush status codes are printed, ideally `200` when PullPush is available.
- Summary counts are printed for submissions, comments, normalized items, and claim candidates.
- Saved JSON paths are printed under `data/raw/` and `data/processed/`.
- Up to 10 claim candidate previews are printed.

Notes:

- This documentation-only step did not change Python code.
- Existing git status includes prior uncommitted work, including PullPush pipeline files and a deleted `tests/smalltest.py`; this documentation step did not address those.

### Current known built state

Built:

- PullPush pilot script: `tests/push_pull_pilot.py`.
- Reusable PullPush client: `src/reddit_credibility/pullpush_client.py`.
- Normalizer: `src/reddit_credibility/normalizer.py`.
- JSON store: `src/reddit_credibility/json_store.py`.
- Claim candidate filter: `src/reddit_credibility/claim_candidate_filter.py`.
- Manual pipeline script: `tests/test_pullpush_pipeline.py`.

Not active yet:

- OpenAI extraction.
- Database persistence.
- FastAPI.
- Market data validation.
- Frontend.
- Production scoring.

## How To Add Future Entries

Use this format:

### YYYY-MM-DD - Short title

Changed:

- ...

Why:

- ...

Manual check to run next:

```bash
command
```

Expected output:

- ...

Notes:

- ...
