from __future__ import annotations

import logging
from datetime import UTC, datetime

from reddit_credibility.config import Settings
from reddit_credibility.schemas import RedditItem

logger = logging.getLogger(__name__)


def _build_client(settings: Settings):
    try:
        import praw
    except ImportError as exc:
        raise RuntimeError("Missing dependency praw. Install dependencies with pip install -e .") from exc

    settings.require_reddit()
    return praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
    )


def fetch_user_items(settings: Settings, username: str, limit: int = 100) -> list[RedditItem]:
    reddit = _build_client(settings)
    redditor = reddit.redditor(username)
    items: list[RedditItem] = []

    for kind, listing in (
        ("post", redditor.submissions.new(limit=limit)),
        ("comment", redditor.comments.new(limit=limit)),
    ):
        for submission_or_comment in listing:
            if len(items) >= limit:
                break
            try:
                subreddit = str(submission_or_comment.subreddit).lower()
                if subreddit not in settings.finance_subreddits:
                    continue
                item = _to_reddit_item(username, kind, submission_or_comment)
                if item.body.strip():
                    items.append(item)
            except Exception as exc:  # noqa: BLE001 - one bad Reddit object should not stop the fetch.
                item_id = getattr(submission_or_comment, "id", "unknown")
                logger.warning("Skipping Reddit %s %s: %s", kind, item_id, exc)

    return items


def _to_reddit_item(username: str, kind: str, obj: object) -> RedditItem:
    created_at = datetime.fromtimestamp(float(getattr(obj, "created_utc")), tz=UTC)
    subreddit = str(getattr(obj, "subreddit"))
    title = getattr(obj, "title", None) if kind == "post" else None
    body = _body_for(kind, obj)
    return RedditItem(
        username=username,
        reddit_id=str(getattr(obj, "id")),
        kind=kind,  # type: ignore[arg-type]
        created_at=created_at,
        subreddit=subreddit,
        title=title,
        body=body,
        permalink=f"https://www.reddit.com{getattr(obj, 'permalink', '')}",
        url=getattr(obj, "url", None),
        score=getattr(obj, "score", None),
    )


def _body_for(kind: str, obj: object) -> str:
    if kind == "post":
        title = getattr(obj, "title", "") or ""
        selftext = getattr(obj, "selftext", "") or ""
        return f"{title}\n\n{selftext}".strip()
    return str(getattr(obj, "body", "") or "").strip()
