"""Ripple CRM — Deals API routes.

Full CRUD for the deal pipeline. Stage changes are logged to audit
so we maintain a complete history of how each deal progressed.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.deal import Deal
from app.schemas.deal import (
    DealCreate,
    DealListResponse,
    DealResponse,
    DealUpdate,
)
from app.services.audit import log_action, log_changes

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", response_model=DealResponse, status_code=201)
async def create_deal(data: DealCreate, db: AsyncSession = Depends(get_db)):
    """Create a new deal, optionally linked to a contact and/or company."""
    deal = Deal(**data.model_dump())
    db.add(deal)
    await db.flush()
    await log_action(db, "deal", str(deal.id), "create")
    await db.commit()
    await db.refresh(deal)
    return deal


@router.get("", response_model=DealListResponse)
async def list_deals(
    stage: str | None = Query(None, description="Filter by pipeline stage"),
    contact_id: uuid.UUID | None = Query(None, description="Filter by contact"),
    company_id: uuid.UUID | None = Query(None, description="Filter by company"),
    search: str | None = Query(None, description="Search deal title"),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List deals with optional filtering by stage, contact, or company."""
    q = select(Deal).where(Deal.is_deleted == False)  # noqa: E712

    if stage:
        q = q.where(Deal.stage == stage)
    if contact_id:
        q = q.where(Deal.contact_id == contact_id)
    if company_id:
        q = q.where(Deal.company_id == company_id)
    if search:
        term = f"%{search}%"
        q = q.where(Deal.title.ilike(term))

    # Count total before pagination
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Sort and paginate
    sort_col = getattr(Deal, sort_by, Deal.created_at)
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    deals = result.scalars().all()

    return DealListResponse(items=deals, total=total, page=page, page_size=page_size)


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Fetch a single deal by ID."""
    result = await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False)  # noqa: E712
    )
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: uuid.UUID, data: DealUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a deal. Stage changes are individually logged to audit."""
    result = await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False)  # noqa: E712
    )
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    old_data = {k: getattr(deal, k) for k in data.model_dump(exclude_unset=True)}
    update_data = data.model_dump(exclude_unset=True)

    # Detect stage transitions — log them explicitly for pipeline analytics
    if "stage" in update_data and update_data["stage"] != old_data.get("stage"):
        await log_action(
            db, "deal", str(deal_id), "stage_change",
            field_changed="stage",
            old_value=old_data.get("stage"),
            new_value=update_data["stage"],
        )

    for key, value in update_data.items():
        setattr(deal, key, value)

    await log_changes(db, "deal", str(deal_id), old_data, update_data)
    await db.commit()
    await db.refresh(deal)
    return deal


@router.delete("/{deal_id}")
async def delete_deal(deal_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Soft-delete a deal (sets is_deleted flag)."""
    result = await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False)  # noqa: E712
    )
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    deal.is_deleted = True
    await log_action(db, "deal", str(deal_id), "delete")
    await db.commit()
    return {"detail": "Deal deleted"}
