from __future__ import annotations

from datetime import UTC, datetime
from html import unescape


def parse_created_utc(value: object) -> str | None:
    if value is None or value == "":
        return None

    try:
        timestamp = int(float(value))
        return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()
    except (TypeError, ValueError, OSError):
        return None


def clean_text(value: object) -> str:
    if value is None:
        return ""
    return unescape(str(value)).strip()


def normalize_submission(post: dict) -> dict:
    title = clean_text(post.get("title"))
    body = clean_text(post.get("selftext"))
    text = "\n\n".join(part for part in (title, body) if part)

    return {
        "source": "pullpush",
        "item_type": "submission",
        "reddit_id": str(post.get("id") or ""),
        "author": post.get("author"),
        "subreddit": post.get("subreddit"),
        "created_at": parse_created_utc(post.get("created_utc")),
        "title": title or None,
        "body": body,
        "text": text,
        "score": post.get("score"),
        "permalink": post.get("permalink"),
        "url": post.get("url"),
    }


def normalize_comment(comment: dict) -> dict:
    body = clean_text(comment.get("body"))

    return {
        "source": "pullpush",
        "item_type": "comment",
        "reddit_id": str(comment.get("id") or ""),
        "author": comment.get("author"),
        "subreddit": comment.get("subreddit"),
        "created_at": parse_created_utc(comment.get("created_utc")),
        "title": None,
        "body": body,
        "text": body,
        "score": comment.get("score"),
        "permalink": comment.get("permalink"),
        "link_id": comment.get("link_id"),
        "parent_id": comment.get("parent_id"),
    }


def normalize_items(submissions: list[dict], comments: list[dict]) -> list[dict]:
    items = [normalize_submission(post) for post in submissions]
    items.extend(normalize_comment(comment) for comment in comments)
    return items
