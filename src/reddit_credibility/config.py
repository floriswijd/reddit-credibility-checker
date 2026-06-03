from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is missing."""


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    default_benchmark: str
    finance_subreddits: set[str]
    reddit_client_id: str | None
    reddit_client_secret: str | None
    reddit_user_agent: str | None
    openai_api_key: str | None
    openai_model: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        subreddit_raw = os.getenv(
            "FINANCE_SUBREDDITS",
            "wallstreetbets,stocks,investing,SecurityAnalysis,pennystocks,options,StockMarket",
        )
        return cls(
            data_dir=Path(os.getenv("DATA_DIR", "data")),
            default_benchmark=os.getenv("DEFAULT_BENCHMARK", "SPY").upper(),
            finance_subreddits={
                subreddit.strip().lower()
                for subreddit in subreddit_raw.split(",")
                if subreddit.strip()
            },
            reddit_client_id=os.getenv("REDDIT_CLIENT_ID") or None,
            reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET") or None,
            reddit_user_agent=os.getenv("REDDIT_USER_AGENT") or None,
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )

    def require_reddit(self) -> None:
        missing = [
            name
            for name, value in {
                "REDDIT_CLIENT_ID": self.reddit_client_id,
                "REDDIT_CLIENT_SECRET": self.reddit_client_secret,
                "REDDIT_USER_AGENT": self.reddit_user_agent,
            }.items()
            if not value
        ]
        if missing:
            joined = ", ".join(missing)
            raise ConfigError(
                f"Missing Reddit configuration: {joined}. Copy .env.example to .env and fill in Reddit API credentials."
            )

    def require_openai(self) -> None:
        if not self.openai_api_key:
            raise ConfigError(
                "Missing OPENAI_API_KEY. Copy .env.example to .env and add an OpenAI API key."
            )


def load_settings() -> Settings:
    return Settings.from_env()
