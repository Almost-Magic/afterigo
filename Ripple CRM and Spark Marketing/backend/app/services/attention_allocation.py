"""Ripple CRM — Attention Allocation Engine.

Compares time spent per contact (from interactions + meetings)
with revenue potential (from deals: value x probability) to
surface misallocated attention.

Thresholds:
  ratio > 1.5  → overallocated  (spending too much time relative to revenue)
  ratio < 0.67 → underallocated (spending too little time relative to revenue)
  else         → well_allocated
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.deal import Deal
from app.models.interaction import Interaction
from app.models.meeting import Meeting


def _classify(ratio: float | None) -> str:
    if ratio is None:
        return "no_deals"
    if ratio > 1.5:
        return "overallocated"
    if ratio < 0.67:
        return "underallocated"
    return "well_allocated"


async def get_attention_summary(db: AsyncSession, period_days: int = 30) -> dict:
    """Summary of attention allocation across all contacts."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=period_days)

    # ── 1. Time from interactions ─────────────────────────────────────
    int_result = await db.execute(
        select(
            Interaction.contact_id,
            func.coalesce(func.sum(Interaction.duration_minutes), 0).label("mins"),
        )
        .where(Interaction.occurred_at >= cutoff)
        .group_by(Interaction.contact_id)
    )
    time_map: dict[str, int] = {}
    for cid, mins in int_result.all():
        time_map[str(cid)] = int(mins)

    # ── 2. Time from meetings ─────────────────────────────────────────
    mtg_result = await db.execute(
        select(
            Meeting.contact_id,
            func.coalesce(func.sum(Meeting.duration_minutes), 0).label("mins"),
        )
        .where(Meeting.scheduled_at >= cutoff)
        .group_by(Meeting.contact_id)
    )
    for cid, mins in mtg_result.all():
        key = str(cid)
        time_map[key] = time_map.get(key, 0) + int(mins)

    # ── 3. Revenue potential per contact ─────────────────────────────
    deal_result = await db.execute(
        select(
            Deal.contact_id,
            func.count(Deal.id).label("deal_count"),
            func.coalesce(func.sum(Deal.value * func.coalesce(Deal.probability, 0.5)), 0).label("potential"),
        )
        .where(
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage.notin_(["closed_won", "closed_lost"]),
            Deal.contact_id.isnot(None),
        )
        .group_by(Deal.contact_id)
    )
    revenue_map: dict[str, dict] = {}
    for cid, count, pot in deal_result.all():
        revenue_map[str(cid)] = {"count": count, "potential": round(float(pot), 2)}

    # ── 4. Contact names ──────────────────────────────────────────────
    all_cids = set(time_map.keys()) | set(revenue_map.keys())
    if not all_cids:
        return {
            "period_days": period_days,
            "total_time_minutes": 0,
            "total_revenue_potential": 0.0,
            "well_allocated": 0,
            "overallocated": 0,
            "underallocated": 0,
            "no_deals": 0,
            "allocations": [],
        }

    import uuid as _uuid
    uuid_cids = [_uuid.UUID(c) for c in all_cids]
    contact_result = await db.execute(
        select(Contact.id, Contact.first_name, Contact.last_name)
        .where(Contact.id.in_(uuid_cids), Contact.is_deleted == False)  # noqa: E712
    )
    name_map = {str(r[0]): f"{r[1]} {r[2]}" for r in contact_result.all()}

    # ── 5. Compute totals ─────────────────────────────────────────────
    total_time = sum(time_map.values()) or 1  # avoid div-by-zero
    total_rev = sum(r["potential"] for r in revenue_map.values()) or 1.0

    allocations = []
    counts = {"well_allocated": 0, "overallocated": 0, "underallocated": 0, "no_deals": 0}

    for cid in sorted(all_cids):
        t = time_map.get(cid, 0)
        rev = revenue_map.get(cid, {})
        pot = rev.get("potential", 0.0)
        dc = rev.get("count", 0)
        t_pct = round((t / total_time) * 100, 1) if total_time else 0.0
        r_pct = round((pot / total_rev) * 100, 1) if total_rev and pot > 0 else 0.0

        if t_pct > 0 and r_pct > 0:
            ratio = round(t_pct / r_pct, 2)
        elif dc == 0:
            ratio = None
        elif t_pct == 0 and r_pct > 0:
            ratio = 0.0
        else:
            ratio = None

        status = _classify(ratio)
        counts[status] = counts.get(status, 0) + 1

        allocations.append({
            "contact_id": cid,
            "contact_name": name_map.get(cid, "Unknown"),
            "time_spent_minutes": t,
            "time_spent_pct": t_pct,
            "revenue_potential": pot,
            "revenue_potential_pct": r_pct,
            "allocation_ratio": ratio,
            "status": status,
            "deal_count": dc,
        })

    # Sort: overallocated first, then underallocated, then well, then no_deals
    status_order = {"overallocated": 0, "underallocated": 1, "well_allocated": 2, "no_deals": 3}
    allocations.sort(key=lambda x: (status_order.get(x["status"], 9), -(x.get("allocation_ratio") or 0)))

    return {
        "period_days": period_days,
        "total_time_minutes": sum(time_map.values()),
        "total_revenue_potential": round(sum(r["potential"] for r in revenue_map.values()), 2),
        "well_allocated": counts["well_allocated"],
        "overallocated": counts["overallocated"],
        "underallocated": counts["underallocated"],
        "no_deals": counts["no_deals"],
        "allocations": allocations,
    }


async def get_contact_allocation(
    db: AsyncSession, contact_id: str, period_days: int = 30
) -> dict | None:
    """Detailed time & revenue breakdown for a single contact."""
    import uuid as _uuid
    uid = _uuid.UUID(contact_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=period_days)

    # Contact exists?
    c_result = await db.execute(
        select(Contact).where(Contact.id == uid, Contact.is_deleted == False)  # noqa: E712
    )
    contact = c_result.scalar_one_or_none()
    if not contact:
        return None

    # Time from interactions (by type)
    int_result = await db.execute(
        select(
            Interaction.type,
            func.coalesce(func.sum(Interaction.duration_minutes), 0).label("mins"),
        )
        .where(Interaction.contact_id == uid, Interaction.occurred_at >= cutoff)
        .group_by(Interaction.type)
    )
    time_by_type: dict[str, int] = {}
    for itype, mins in int_result.all():
        time_by_type[itype] = int(mins)

    # Time from meetings
    mtg_result = await db.execute(
        select(func.coalesce(func.sum(Meeting.duration_minutes), 0))
        .where(Meeting.contact_id == uid, Meeting.scheduled_at >= cutoff)
    )
    mtg_mins = int(mtg_result.scalar() or 0)
    if mtg_mins:
        time_by_type["meeting"] = time_by_type.get("meeting", 0) + mtg_mins

    contact_time = sum(time_by_type.values())

    # Total time across all contacts (for percentage)
    total_int = await db.execute(
        select(func.coalesce(func.sum(Interaction.duration_minutes), 0))
        .where(Interaction.occurred_at >= cutoff)
    )
    total_mtg = await db.execute(
        select(func.coalesce(func.sum(Meeting.duration_minutes), 0))
        .where(Meeting.scheduled_at >= cutoff)
    )
    total_time = int(total_int.scalar() or 0) + int(total_mtg.scalar() or 0)

    # Deals
    deal_result = await db.execute(
        select(Deal).where(
            Deal.contact_id == uid,
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage.notin_(["closed_won", "closed_lost"]),
        )
    )
    deals = deal_result.scalars().all()
    deal_list = []
    contact_potential = 0.0
    for d in deals:
        prob = d.probability if d.probability is not None else 0.5
        pot = round((d.value or 0) * prob, 2)
        contact_potential += pot
        deal_list.append({
            "deal_id": str(d.id),
            "title": d.title,
            "stage": d.stage,
            "value": d.value,
            "probability": prob,
            "potential": pot,
        })

    # Total revenue across all contacts
    total_rev_result = await db.execute(
        select(func.coalesce(
            func.sum(Deal.value * func.coalesce(Deal.probability, 0.5)), 0
        )).where(
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage.notin_(["closed_won", "closed_lost"]),
            Deal.contact_id.isnot(None),
        )
    )
    total_rev = float(total_rev_result.scalar() or 1.0)

    t_pct = round((contact_time / total_time) * 100, 1) if total_time else 0.0
    r_pct = round((contact_potential / total_rev) * 100, 1) if total_rev and contact_potential > 0 else 0.0

    if t_pct > 0 and r_pct > 0:
        ratio = round(t_pct / r_pct, 2)
    elif len(deals) == 0:
        ratio = None
    elif t_pct == 0 and r_pct > 0:
        ratio = 0.0
    else:
        ratio = None

    company_name = None
    if contact.company:
        company_name = contact.company.name

    return {
        "contact_id": str(uid),
        "contact_name": f"{contact.first_name} {contact.last_name}",
        "company_name": company_name,
        "period_days": period_days,
        "time_spent_minutes": contact_time,
        "time_by_type": time_by_type,
        "time_pct": t_pct,
        "deals": deal_list,
        "revenue_potential": contact_potential,
        "revenue_pct": r_pct,
        "allocation_ratio": ratio,
        "status": _classify(ratio),
    }


async def get_recommendations(db: AsyncSession, period_days: int = 30) -> dict:
    """Generate actionable attention reallocation recommendations."""
    summary = await get_attention_summary(db, period_days)
    recs = []

    for a in summary["allocations"]:
        if a["status"] == "underallocated":
            recs.append({
                "type": "increase_attention",
                "priority": "high" if (a["allocation_ratio"] or 0) < 0.3 else "medium",
                "contact_id": a["contact_id"],
                "contact_name": a["contact_name"],
                "revenue_potential": a["revenue_potential"],
                "current_time_pct": a["time_spent_pct"],
                "suggested_time_pct": a["revenue_potential_pct"],
                "reason": (
                    f"{a['contact_name']} represents {a['revenue_potential_pct']}% "
                    f"of revenue potential but receives only {a['time_spent_pct']}% of attention"
                ),
            })
        elif a["status"] == "overallocated":
            recs.append({
                "type": "reduce_attention",
                "priority": "high" if (a["allocation_ratio"] or 0) > 3.0 else "medium",
                "contact_id": a["contact_id"],
                "contact_name": a["contact_name"],
                "revenue_potential": a["revenue_potential"],
                "current_time_pct": a["time_spent_pct"],
                "suggested_time_pct": a["revenue_potential_pct"],
                "reason": (
                    f"{a['contact_name']} receives {a['time_spent_pct']}% of attention "
                    f"but represents only {a['revenue_potential_pct']}% of revenue potential"
                ),
            })

    # Sort: high priority first, then by revenue potential descending
    prio_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda x: (prio_order.get(x["priority"], 9), -x["revenue_potential"]))

    return {
        "period_days": period_days,
        "items": recs,
        "total": len(recs),
    }
