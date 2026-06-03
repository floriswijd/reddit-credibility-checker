from pathlib import Path

from reddit_credibility import database
from reddit_credibility.config import Settings
from reddit_credibility.schemas import ExtractedClaim


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path,
        default_benchmark="SPY",
        finance_subreddits={"stocks"},
        reddit_client_id=None,
        reddit_client_secret=None,
        reddit_user_agent=None,
        openai_api_key=None,
        openai_model="gpt-4o-mini",
    )


def test_save_review_csv_adds_pending_manual_fields(tmp_path):
    settings = _settings(tmp_path)
    claim = ExtractedClaim(
        username="alice",
        reddit_id="abc123",
        created_at="2024-01-01T00:00:00Z",
        subreddit="stocks",
        ticker="AAPL",
        claim_text="AAPL will go up",
        claim_type="direction",
        direction="bullish",
        measurable=True,
        ai_confidence=0.75,
    )

    path = database.save_review_csv(settings, "alice", [claim])
    rows = database.load_review_csv(path)

    assert rows[0].manual_status == "pending"
    assert rows[0].manual_notes is None
