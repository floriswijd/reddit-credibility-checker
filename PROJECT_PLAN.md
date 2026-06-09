# Project Plan

## Project

`reddit-credibility-checker` is a local-first Python project for analyzing public Reddit finance and investing posts/comments.

The MVP will eventually help review historical stock-related claims made by Reddit users, but the current phase is intentionally narrower: fetch public Reddit activity from PullPush, normalize it, save JSON, and identify possible claim candidates with simple non-AI heuristics.

This project is not investment advice. It does not recommend buying or selling anything.

## Current Phase

Current phase: **Phase 1 - PullPush prototype pipeline**

We are working on a clean, reusable, non-AI pipeline around the PullPush prototype.

Active test data:

- Username: `Where_is_Gabriel`
- Subreddit: `wallstreetbets`
- Prototype source: PullPush
- Known working pilot: `tests/push_pull_pilot.py`

## Current Scope

Phase 1 includes:

- PullPush fetching for submissions and comments.
- Reddit item normalization into one shared JSON-friendly shape.
- JSON save/load helpers.
- Simple claim candidate filtering with ticker and keyword heuristics.
- Manual integration scripts that print counts, saved paths, and previews.

Phase 1 does not include:

- OpenAI or AI extraction.
- API keys.
- Databases.
- FastAPI.
- Market data.
- Scoring.
- Frontend.
- Authentication.
- Payments.

## Existing Structure

Keep the current package structure:

```text
src/
  reddit_credibility/
tests/
prompts/
data/
```

Do not rename the project, move files, or recreate the repo from scratch.

## Built So Far

Confirmed existing pieces:

- `tests/push_pull_pilot.py` fetches PullPush submissions and comments for `Where_is_Gabriel` in `wallstreetbets`.
- `src/reddit_credibility/pullpush_client.py` provides reusable PullPush fetching.
- `src/reddit_credibility/normalizer.py` converts PullPush submissions/comments into a shared item format.
- `src/reddit_credibility/json_store.py` saves and loads JSON.
- `src/reddit_credibility/claim_candidate_filter.py` finds simple ticker/keyword claim candidates.
- `tests/test_pullpush_pipeline.py` runs the non-AI PullPush pipeline manually and saves JSON output.

There are also older scaffold files for future phases, including AI extraction, scoring, market data, report generation, and database-shaped helpers. These are out of scope for the current phase and should not be expanded until the PullPush pipeline is stable.

## Still To Build In Phase 1

- Manually run and inspect `tests/test_pullpush_pipeline.py`.
- Confirm saved raw JSON, normalized JSON, and claim candidate JSON are useful.
- Tighten normalization only if real PullPush output shows missing or messy fields.
- Tighten claim candidate heuristics only after reviewing false positives and false negatives.
- Add small unit tests for the PullPush client, normalizer, JSON store, and claim candidate filter if needed.

## Later Phases

Phase 2: Manual review export

- Convert claim candidates into a review-friendly CSV.
- Add `manual_status` and `manual_notes`.
- Keep review deterministic and non-AI.

Phase 3: Claim extraction design

- Decide whether AI extraction is needed.
- If added, keep AI limited to extraction only.
- Do not use AI for validation, scoring, or final credibility results.

Phase 4: Market validation

- Fetch historical price data.
- Validate only approved, measurable claims.
- Use deterministic Python calculations.

Phase 5: Reports

- Generate a simple Markdown report.
- Keep report transparent and inspectable.

## Development Workflow

Before coding:

1. Read `PROJECT_PLAN.md`.
2. Read `WORKLOG.md`.
3. Read `CHECKPOINTS.md`.
4. Inspect existing files.
5. State which phase is active.

While coding:

1. Make the smallest possible change.
2. Do not add unrelated features.
3. Keep code simple and testable.
4. Prefer reusable functions over one-off script logic only when the function is already needed.

After coding:

1. Update `WORKLOG.md`.
2. Update `CHECKPOINTS.md` if a new manual test is added.
3. Tell the user exactly which command to run.
4. Tell the user exactly what output to expect.
