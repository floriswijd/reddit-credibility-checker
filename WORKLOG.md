# Worklog

This file tracks what changed, why it changed, and what should be checked next.

## Current Phase

Current phase: **Phase 1 - PullPush prototype pipeline**

The active goal is to stabilize a simple non-AI workflow:

```text
PullPush fetch -> normalize items -> save JSON -> filter claim candidates -> inspect output
```

## Entries

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
