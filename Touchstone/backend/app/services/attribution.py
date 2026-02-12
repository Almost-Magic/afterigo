"""Touchstone — Attribution calculation engine.

Five models: first_touch, last_touch, linear, time_decay, position_based.
All weights sum to exactly 1.0 using Decimal precision.
"""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import delete, func, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.attribution import Attribution
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.touchpoint import Touchpoint


VALID_MODELS = ("first_touch", "last_touch", "linear", "time_decay", "position_based")


# ── Weight functions ─────────────────────────────────────────

def _first_touch_weights(count: int) -> list[Decimal]:
    """100% to the first touchpoint."""
    if count == 0:
        return []
    weights = [Decimal("0")] * count
    weights[0] = Decimal("1")
    return weights


def _last_touch_weights(count: int) -> list[Decimal]:
    """100% to the last touchpoint."""
    if count == 0:
        return []
    weights = [Decimal("0")] * count
    weights[-1] = Decimal("1")
    return weights


def _linear_weights(count: int) -> list[Decimal]:
    """Equal split. Last touchpoint absorbs rounding remainder."""
    if count == 0:
        return []
    base = Decimal("1") / Decimal(str(count))
    base = base.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    weights = [base] * count
    remainder = Decimal("1") - sum(weights)
    weights[-1] += remainder
    return weights


def _time_decay_weights(
    timestamps: list[datetime],
    closed_at: datetime,
    half_life_days: float = 7.0,
) -> list[Decimal]:
    """Exponential decay. Recent touchpoints get more credit.
    weight_raw = 2^(-(days_before_close / half_life))
    Then normalise so sum = 1.0.
    """
    count = len(timestamps)
    if count == 0:
        return []
    raw = []
    for ts in timestamps:
        days_before = max(0.0, (closed_at - ts).total_seconds() / 86400.0)
        raw_weight = 2.0 ** (-(days_before / half_life_days))
        raw.append(Decimal(str(raw_weight)))
    total = sum(raw)
    if total == 0:
        return _linear_weights(count)
    weights = []
    for r in raw:
        w = (r / total).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        weights.append(w)
    remainder = Decimal("1") - sum(weights)
    weights[-1] += remainder
    return weights


def _position_based_weights(count: int) -> list[Decimal]:
    """40% first, 40% last, 20% split across middle.
    1 touch = 100%. 2 touches = 50/50.
    """
    if count == 0:
        return []
    if count == 1:
        return [Decimal("1")]
    if count == 2:
        return [Decimal("0.5"), Decimal("0.5")]

    middle_count = count - 2
    middle_each = (Decimal("0.2") / Decimal(str(middle_count))).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )
    weights = [Decimal("0.4")]
    for _ in range(middle_count):
        weights.append(middle_each)
    weights.append(Decimal("0.4"))
    remainder = Decimal("1") - sum(weights)
    weights[-1] += remainder
    return weights


def compute_weights(model: str, touchpoints: list, closed_at: datetime) -> list[Decimal]:
    """Dispatch to the correct model function."""
    count = len(touchpoints)
    if model == "first_touch":
        return _first_touch_weights(count)
    elif model == "last_touch":
        return _last_touch_weights(count)
    elif model == "linear":
        return _linear_weights(count)
    elif model == "time_decay":
        timestamps = [tp.timestamp for tp in touchpoints]
        return _time_decay_weights(timestamps, closed_at)
    elif model == "position_based":
        return _position_based_weights(count)
    else:
        raise ValueError(f"Unknown model: {model}")


# ── Main calculation ─────────────────────────────────────────

async def calculate_attributions(
    db: AsyncSession,
    model: str,
    recalculate: bool = True,
) -> dict:
    """Run attribution for all won deals.

    Returns summary: {model, deals_processed, attributions_created, total_revenue_attributed}
    """
    if model not in VALID_MODELS:
        raise ValueError(f"Invalid model: {model}. Must be one of {VALID_MODELS}")

    if recalculate:
        await db.execute(delete(Attribution).where(Attribution.model == model))

    result = await db.execute(
        select(Deal).where(
            Deal.stage == "won",
            Deal.amount.isnot(None),
            Deal.amount > 0,
            Deal.closed_at.isnot(None),
            Deal.contact_id.isnot(None),
        )
    )
    deals = result.scalars().all()

    deals_processed = 0
    attributions_created = 0
    total_revenue = Decimal("0")

    for deal in deals:
        tp_result = await db.execute(
            select(Touchpoint)
            .where(
                Touchpoint.contact_id == deal.contact_id,
                Touchpoint.timestamp < deal.closed_at,
            )
            .order_by(Touchpoint.timestamp.asc())
        )
        touchpoints = tp_result.scalars().all()

        if not touchpoints:
            continue

        weights = compute_weights(model, touchpoints, deal.closed_at)

        for tp, weight in zip(touchpoints, weights):
            attr = Attribution(
                deal_id=deal.id,
                touchpoint_id=tp.id,
                campaign_id=tp.campaign_id,
                model=model,
                attribution_weight=weight,
                attributed_amount=(deal.amount * weight).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
            )
            db.add(attr)
            attributions_created += 1

        deals_processed += 1
        total_revenue += deal.amount

    await db.commit()

    return {
        "model": model,
        "deals_processed": deals_processed,
        "attributions_created": attributions_created,
        "total_revenue_attributed": total_revenue,
    }


# ── Aggregation queries ──────────────────────────────────────

async def get_campaign_attribution(
    db: AsyncSession,
    model: str,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    """Campaigns ranked by attributed revenue."""
    query = (
        select(
            Attribution.campaign_id,
            Campaign.name.label("campaign_name"),
            Campaign.channel,
            Campaign.budget,
            func.sum(Attribution.attributed_amount).label("attributed_revenue"),
            func.count(Attribution.id).label("touchpoint_count"),
            func.count(func.distinct(Attribution.deal_id)).label("deal_count"),
        )
        .outerjoin(Campaign, Attribution.campaign_id == Campaign.id)
        .where(Attribution.model == model)
    )

    if date_from:
        query = query.join(Deal, Attribution.deal_id == Deal.id).where(Deal.closed_at >= date_from)
    if date_to:
        if not date_from:
            query = query.join(Deal, Attribution.deal_id == Deal.id)
        query = query.where(Deal.closed_at <= date_to)

    query = query.group_by(
        Attribution.campaign_id, Campaign.name, Campaign.channel, Campaign.budget
    ).order_by(func.sum(Attribution.attributed_amount).desc())

    result = await db.execute(query)
    rows = result.all()

    items = []
    total = Decimal("0")
    for row in rows:
        revenue = row.attributed_revenue or Decimal("0")
        total += revenue
        budget = row.budget
        roi = None
        if budget and budget > 0:
            roi = ((revenue - budget) / budget * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        items.append({
            "campaign_id": row.campaign_id,
            "campaign_name": row.campaign_name or "(Direct / Unattributed)",
            "channel": row.channel,
            "attributed_revenue": revenue,
            "touchpoint_count": row.touchpoint_count,
            "deal_count": row.deal_count,
            "budget": budget,
            "roi": roi,
        })

    return {"model": model, "items": items, "total_attributed_revenue": total}


async def get_channel_attribution(
    db: AsyncSession,
    model: str,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    """Channels ranked by attributed revenue."""
    tp = aliased(Touchpoint)
    query = (
        select(
            tp.channel,
            func.sum(Attribution.attributed_amount).label("attributed_revenue"),
            func.count(Attribution.id).label("touchpoint_count"),
            func.count(func.distinct(Attribution.deal_id)).label("deal_count"),
        )
        .join(tp, Attribution.touchpoint_id == tp.id)
        .where(Attribution.model == model)
    )

    if date_from or date_to:
        query = query.join(Deal, Attribution.deal_id == Deal.id)
        if date_from:
            query = query.where(Deal.closed_at >= date_from)
        if date_to:
            query = query.where(Deal.closed_at <= date_to)

    query = query.group_by(tp.channel).order_by(
        func.sum(Attribution.attributed_amount).desc()
    )

    result = await db.execute(query)
    rows = result.all()

    items = []
    total = Decimal("0")
    for row in rows:
        revenue = row.attributed_revenue or Decimal("0")
        total += revenue
        items.append({
            "channel": row.channel or "unknown",
            "attributed_revenue": revenue,
            "touchpoint_count": row.touchpoint_count,
            "deal_count": row.deal_count,
        })

    # Calculate percentages
    for item in items:
        if total > 0:
            item["percentage"] = (item["attributed_revenue"] / total * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            item["percentage"] = Decimal("0")

    return {"model": model, "items": items, "total_attributed_revenue": total}


async def get_model_comparison(
    db: AsyncSession,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    """Side-by-side comparison of all 5 models by campaign."""
    campaigns_by_model = {}
    for model in VALID_MODELS:
        data = await get_campaign_attribution(db, model, date_from, date_to)
        for item in data["items"]:
            key = item["campaign_id"] or "direct"
            if key not in campaigns_by_model:
                campaigns_by_model[key] = {
                    "campaign_id": item["campaign_id"],
                    "campaign_name": item["campaign_name"],
                }
            campaigns_by_model[key][model] = item["attributed_revenue"]

    # Fill in zeros for missing models
    campaigns = []
    for row in campaigns_by_model.values():
        for m in VALID_MODELS:
            if m not in row:
                row[m] = Decimal("0")
        campaigns.append(row)

    # Sort by linear (default) descending
    campaigns.sort(key=lambda x: x.get("linear", Decimal("0")), reverse=True)

    return {"campaigns": campaigns}


async def get_contact_attribution(
    db: AsyncSession,
    contact_id: UUID,
    model: str | None = None,
) -> dict:
    """Attribution records for a contact's deals."""
    contact_result = await db.execute(
        select(Contact).where(Contact.id == contact_id).limit(1)
    )
    contact = contact_result.scalar_one_or_none()
    if not contact:
        return None

    query = (
        select(
            Attribution.deal_id,
            Deal.deal_name,
            Deal.amount.label("deal_amount"),
            Attribution.touchpoint_id,
            Touchpoint.timestamp.label("touchpoint_timestamp"),
            Touchpoint.channel,
            Touchpoint.source,
            Touchpoint.utm_campaign,
            Attribution.model,
            Attribution.attribution_weight,
            Attribution.attributed_amount,
        )
        .join(Deal, Attribution.deal_id == Deal.id)
        .join(Touchpoint, Attribution.touchpoint_id == Touchpoint.id)
        .where(Deal.contact_id == contact_id)
    )

    if model:
        query = query.where(Attribution.model == model)

    query = query.order_by(Attribution.model, Touchpoint.timestamp.asc())

    result = await db.execute(query)
    rows = result.all()

    items = []
    models_seen = set()
    total = Decimal("0")
    for row in rows:
        models_seen.add(row.model)
        amt = row.attributed_amount or Decimal("0")
        total += amt
        items.append({
            "deal_id": row.deal_id,
            "deal_name": row.deal_name,
            "deal_amount": row.deal_amount,
            "touchpoint_id": row.touchpoint_id,
            "touchpoint_timestamp": row.touchpoint_timestamp,
            "channel": row.channel,
            "source": row.source,
            "utm_campaign": row.utm_campaign,
            "model": row.model,
            "attribution_weight": row.attribution_weight,
            "attributed_amount": amt,
        })

    return {
        "contact_id": contact_id,
        "contact_name": contact.name,
        "models": sorted(models_seen),
        "items": items,
        "total_attributed": total,
    }
