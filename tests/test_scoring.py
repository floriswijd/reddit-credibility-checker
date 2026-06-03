from reddit_credibility.schemas import ValidatedClaim
from reddit_credibility.scoring import score_claims


def _claim(hit: bool, excess: float, target_price: float | None = None) -> ValidatedClaim:
    return ValidatedClaim(
        username="alice",
        reddit_id="abc123",
        created_at="2024-01-01T00:00:00Z",
        subreddit="stocks",
        ticker="AAPL",
        claim_text="AAPL will beat SPY",
        claim_type="direction",
        direction="bullish",
        target_price=target_price,
        time_horizon_days=30,
        measurable=True,
        ai_confidence=0.7,
        manual_status="approved",
        validation_status="validated",
        evaluation_window_days=30,
        selected_excess_return=excess,
        selected_hit=hit,
    )


def test_score_claims_combines_weighted_components():
    scores = score_claims([_claim(True, 0.10, target_price=200), _claim(False, -0.05)])

    assert scores.evaluated_claims == 2
    assert scores.hit_rate_score == 50
    assert 0 < scores.credibility_score < 100


def test_score_empty_claims_is_low_confidence_not_crash():
    scores = score_claims([])

    assert scores.evaluated_claims == 0
    assert scores.credibility_score == 10
