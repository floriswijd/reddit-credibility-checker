from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Direction = Literal["bullish", "bearish"]
ClaimType = Literal["direction", "price", "other"]
ManualStatus = Literal["pending", "approved", "rejected"]


class RedditItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: str
    reddit_id: str
    kind: Literal["post", "comment"]
    created_at: datetime
    subreddit: str
    title: str | None = None
    body: str
    permalink: str | None = None
    url: str | None = None
    score: int | None = None

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_created_at(cls, value: object) -> datetime:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=UTC)
        if isinstance(value, int | float):
            return datetime.fromtimestamp(value, tz=UTC)
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        raise ValueError("created_at must be a datetime, ISO string, or unix timestamp")


class ExtractedClaim(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: str
    reddit_id: str
    created_at: datetime
    subreddit: str
    ticker: str | None = None
    claim_text: str
    claim_type: ClaimType
    direction: Direction | None = None
    target_price: float | None = None
    time_horizon_days: int | None = Field(default=None, ge=1)
    measurable: bool = False
    ai_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_created_at(cls, value: object) -> datetime:
        return RedditItem.parse_created_at(value)

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: object) -> str | None:
        if value is None:
            return None
        ticker = str(value).strip().upper().replace("$", "")
        return ticker or None

    @model_validator(mode="after")
    def force_unclear_claims_not_measurable(self) -> "ExtractedClaim":
        if not self.ticker or not self.direction or self.claim_type not in {"direction", "price"}:
            self.measurable = False
        return self


class ReviewedClaim(ExtractedClaim):
    manual_status: ManualStatus = "pending"
    manual_notes: str | None = None


class ValidatedClaim(ReviewedClaim):
    benchmark: str = "SPY"
    evaluation_window_days: int | None = None
    validation_status: Literal["validated", "skipped"] = "skipped"
    skipped_reason: str | None = None
    stock_return_30d: float | None = None
    benchmark_return_30d: float | None = None
    excess_return_30d: float | None = None
    hit_30d: bool | None = None
    stock_return_90d: float | None = None
    benchmark_return_90d: float | None = None
    excess_return_90d: float | None = None
    hit_90d: bool | None = None
    stock_return_180d: float | None = None
    benchmark_return_180d: float | None = None
    excess_return_180d: float | None = None
    hit_180d: bool | None = None
    selected_stock_return: float | None = None
    selected_benchmark_return: float | None = None
    selected_excess_return: float | None = None
    selected_hit: bool | None = None


class ScoreBreakdown(BaseModel):
    evaluated_claims: int
    skipped_claims: int
    hit_rate_score: float
    average_excess_return_score: float
    specificity_score: float
    sample_size_confidence: float
    red_flag_adjustment: float
    credibility_score: float
