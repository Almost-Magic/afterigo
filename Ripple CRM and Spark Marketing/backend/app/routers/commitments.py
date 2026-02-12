"""Ripple CRM — Commitments API routes.

Tracks promises made by us or by the contact/client. Automatically
flags overdue commitments (pending + due_date in the past) so nothing
slips through the cracks. This is the "trust ledger" of the CRM.
"""

import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.commitment import Commitment
from app.schemas.commitment import (
    CommitmentCreate,
    CommitmentListResponse,
    CommitmentResponse,
    CommitmentUpdate,
)
from app.services.audit import log_action, log_changes

router = APIRouter(prefix="/commitments", tags=["commitments"])


def _enrich_overdue(commitment: Commitment) -> CommitmentResponse:
    """Build response with computed is_overdue flag."""
    is_overdue = (
        commitment.status == "pending"
        and commitment.due_date is not None
        and commitment.due_date < date.today()
    )
    return CommitmentResponse(
        id=commitment.id,
        contact_id=commitment.contact_id,
        deal_id=commitment.deal_id,
        description=commitment.description,
        committed_by=commitment.committed_by,
        due_date=commitment.due_date,
        status=commitment.status,
        is_overdue=is_overdue,
        fulfilled_at=commitment.fulfilled_at,
        created_at=commitment.created_at,
    )


@router.post("", response_model=CommitmentResponse, status_code=201)
async def create_commitment(
    data: CommitmentCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new commitment — a promise made by us or by them."""
    commitment = Commitment(**data.model_dump())
    db.add(commitment)
    await db.flush()
    await log_action(db, "commitment", str(commitment.id), "create")
    await db.commit()
    await db.refresh(commitment)
    return _enrich_overdue(commitment)


@router.get("", response_model=CommitmentListResponse)
async def list_commitments(
    status: str | None = Query(None, description="Filter by status (pending/fulfilled/broken)"),
    committed_by: str | None = Query(None, description="Filter by who committed (us/them)"),
    overdue: bool | None = Query(None, description="Only show overdue commitments"),
    contact_id: uuid.UUID | None = Query(None, description="Filter by contact"),
    deal_id: uuid.UUID | None = Query(None, description="Filter by deal"),
    sort_by: str = Query("due_date"),
    sort_dir: str = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List commitments with optional filtering. Overdue flag computed automatically."""
    q = select(Commitment)

    if status:
        q = q.where(Commitment.status == status)
    if committed_by:
        q = q.where(Commitment.committed_by == committed_by)
    if overdue:
        today = date.today()
        q = q.where(
            Commitment.status == "pending",
            Commitment.due_date < today,
        )
    if contact_id:
        q = q.where(Commitment.contact_id == contact_id)
    if deal_id:
        q = q.where(Commitment.deal_id == deal_id)

    # Count total before pagination
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Sort and paginate
    sort_col = getattr(Commitment, sort_by, Commitment.due_date)
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    commitments = result.scalars().all()

    # Enrich each commitment with the computed is_overdue flag
    items = [_enrich_overdue(c) for c in commitments]

    return CommitmentListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.put("/{commitment_id}", response_model=CommitmentResponse)
async def update_commitment(
    commitment_id: uuid.UUID,
    data: CommitmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a commitment — typically to mark it fulfilled or broken."""
    result = await db.execute(
        select(Commitment).where(Commitment.id == commitment_id)
    )
    commitment = result.scalar_one_or_none()
    if not commitment:
        raise HTTPException(status_code=404, detail="Commitment not found")

    old_data = {k: getattr(commitment, k) for k in data.model_dump(exclude_unset=True)}
    update_data = data.model_dump(exclude_unset=True)

    # Auto-set fulfilled_at timestamp when status changes to fulfilled
    if update_data.get("status") == "fulfilled" and commitment.status != "fulfilled":
        update_data["fulfilled_at"] = datetime.utcnow()
        commitment.fulfilled_at = update_data["fulfilled_at"]

    for key, value in update_data.items():
        setattr(commitment, key, value)

    await log_changes(db, "commitment", str(commitment_id), old_data, update_data)
    await db.commit()
    await db.refresh(commitment)
    return _enrich_overdue(commitment)
