from __future__ import annotations

from statistics import mean

from reddit_credibility.schemas import ScoreBreakdown, ValidatedClaim


def score_claims(claims: list[ValidatedClaim]) -> ScoreBreakdown:
    evaluated = [claim for claim in claims if claim.validation_status == "validated"]
    skipped_count = len([claim for claim in claims if claim.validation_status == "skipped"])

    if not evaluated:
        return ScoreBreakdown(
            evaluated_claims=0,
            skipped_claims=skipped_count,
            hit_rate_score=0,
            average_excess_return_score=0,
            specificity_score=0,
            sample_size_confidence=0,
            red_flag_adjustment=100,
            credibility_score=10,
        )

    hit_rate_score = 100 * mean(1 if claim.selected_hit else 0 for claim in evaluated)
    average_excess = mean(claim.selected_excess_return or 0 for claim in evaluated)
    average_excess_return_score = _score_average_excess_return(average_excess)
    specificity_score = 100 * mean(_claim_specificity(claim) for claim in evaluated)
    sample_size_confidence = min(len(evaluated) / 20, 1) * 100
    red_flag_adjustment = _score_red_flags(evaluated)

    credibility_score = (
        0.35 * hit_rate_score
        + 0.25 * average_excess_return_score
        + 0.20 * specificity_score
        + 0.10 * sample_size_confidence
        + 0.10 * red_flag_adjustment
    )

    return ScoreBreakdown(
        evaluated_claims=len(evaluated),
        skipped_claims=skipped_count,
        hit_rate_score=round(hit_rate_score, 2),
        average_excess_return_score=round(average_excess_return_score, 2),
        specificity_score=round(specificity_score, 2),
        sample_size_confidence=round(sample_size_confidence, 2),
        red_flag_adjustment=round(red_flag_adjustment, 2),
        credibility_score=round(credibility_score, 2),
    )


def _score_average_excess_return(average_excess_return: float) -> float:
    capped = max(min(average_excess_return, 0.20), -0.20)
    return 50 + (capped / 0.20) * 50


def _claim_specificity(claim: ValidatedClaim) -> float:
    points = 0
    points += 1 if claim.ticker else 0
    points += 1 if claim.direction else 0
    points += 1 if claim.time_horizon_days else 0
    points += 1 if claim.target_price is not None else 0
    return points / 4


def _score_red_flags(claims: list[ValidatedClaim]) -> float:
    high_confidence_misses = [
        claim
        for claim in claims
        if claim.ai_confidence >= 0.8
        and claim.selected_hit is False
        and (claim.selected_excess_return or 0) <= -0.10
    ]
    penalty = 25 * len(high_confidence_misses)
    return max(0, 100 - penalty)
