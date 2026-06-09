from __future__ import annotations

import time
from typing import Literal

import requests
from requests.exceptions import RequestException, Timeout

PullPushKind = Literal["comments", "submissions"]

BASE_URLS: dict[PullPushKind, str] = {
    "comments": "https://api.pullpush.io/reddit/search/comment/",
    "submissions": "https://api.pullpush.io/reddit/search/submission/",
}

HEADERS = {"User-Agent": "reddit-credibility-checker/0.1"}


def fetch_pullpush(
    kind: PullPushKind,
    username: str,
    subreddit: str | None = None,
    size: int = 25,
    retries: int = 3,
    timeout: int = 60,
) -> list[dict]:
    if kind not in BASE_URLS:
        raise ValueError('kind must be "comments" or "submissions"')

    params: dict[str, object] = {
        "author": username,
        "size": size,
        "sort": "desc",
        "sort_type": "created_utc",
    }
    if subreddit:
        params["subreddit"] = subreddit

    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: fetching PullPush {kind}...")
            response = requests.get(
                BASE_URLS[kind],
                params=params,
                headers=HEADERS,
                timeout=timeout,
            )
            print("URL:", response.url)
            print("Status code:", response.status_code)
            response.raise_for_status()

            payload = response.json()
            data = payload.get("data", []) if isinstance(payload, dict) else []
            return data if isinstance(data, list) else []

        except Timeout:
            print(f"Timeout on attempt {attempt}. PullPush responded too slowly.")
        except RequestException as exc:
            print(f"Request error on attempt {attempt}: {exc}")
        except ValueError as exc:
            print(f"JSON parse error on attempt {attempt}: {exc}")

        if attempt < retries:
            wait_time = attempt * 5
            print(f"Waiting {wait_time} seconds before retrying...\n")
            time.sleep(wait_time)

    return []


def fetch_user_activity(
    username: str,
    subreddits: list[str],
    size_per_subreddit: int = 25,
) -> dict[str, list[dict]]:
    submissions: list[dict] = []
    comments: list[dict] = []

    for subreddit in subreddits:
        submissions.extend(
            fetch_pullpush(
                kind="submissions",
                username=username,
                subreddit=subreddit,
                size=size_per_subreddit,
            )
        )
        comments.extend(
            fetch_pullpush(
                kind="comments",
                username=username,
                subreddit=subreddit,
                size=size_per_subreddit,
            )
        )

    return {"submissions": submissions, "comments": comments}
