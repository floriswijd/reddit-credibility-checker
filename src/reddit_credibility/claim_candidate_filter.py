from __future__ import annotations

import re

KEYWORDS = [
    "buy",
    "sell",
    "hold",
    "bullish",
    "bearish",
    "dip",
    "calls",
    "puts",
    "short",
    "long",
    "yolo",
    "moon",
    "crash",
    "undervalued",
    "overvalued",
    "earnings",
    "revenue",
    "profit",
    "forecast",
    "price target",
    "up",
    "down",
    "higher",
    "lower",
    "beat",
    "miss",
    "rally",
    "dump",
    "pump",
]

TICKER_PATTERN = re.compile(r"(?<![A-Za-z0-9])\$?([A-Z]{2,5})(?![A-Za-z0-9])")
KEYWORD_PATTERNS = {
    keyword: re.compile(rf"(?<![A-Za-z]){re.escape(keyword)}(?![A-Za-z])", re.IGNORECASE)
    for keyword in KEYWORDS
}


def extract_possible_tickers(text: str | None) -> list[str]:
    if not text:
        return []
    tickers = {match.group(1) for match in TICKER_PATTERN.finditer(text)}
    return sorted(tickers)


def is_claim_candidate(item: dict) -> bool:
    text = item.get("text") or ""
    return bool(extract_possible_tickers(text) and _matched_keywords(text))


def filter_claim_candidates(items: list[dict]) -> list[dict]:
    candidates: list[dict] = []

    for item in items:
        text = item.get("text") or ""
        possible_tickers = extract_possible_tickers(text)
        matched_keywords = _matched_keywords(text)
        if not possible_tickers or not matched_keywords:
            continue

        candidate = dict(item)
        candidate["candidate_reason"] = {
            "possible_tickers": possible_tickers,
            "matched_keywords": matched_keywords,
        }
        candidates.append(candidate)

    return candidates


def _matched_keywords(text: str) -> list[str]:
    return [
        keyword
        for keyword, pattern in KEYWORD_PATTERNS.items()
        if pattern.search(text)
    ]
