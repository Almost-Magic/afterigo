"""Ripple CRM — Rep Bias Brain Engine (Phase 2.4).

Profiles sales rep forecast bias by comparing stated probability vs actual outcomes.
Applies correction factor to future predictions.

Logic:
- Track stated_probability at each deal stage
- Compare to actual outcome (won/lost)
- Build bias profile: avg overestimate/underestimate
- Correction factor = actual_win_rate / avg_stated_probability
- "Rep says 80%. History-adjusted: 62%."
"""

from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rep_forecast import RepForecastHistory


async def get_bias_profile(db: AsyncSession) -> dict:
    """Calculate overall rep bias profile from forecast history."""

    # Get all forecasts
    result = await db.execute(
        select(RepForecastHistory).order_by(RepForecastHistory.recorded_at.desc())
    )
    forecasts = result.scalars().all()

    total = len(forecasts)
    if total == 0:
        return {
            "total_forecasts": 0,
            "closed_deals": 0,
            "avg_stated_probability": None,
            "avg_actual_win_rate": None,
            "bias_direction": None,
            "bias_magnitude": None,
            "correction_factor": None,
            "stage_bias": [],
            "confidence_level": "insufficient_data",
            "min_deals_for_reliable": 20,
        }

    # Split into closed (won/lost) and open
    closed = [f for f in forecasts if f.actual_outcome in ("won", "lost")]
    closed_count = len(closed)

    # Average stated probability across all forecasts
    avg_stated = sum(f.stated_probability for f in forecasts) / total

    # Actual win rate from closed deals
    won = [f for f in closed if f.actual_outcome == "won"]
    actual_win_rate = (len(won) / closed_count * 100) if closed_count > 0 else None

    # Bias calculation
    bias_direction = None
    bias_magnitude = None
    correction_factor = None

    if actual_win_rate is not None and closed_count >= 3:
        # Calculate bias from closed deals
        avg_stated_closed = sum(f.stated_probability for f in closed) / closed_count
        bias_magnitude = round(avg_stated_closed - actual_win_rate, 1)

        if bias_magnitude > 5:
            bias_direction = "optimistic"
        elif bias_magnitude < -5:
            bias_direction = "pessimistic"
            bias_magnitude = abs(bias_magnitude)
        else:
            bias_direction = "calibrated"
            bias_magnitude = abs(bias_magnitude)

        # Correction factor
        if avg_stated_closed > 0:
            correction_factor = round(actual_win_rate / avg_stated_closed, 3)
        else:
            correction_factor = 1.0

    # Confidence level
    if closed_count >= 20:
        confidence = "high"
    elif closed_count >= 10:
        confidence = "moderate"
    elif closed_count >= 3:
        confidence = "low"
    else:
        confidence = "insufficient_data"

    # Per-stage breakdown
    stage_data = defaultdict(lambda: {"total": 0, "won": 0, "lost": 0, "stated_probs": []})
    for f in closed:
        s = f.stage
        stage_data[s]["total"] += 1
        stage_data[s]["stated_probs"].append(f.stated_probability)
        if f.actual_outcome == "won":
            stage_data[s]["won"] += 1
        else:
            stage_data[s]["lost"] += 1

    stage_bias = []
    for stage, data in sorted(stage_data.items()):
        avg_sp = sum(data["stated_probs"]) / len(data["stated_probs"])
        actual_rate = (data["won"] / data["total"] * 100) if data["total"] > 0 else 0
        stage_bias.append({
            "stage": stage,
            "forecast_count": data["total"],
            "avg_stated_probability": round(avg_sp, 1),
            "actual_win_rate": round(actual_rate, 1),
            "bias": round(avg_sp - actual_rate, 1),
        })

    return {
        "total_forecasts": total,
        "closed_deals": closed_count,
        "avg_stated_probability": round(avg_stated, 1),
        "avg_actual_win_rate": round(actual_win_rate, 1) if actual_win_rate is not None else None,
        "bias_direction": bias_direction,
        "bias_magnitude": bias_magnitude,
        "correction_factor": correction_factor,
        "stage_bias": stage_bias,
        "confidence_level": confidence,
        "min_deals_for_reliable": 20,
    }


async def get_corrected_probability(
    db: AsyncSession, deal_id, stage: str, stated_probability: int
) -> dict:
    """Apply bias correction to a stated probability."""

    profile = await get_bias_profile(db)

    corrected = float(stated_probability)
    bias_applied = 0.0

    if profile["correction_factor"] is not None and profile["confidence_level"] != "insufficient_data":
        # Check if we have stage-specific data
        stage_match = next((s for s in profile["stage_bias"] if s["stage"] == stage), None)
        if stage_match and stage_match["forecast_count"] >= 3:
            # Use stage-specific correction
            if stage_match["avg_stated_probability"] > 0:
                stage_factor = stage_match["actual_win_rate"] / stage_match["avg_stated_probability"]
                corrected = stated_probability * stage_factor
            else:
                corrected = float(stated_probability)
        else:
            # Use overall correction factor
            corrected = stated_probability * profile["correction_factor"]

        bias_applied = round(stated_probability - corrected, 1)
        corrected = max(0, min(100, round(corrected, 1)))

    return {
        "deal_id": str(deal_id),
        "stage": stage,
        "stated_probability": stated_probability,
        "corrected_probability": corrected,
        "bias_applied": bias_applied,
        "confidence_level": profile["confidence_level"],
    }
