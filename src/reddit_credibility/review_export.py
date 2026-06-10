from __future__ import annotations

import csv
from pathlib import Path


REVIEW_COLUMNS = [
    "item_type",
    "author",
    "subreddit",
    "created_at",
    "text",
    "permalink",
    "possible_tickers",
    "matched_keywords",
    "manual_status",
    "manual_notes",
]


def claim_candidate_to_review_row(candidate: dict) -> dict[str, str]:
    reason = candidate.get("candidate_reason") or {}
    return {
        "item_type": _string(candidate.get("item_type")),
        "author": _string(candidate.get("author")),
        "subreddit": _string(candidate.get("subreddit")),
        "created_at": _string(candidate.get("created_at")),
        "text": _string(candidate.get("text")),
        "permalink": _string(candidate.get("permalink")),
        "possible_tickers": _join_values(reason.get("possible_tickers")),
        "matched_keywords": _join_values(reason.get("matched_keywords")),
        "manual_status": "",
        "manual_notes": "",
    }


def export_claim_candidates_csv(candidates: list[dict], output_path: str | Path) -> int:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [claim_candidate_to_review_row(candidate) for candidate in candidates]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def _join_values(value: object) -> str:
    if not isinstance(value, list):
        return ""
    return "; ".join(_string(item) for item in value if _string(item))


def _string(value: object) -> str:
    if value is None:
        return ""
    return str(value)
