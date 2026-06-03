from __future__ import annotations

import argparse
import logging
from pathlib import Path

from reddit_credibility import database
from reddit_credibility.claim_extractor import extract_claims_for_items
from reddit_credibility.config import ConfigError, load_settings
from reddit_credibility.market_data import validate_reviewed_claims
from reddit_credibility.reddit_client import fetch_user_items
from reddit_credibility.report_generator import render_report
from reddit_credibility.scoring import score_claims


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reddit-credibility", description="Reddit Credibility Checker MVP")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Fetch recent finance-related Reddit posts/comments")
    fetch.add_argument("--username", required=True)
    fetch.add_argument("--limit", type=int, default=100)

    extract = subparsers.add_parser("extract", help="Extract concrete stock claims using an LLM")
    extract.add_argument("--username", required=True)

    export_review = subparsers.add_parser("export-review", help="Export extracted claims for manual review")
    export_review.add_argument("--username", required=True)

    validate = subparsers.add_parser("validate", help="Validate approved claims against market data")
    validate.add_argument("--username", required=True)
    validate.add_argument("--review-file", required=True)
    validate.add_argument("--benchmark", default=None)

    report = subparsers.add_parser("report", help="Generate a Markdown credibility report")
    report.add_argument("--username", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = load_settings()
    database.ensure_data_dirs(settings)

    try:
        if args.command == "fetch":
            return _fetch(args.username, args.limit, settings)
        if args.command == "extract":
            return _extract(args.username, settings)
        if args.command == "export-review":
            return _export_review(args.username, settings)
        if args.command == "validate":
            benchmark = (args.benchmark or settings.default_benchmark).upper()
            return _validate(args.username, Path(args.review_file), benchmark, settings)
        if args.command == "report":
            return _report(args.username, settings)
    except ConfigError as exc:
        parser.exit(2, f"Configuration error: {exc}\n")
    except RuntimeError as exc:
        parser.exit(2, f"Runtime error: {exc}\n")

    parser.exit(2, "Unknown command\n")
    return 2


def _fetch(username: str, limit: int, settings) -> int:
    items = fetch_user_items(settings, username=username, limit=limit)
    path = database.save_raw_items(settings, username, items)
    print(f"Saved {len(items)} Reddit items to {path}")
    return 0


def _extract(username: str, settings) -> int:
    items = database.load_raw_items(settings, username)
    if not items:
        raise RuntimeError(f"No raw Reddit items found for {username}. Run fetch first.")
    claims = extract_claims_for_items(settings, items)
    json_path, csv_path = database.save_claims(settings, username, claims)
    print(f"Saved {len(claims)} extracted claims to {json_path} and {csv_path}")
    return 0


def _export_review(username: str, settings) -> int:
    claims = database.load_claims(settings, username)
    if not claims:
        raise RuntimeError(f"No extracted claims found for {username}. Run extract first.")
    path = database.save_review_csv(settings, username, claims)
    print(f"Saved manual review CSV to {path}")
    return 0


def _validate(username: str, review_file: Path, benchmark: str, settings) -> int:
    reviewed = database.load_review_csv(review_file)
    if not reviewed:
        raise RuntimeError(f"No review rows found in {review_file}.")
    validated = validate_reviewed_claims(reviewed, benchmark=benchmark)
    path = database.save_validated_claims(settings, username, validated)
    print(f"Saved {len(validated)} validated claim rows to {path}")
    return 0


def _report(username: str, settings) -> int:
    validated = database.load_validated_claims(settings, username)
    if not validated:
        raise RuntimeError(f"No validated claims found for {username}. Run validate first.")
    scores = score_claims(validated)
    path = render_report(username, validated, scores, database.report_path(settings, username))
    print(f"Saved credibility report to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
