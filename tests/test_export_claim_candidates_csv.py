from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from reddit_credibility.json_store import load_json, utc_now_slug
from reddit_credibility.review_export import export_claim_candidates_csv


PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def newest_claim_candidates_file() -> Path:
    paths = list(PROCESSED_DIR.glob("*_claim_candidates_*.json"))
    if not paths:
        raise FileNotFoundError(
            "No claim candidate JSON files found in data/processed/. "
            "Run python tests/test_pullpush_pipeline.py first."
        )
    return max(paths, key=lambda path: path.stat().st_mtime)


def main() -> None:
    input_path = newest_claim_candidates_file()
    candidates = load_json(input_path)
    output_path = PROCESSED_DIR / f"{input_path.stem}_review_{utc_now_slug()}.csv"
    row_count = export_claim_candidates_csv(candidates, output_path)

    print("Input claim candidate JSON:", input_path)
    print("Output review CSV:", output_path)
    print("Rows exported:", row_count)


if __name__ == "__main__":
    main()
