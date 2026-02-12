"""Ripple CRM — Relationship Health Score calculator (Heuristic v1).

Scores 0-100 based on five weighted factors:
  - Recency of last interaction:    30%
  - Frequency vs baseline:          25%
  - Sentiment trend (last 10):      20%
  - Commitment fulfilment ratio:    15%
  - Response pattern:               10%
"""

from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment
from app.models.contact import Contact
from app.models.interaction import Interaction


async def calculate_health_score(db: AsyncSession, contact_id) -> dict:
    """Calculate relationship health for a single contact. Returns dict with
    score, components, trust_decay_days, and label."""

    # Fetch recent interactions (last 50)
    result = await db.execute(
        select(Interaction)
        .where(Interaction.contact_id == contact_id)
        .order_by(Interaction.occurred_at.desc())
        .limit(50)
    )
    interactions = result.scalars().all()

    # Fetch commitments
    result = await db.execute(
        select(Commitment).where(Commitment.contact_id == contact_id)
    )
    commitments = result.scalars().all()

    now = datetime.now(timezone.utc)
    today = date.today()

    # ── Recency Score (30%) ──────────────────────────────────────────────
    if interactions:
        last_interaction = interactions[0].occurred_at
        if last_interaction.tzinfo is None:
            from datetime import timezone as tz
            last_interaction = last_interaction.replace(tzinfo=tz.utc)
        days_since = (now - last_interaction).days
        # 0 days = 100, 7 days = 85, 30 days = 50, 90 days = 10, 180+ = 0
        if days_since <= 7:
            recency_score = 100 - (days_since * 2)
        elif days_since <= 30:
            recency_score = 85 - ((days_since - 7) * 1.5)
        elif days_since <= 90:
            recency_score = 50 - ((days_since - 30) * 0.67)
        else:
            recency_score = max(0, 10 - ((days_since - 90) * 0.11))
    else:
        days_since = None
        recency_score = 0

    # ── Frequency Score (25%) ────────────────────────────────────────────
    if len(interactions) >= 2:
        oldest = interactions[-1].occurred_at
        if oldest.tzinfo is None:
            from datetime import timezone as tz
            oldest = oldest.replace(tzinfo=tz.utc)
        span_days = max((now - oldest).days, 1)
        avg_gap = span_days / len(interactions)
        # Ideal gap is 7-14 days. Score penalises both too frequent and too rare.
        if avg_gap <= 3:
            frequency_score = 80  # very frequent — slight concern about over-contact
        elif avg_gap <= 14:
            frequency_score = 100  # sweet spot
        elif avg_gap <= 30:
            frequency_score = 70
        elif avg_gap <= 60:
            frequency_score = 40
        else:
            frequency_score = max(0, 20 - (avg_gap - 60) * 0.3)
        baseline_gap = avg_gap
    else:
        frequency_score = 0 if not interactions else 30
        baseline_gap = None

    # ── Sentiment Score (20%) ────────────────────────────────────────────
    recent_10 = interactions[:10]
    sentiments = [i.sentiment_score for i in recent_10 if i.sentiment_score is not None]
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        # Map -1..1 to 0..100
        sentiment_score = max(0, min(100, (avg_sentiment + 1) * 50))
    else:
        sentiment_score = 50  # neutral when no data

    # ── Commitment Score (15%) ───────────────────────────────────────────
    if commitments:
        total_c = len(commitments)
        fulfilled = sum(1 for c in commitments if c.status == "fulfilled")
        broken = sum(1 for c in commitments if c.status == "broken")
        commitment_score = max(0, (fulfilled / total_c) * 100 - (broken / total_c) * 30)
    else:
        commitment_score = 50  # neutral when no commitments

    # ── Response Pattern Score (10%) ─────────────────────────────────────
    # Simple heuristic: if there are recent interactions, we assume engagement
    if len(interactions) >= 5:
        response_score = min(100, len(interactions) * 5)
    elif interactions:
        response_score = 40
    else:
        response_score = 0

    # ── Weighted Total ───────────────────────────────────────────────────
    total = (
        recency_score * 0.30
        + frequency_score * 0.25
        + sentiment_score * 0.20
        + commitment_score * 0.15
        + response_score * 0.10
    )
    total = round(min(100, max(0, total)), 1)

    # Trust decay
    trust_decay_days = days_since

    # Label
    if total >= 70:
        label = "Healthy"
    elif total >= 40:
        label = "Warning"
    else:
        label = "Critical"

    return {
        "score": total,
        "label": label,
        "trust_decay_days": trust_decay_days,
        "baseline_gap_days": round(baseline_gap, 1) if baseline_gap else None,
        "components": {
            "recency": round(recency_score, 1),
            "frequency": round(frequency_score, 1),
            "sentiment": round(sentiment_score, 1),
            "commitment": round(commitment_score, 1),
            "response": round(response_score, 1),
        },
    }


async def recalculate_all(db: AsyncSession) -> int:
    """Recalculate health scores for all non-deleted contacts. Returns count updated."""
    result = await db.execute(
        select(Contact.id).where(Contact.is_deleted == False)  # noqa: E712
    )
    contact_ids = result.scalars().all()

    count = 0
    for cid in contact_ids:
        health = await calculate_health_score(db, cid)
        await db.execute(
            select(Contact).where(Contact.id == cid)
        )
        result2 = await db.execute(select(Contact).where(Contact.id == cid))
        contact = result2.scalar_one_or_none()
        if contact:
            contact.relationship_health_score = health["score"]
            contact.trust_decay_days = health["trust_decay_days"]
            count += 1

    await db.commit()
    return count
