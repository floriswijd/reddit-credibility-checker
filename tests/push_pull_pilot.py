import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException, Timeout


load_dotenv()

USERNAME = os.getenv("REDDIT_TEST_USERNAME", "Where_is_Gabriel")
SUBREDDIT = os.getenv("REDDIT_TEST_SUBREDDITS", "wallstreetbets").split(",")[0].strip()
SIZE_PER_SUBREDDIT = int(os.getenv("REDDIT_TEST_SIZE_PER_SUBREDDIT", "10"))

BASE_URLS = {
    "comments": "https://api.pullpush.io/reddit/search/comment/",
    "submissions": "https://api.pullpush.io/reddit/search/submission/",
}


def parse_created_utc(value):
    if not value:
        return None

    try:
        timestamp = int(float(value))
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
    except (ValueError, TypeError):
        return None


def fetch_pullpush(kind, username, subreddit=None, size=10, retries=3, timeout=60):
    url = BASE_URLS[kind]

    params = {
        "author": username,
        "size": size,
        "sort": "desc",
        "sort_type": "created_utc",
    }

    if subreddit:
        params["subreddit"] = subreddit

    headers = {
        "User-Agent": "reddit-credibility-checker/0.1"
    }

    for attempt in range(1, retries + 1):
        try:
            print(f"Poging {attempt}: {kind} ophalen...")
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
            )

            print("URL:", response.url)
            print("Status code:", response.status_code)

            response.raise_for_status()
            return response.json().get("data", [])

        except Timeout:
            print(f"Timeout bij poging {attempt}. PullPush reageert te traag.")

        except RequestException as e:
            print(f"Request fout bij poging {attempt}: {e}")

        if attempt < retries:
            wait_time = attempt * 5
            print(f"{wait_time} seconden wachten en opnieuw proberen...\n")
            time.sleep(wait_time)

    return []


def print_submission(post):
    print("Type: submission")
    print("Subreddit:", post.get("subreddit"))
    print("Date:", parse_created_utc(post.get("created_utc")))
    print("Title:", post.get("title"))
    print("Text:", (post.get("selftext") or "")[:500])
    print("Permalink:", post.get("permalink"))
    print("-" * 80)


def print_comment(comment):
    print("Type: comment")
    print("Subreddit:", comment.get("subreddit"))
    print("Date:", parse_created_utc(comment.get("created_utc")))
    print("Body:", (comment.get("body") or "")[:500])
    print("Permalink:", comment.get("permalink"))
    print("-" * 80)


def main():
    submissions = fetch_pullpush(
        kind="submissions",
        username=USERNAME,
        subreddit=SUBREDDIT,
        size=SIZE_PER_SUBREDDIT,
    )

    print(f"\nAantal submissions gevonden: {len(submissions)}\n")

    for post in submissions[:10]:
        print_submission(post)

    comments = fetch_pullpush(
        kind="comments",
        username=USERNAME,
        subreddit=SUBREDDIT,
        size=SIZE_PER_SUBREDDIT,
    )

    print(f"\nAantal comments gevonden: {len(comments)}\n")

    for comment in comments[:10]:
        print_comment(comment)


if __name__ == "__main__":
    main()
