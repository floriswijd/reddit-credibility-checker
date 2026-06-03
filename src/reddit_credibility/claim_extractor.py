from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from reddit_credibility.config import Settings
from reddit_credibility.schemas import ExtractedClaim, RedditItem

logger = logging.getLogger(__name__)


CLAIM_RESPONSE_SCHEMA: dict[str, Any] = {
    "name": "stock_claim_extraction",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "ticker": {"type": ["string", "null"]},
                        "claim_text": {"type": "string"},
                        "claim_type": {"type": "string", "enum": ["direction", "price", "other"]},
                        "direction": {"type": ["string", "null"], "enum": ["bullish", "bearish", None]},
                        "target_price": {"type": ["number", "null"]},
                        "time_horizon_days": {"type": ["integer", "null"], "minimum": 1},
                        "measurable": {"type": "boolean"},
                        "ai_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                    "required": [
                        "ticker",
                        "claim_text",
                        "claim_type",
                        "direction",
                        "target_price",
                        "time_horizon_days",
                        "measurable",
                        "ai_confidence",
                    ],
                },
            }
        },
        "required": ["claims"],
    },
    "strict": True,
}


def load_prompt(path: Path = Path("prompts/claim_extraction.md")) -> str:
    return path.read_text(encoding="utf-8")


def extract_claims_for_items(settings: Settings, items: list[RedditItem]) -> list[ExtractedClaim]:
    settings.require_openai()
    client = _build_openai_client(settings)
    prompt = load_prompt()
    claims: list[ExtractedClaim] = []

    for item in items:
        try:
            claims.extend(_extract_claims_for_item(client, settings.openai_model, prompt, item))
        except Exception as exc:  # noqa: BLE001 - keep extraction robust across bad posts.
            logger.warning("Skipping claim extraction for Reddit item %s: %s", item.reddit_id, exc)

    return claims


def _build_openai_client(settings: Settings):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Missing dependency openai. Install dependencies with pip install -e .") from exc

    return OpenAI(api_key=settings.openai_api_key)


def _extract_claims_for_item(
    client: object, model: str, prompt: str, item: RedditItem
) -> list[ExtractedClaim]:
    user_payload = {
        "username": item.username,
        "reddit_id": item.reddit_id,
        "created_at": item.created_at.isoformat(),
        "subreddit": item.subreddit,
        "text": item.body,
    }
    response = client.chat.completions.create(  # type: ignore[attr-defined]
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        response_format={"type": "json_schema", "json_schema": CLAIM_RESPONSE_SCHEMA},
        temperature=0,
    )
    content = response.choices[0].message.content
    payload = json.loads(content or "{}")
    extracted: list[ExtractedClaim] = []
    for row in payload.get("claims", []):
        try:
            extracted.append(
                ExtractedClaim(
                    username=item.username,
                    reddit_id=item.reddit_id,
                    created_at=item.created_at,
                    subreddit=item.subreddit,
                    **row,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping malformed claim for Reddit item %s: %s", item.reddit_id, exc)
    return extracted
