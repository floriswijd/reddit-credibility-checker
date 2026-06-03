from reddit_credibility.schemas import ExtractedClaim


def test_ticker_is_normalized_and_dollar_removed():
    claim = ExtractedClaim(
        username="alice",
        reddit_id="abc123",
        created_at="2024-01-01T00:00:00Z",
        subreddit="stocks",
        ticker="$aapl",
        claim_text="AAPL goes up",
        claim_type="direction",
        direction="bullish",
        measurable=True,
        ai_confidence=0.8,
    )

    assert claim.ticker == "AAPL"
    assert claim.measurable is True


def test_claim_without_direction_is_forced_not_measurable():
    claim = ExtractedClaim(
        username="alice",
        reddit_id="abc123",
        created_at="2024-01-01T00:00:00Z",
        subreddit="stocks",
        ticker="MSFT",
        claim_text="MSFT is interesting",
        claim_type="other",
        direction=None,
        measurable=True,
        ai_confidence=0.5,
    )

    assert claim.measurable is False
