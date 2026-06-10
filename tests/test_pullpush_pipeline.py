from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from reddit_credibility.claim_candidate_filter import filter_claim_candidates
from reddit_credibility.json_store import save_json, utc_now_slug
from reddit_credibility.normalizer import normalize_items
from reddit_credibility.pullpush_client import fetch_user_activity


load_dotenv()

USERNAME = os.getenv("REDDIT_TEST_USERNAME", "Where_is_Gabriel")
SUBREDDITS = [
    subreddit.strip()
    for subreddit in os.getenv("REDDIT_TEST_SUBREDDITS", "wallstreetbets").split(",")
    if subreddit.strip()
]
SIZE_PER_SUBREDDIT = int(os.getenv("REDDIT_TEST_SIZE_PER_SUBREDDIT", "10"))


def preview_text(value: str, limit: int = 240) -> str:
    compact = " ".join((value or "").split())
    return compact[:limit]


def main() -> None:
    slug = utc_now_slug()

    print("Test username:", USERNAME)
    print("Test subreddits:", ", ".join(SUBREDDITS))
    print("Size per subreddit:", SIZE_PER_SUBREDDIT)

    activity = fetch_user_activity(
        username=USERNAME,
        subreddits=SUBREDDITS,
        size_per_subreddit=SIZE_PER_SUBREDDIT,
    )
    submissions = activity["submissions"]
    comments = activity["comments"]
    normalized = normalize_items(submissions=submissions, comments=comments)
    candidates = filter_claim_candidates(normalized)

    raw_path = save_json(
        activity,
        PROJECT_ROOT / "data" / "raw" / f"{USERNAME}_pullpush_raw_{slug}.json",
    )
    normalized_path = save_json(
        normalized,
        PROJECT_ROOT / "data" / "processed" / f"{USERNAME}_normalized_{slug}.json",
    )
    candidates_path = save_json(
        candidates,
        PROJECT_ROOT / "data" / "processed" / f"{USERNAME}_claim_candidates_{slug}.json",
    )

    print("\nPipeline summary")
    print("Submissions:", len(submissions))
    print("Comments:", len(comments))
    print("Normalized items:", len(normalized))
    print("Claim candidates:", len(candidates))
    print("Raw JSON:", raw_path)
    print("Normalized JSON:", normalized_path)
    print("Claim candidates JSON:", candidates_path)

    print("\nFirst 10 claim candidates")
    for index, item in enumerate(candidates[:10], start=1):
        print("-" * 80)
        print(f"Candidate {index}")
        print("Type:", item.get("item_type"))
        print("Created at:", item.get("created_at"))
        print("Reason:", item.get("candidate_reason"))
        print("Text:", preview_text(item.get("text", "")))
        print("Permalink:", item.get("permalink"))


if __name__ == "__main__":
    main()
