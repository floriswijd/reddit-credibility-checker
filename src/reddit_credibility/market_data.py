from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import pandas as pd

from reddit_credibility.schemas import ReviewedClaim, ValidatedClaim

logger = logging.getLogger(__name__)

VALIDATION_WINDOWS = (30, 90, 180)


def validate_reviewed_claims(
    claims: list[ReviewedClaim],
    benchmark: str = "SPY",
    as_of: datetime | None = None,
) -> list[ValidatedClaim]:
    as_of = as_of or datetime.now(tz=UTC)
    approved = [claim for claim in claims if claim.manual_status == "approved"]
    validated: list[ValidatedClaim] = []

    for claim in approved:
        try:
            validated.append(validate_claim(claim, benchmark=benchmark, as_of=as_of))
        except Exception as exc:  # noqa: BLE001 - keep one bad market lookup from stopping the run.
            logger.warning("Skipping validation for claim %s/%s: %s", claim.reddit_id, claim.ticker, exc)
            validated.append(
                ValidatedClaim(
                    **claim.model_dump(),
                    benchmark=benchmark,
                    validation_status="skipped",
                    skipped_reason=str(exc),
                )
            )
    return validated


def validate_claim(
    claim: ReviewedClaim, benchmark: str = "SPY", as_of: datetime | None = None
) -> ValidatedClaim:
    as_of = as_of or datetime.now(tz=UTC)
    base = ValidatedClaim(**claim.model_dump(), benchmark=benchmark)

    if not claim.measurable:
        return base.model_copy(update={"skipped_reason": "claim is not measurable"})
    if claim.claim_type not in {"direction", "price"}:
        return base.model_copy(update={"skipped_reason": "claim type is not validated in MVP"})
    if not claim.ticker or not claim.direction:
        return base.model_copy(update={"skipped_reason": "missing clear ticker or direction"})

    earliest_needed_days = min(VALIDATION_WINDOWS)
    if claim.created_at + timedelta(days=earliest_needed_days) > as_of:
        return base.model_copy(update={"skipped_reason": "claim is too recent to validate"})

    start = claim.created_at.date().isoformat()
    end = (claim.created_at + timedelta(days=max(VALIDATION_WINDOWS) + 10)).date().isoformat()
    stock_prices = fetch_adjusted_close(claim.ticker, start=start, end=end)
    benchmark_prices = fetch_adjusted_close(benchmark, start=start, end=end)

    updates: dict[str, object] = {}
    for window in VALIDATION_WINDOWS:
        if claim.created_at + timedelta(days=window) > as_of:
            continue
        stock_return = calculate_window_return(stock_prices, claim.created_at, window)
        benchmark_return = calculate_window_return(benchmark_prices, claim.created_at, window)
        if stock_return is None or benchmark_return is None:
            continue
        excess_return = direction_adjusted_excess(
            stock_return=stock_return,
            benchmark_return=benchmark_return,
            direction=claim.direction,
        )
        updates[f"stock_return_{window}d"] = stock_return
        updates[f"benchmark_return_{window}d"] = benchmark_return
        updates[f"excess_return_{window}d"] = excess_return
        updates[f"hit_{window}d"] = excess_return > 0

    evaluation_window = choose_evaluation_window(claim.time_horizon_days)
    selected_excess = updates.get(f"excess_return_{evaluation_window}d")
    if selected_excess is None:
        available = [window for window in VALIDATION_WINDOWS if updates.get(f"excess_return_{window}d") is not None]
        if not available:
            return base.model_copy(update={**updates, "skipped_reason": "not enough market data"})
        evaluation_window = available[0]

    updates.update(
        {
            "evaluation_window_days": evaluation_window,
            "validation_status": "validated",
            "skipped_reason": None,
            "selected_stock_return": updates.get(f"stock_return_{evaluation_window}d"),
            "selected_benchmark_return": updates.get(f"benchmark_return_{evaluation_window}d"),
            "selected_excess_return": updates.get(f"excess_return_{evaluation_window}d"),
            "selected_hit": updates.get(f"hit_{evaluation_window}d"),
        }
    )
    return base.model_copy(update=updates)


def fetch_adjusted_close(ticker: str, start: str, end: str) -> pd.Series:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Missing dependency yfinance. Install dependencies with pip install -e .") from exc

    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if data.empty:
        raise RuntimeError(f"No market data returned for {ticker}")

    if isinstance(data.columns, pd.MultiIndex):
        if ("Adj Close", ticker) in data.columns:
            series = data[("Adj Close", ticker)]
        else:
            series = data.xs("Adj Close", level=0, axis=1).iloc[:, 0]
    elif "Adj Close" in data.columns:
        series = data["Adj Close"]
    elif "Close" in data.columns:
        series = data["Close"]
    else:
        raise RuntimeError(f"No adjusted close data returned for {ticker}")

    series = series.dropna()
    series.index = pd.to_datetime(series.index, utc=True)
    return series


def calculate_window_return(prices: pd.Series, claim_date: datetime, window_days: int) -> float | None:
    if prices.empty:
        return None
    start_price = _first_price_on_or_after(prices, claim_date)
    end_price = _first_price_on_or_after(prices, claim_date + timedelta(days=window_days))
    if start_price is None or end_price is None or start_price == 0:
        return None
    return float((end_price / start_price) - 1)


def _first_price_on_or_after(prices: pd.Series, date: datetime) -> float | None:
    cutoff = pd.Timestamp(date).tz_convert("UTC") if pd.Timestamp(date).tzinfo else pd.Timestamp(date, tz="UTC")
    matches = prices[prices.index >= cutoff]
    if matches.empty:
        return None
    return float(matches.iloc[0])


def direction_adjusted_excess(stock_return: float, benchmark_return: float, direction: str) -> float:
    raw_excess = stock_return - benchmark_return
    if direction == "bearish":
        return -raw_excess
    return raw_excess


def choose_evaluation_window(time_horizon_days: int | None) -> int:
    if time_horizon_days is None:
        return 30
    return min(VALIDATION_WINDOWS, key=lambda window: abs(window - time_horizon_days))
