"""Ripple CRM — Dashboard API routes (Daily Command Centre).

The most important screen in Ripple. Aggregates key metrics,
people needing attention, overdue commitments, and today's tasks.
"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.commitment import Commitment
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.interaction import Interaction
from app.models.task import Task

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """The Daily Command Centre — aggregated view of everything that matters."""
    today = date.today()

    # ── Key Metrics ──────────────────────────────────────────────────────
    total_contacts = (await db.execute(
        select(func.count()).select_from(
            select(Contact.id).where(Contact.is_deleted == False).subquery()  # noqa: E712
        )
    )).scalar() or 0

    active_deals = (await db.execute(
        select(func.count()).select_from(
            select(Deal.id).where(
                Deal.is_deleted == False,  # noqa: E712
                Deal.stage.notin_(["closed_won", "closed_lost"])
            ).subquery()
        )
    )).scalar() or 0

    pipeline_value = (await db.execute(
        select(func.coalesce(func.sum(Deal.value), 0)).where(
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage.notin_(["closed_won", "closed_lost"])
        )
    )).scalar() or 0

    overdue_task_count = (await db.execute(
        select(func.count()).select_from(
            select(Task.id).where(
                Task.due_date < today,
                Task.status.notin_(["done", "cancelled"])
            ).subquery()
        )
    )).scalar() or 0

    # ── People to Reach Out To (top 5 by trust decay) ────────────────────
    result = await db.execute(
        select(Contact)
        .where(
            Contact.is_deleted == False,  # noqa: E712
            Contact.trust_decay_days.isnot(None),
            Contact.trust_decay_days > 0
        )
        .order_by(Contact.trust_decay_days.desc())
        .limit(5)
    )
    decay_contacts = result.scalars().all()
    people_to_reach = [
        {
            "id": str(c.id),
            "name": f"{c.first_name} {c.last_name}",
            "trust_decay_days": c.trust_decay_days,
            "health_score": c.relationship_health_score,
            "type": c.type,
        }
        for c in decay_contacts
    ]

    # ── Deals Needing Attention (stalled or low health) ──────────────────
    result = await db.execute(
        select(Deal)
        .where(
            Deal.is_deleted == False,  # noqa: E712
            Deal.stage.notin_(["closed_won", "closed_lost"])
        )
        .order_by(Deal.updated_at.asc())
        .limit(5)
    )
    stalled_deals = result.scalars().all()
    deals_needing_attention = [
        {
            "id": str(d.id),
            "title": d.title,
            "stage": d.stage,
            "value": d.value,
            "days_in_stage": (date.today() - d.updated_at.date()).days if d.updated_at else None,
        }
        for d in stalled_deals
    ]

    # ── Overdue Commitments ──────────────────────────────────────────────
    result = await db.execute(
        select(Commitment)
        .where(
            Commitment.status == "pending",
            Commitment.due_date < today,
        )
        .order_by(Commitment.due_date.asc())
        .limit(10)
    )
    overdue_commitments = result.scalars().all()
    overdue_list = [
        {
            "id": str(c.id),
            "description": c.description,
            "committed_by": c.committed_by,
            "due_date": c.due_date.isoformat() if c.due_date else None,
            "days_overdue": (today - c.due_date).days if c.due_date else None,
        }
        for c in overdue_commitments
    ]

    # ── Today's Tasks ────────────────────────────────────────────────────
    result = await db.execute(
        select(Task)
        .where(Task.due_date == today, Task.status.notin_(["done", "cancelled"]))
        .order_by(Task.priority.desc())
    )
    todays_tasks = result.scalars().all()
    tasks_list = [
        {
            "id": str(t.id),
            "title": t.title,
            "priority": t.priority,
            "status": t.status,
        }
        for t in todays_tasks
    ]

    # ── Recent Activity ──────────────────────────────────────────────────
    result = await db.execute(
        select(Interaction)
        .order_by(Interaction.occurred_at.desc())
        .limit(10)
    )
    recent = result.scalars().all()
    recent_activity = [
        {
            "id": str(i.id),
            "type": i.type,
            "subject": i.subject,
            "occurred_at": i.occurred_at.isoformat() if i.occurred_at else None,
        }
        for i in recent
    ]

    return {
        "metrics": {
            "total_contacts": total_contacts,
            "active_deals": active_deals,
            "pipeline_value": float(pipeline_value),
            "overdue_tasks": overdue_task_count,
        },
        "people_to_reach": people_to_reach,
        "deals_needing_attention": deals_needing_attention,
        "overdue_commitments": overdue_list,
        "todays_tasks": tasks_list,
        "recent_activity": recent_activity,
    }
