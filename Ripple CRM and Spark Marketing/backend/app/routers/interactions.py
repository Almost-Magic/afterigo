"""Ripple CRM — Interactions API routes.

Every touchpoint with a contact — emails, calls, meetings, notes —
is recorded here so the relationship timeline is complete.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.interaction import Interaction
from app.schemas.interaction import (
    InteractionCreate,
    InteractionListResponse,
    InteractionResponse,
)
from app.services.audit import log_action

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionResponse, status_code=201)
async def create_interaction(
    data: InteractionCreate, db: AsyncSession = Depends(get_db)
):
    """Log a new interaction (email, call, meeting, or note)."""
    dump = data.model_dump()
    # Default occurred_at to now if not provided
    if dump.get("occurred_at") is None:
        dump["occurred_at"] = datetime.utcnow()

    interaction = Interaction(**dump)
    db.add(interaction)
    await db.flush()
    await log_action(db, "interaction", str(interaction.id), "create")
    await db.commit()
    await db.refresh(interaction)
    return interaction


@router.get("", response_model=InteractionListResponse)
async def list_interactions(
    contact_id: uuid.UUID | None = Query(None, description="Filter by contact"),
    type: str | None = Query(None, description="Filter by type (email/call/meeting/note)"),
    date_from: datetime | None = Query(None, description="Interactions after this date"),
    date_to: datetime | None = Query(None, description="Interactions before this date"),
    sort_by: str = Query("occurred_at"),
    sort_dir: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List interactions with optional filtering by contact, type, and date range."""
    q = select(Interaction)

    if contact_id:
        q = q.where(Interaction.contact_id == contact_id)
    if type:
        q = q.where(Interaction.type == type)
    if date_from:
        q = q.where(Interaction.occurred_at >= date_from)
    if date_to:
        q = q.where(Interaction.occurred_at <= date_to)

    # Count total before pagination
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Sort and paginate
    sort_col = getattr(Interaction, sort_by, Interaction.occurred_at)
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    interactions = result.scalars().all()

    return InteractionListResponse(
        items=interactions, total=total, page=page, page_size=page_size
    )


# --- Contact timeline endpoint (mounted under /contacts prefix) ---

timeline_router = APIRouter(prefix="/contacts", tags=["interactions"])


@timeline_router.get(
    "/{contact_id}/interactions", response_model=InteractionListResponse
)
async def get_contact_timeline(
    contact_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Chronological timeline of all interactions for a specific contact."""
    q = select(Interaction).where(Interaction.contact_id == contact_id)

    # Count total
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Chronological order — oldest first for a timeline view
    q = q.order_by(Interaction.occurred_at.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    interactions = result.scalars().all()

    return InteractionListResponse(
        items=interactions, total=total, page=page, page_size=page_size
    )
