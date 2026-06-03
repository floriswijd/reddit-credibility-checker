from datetime import UTC, datetime

import pandas as pd
import pytest

from reddit_credibility.market_data import (
    calculate_window_return,
    choose_evaluation_window,
    direction_adjusted_excess,
)


def test_calculate_window_return_uses_first_trading_day_on_or_after_dates():
    prices = pd.Series(
        [100.0, 110.0],
        index=pd.to_datetime(["2024-01-02", "2024-02-01"], utc=True),
    )

    result = calculate_window_return(
        prices,
        claim_date=datetime(2024, 1, 1, tzinfo=UTC),
        window_days=30,
    )

    assert result == pytest.approx(0.10)


def test_bearish_direction_flips_excess_return():
    assert direction_adjusted_excess(0.05, 0.10, "bearish") == 0.05


def test_choose_evaluation_window_picks_nearest_supported_window():
    assert choose_evaluation_window(100) == 90
