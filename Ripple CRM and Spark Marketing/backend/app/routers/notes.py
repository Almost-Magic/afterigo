"""Ripple CRM — Notes API routes.

Simple free-text notes attached to contacts and/or deals.
No update or delete — notes are append-only for audit integrity.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Note
from app.schemas.note import (
    NoteCreate,
    NoteListResponse,
    NoteResponse,
)
from app.services.audit import log_action

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(data: NoteCreate, db: AsyncSession = Depends(get_db)):
    """Create a new note linked to a contact and/or deal."""
    # At least one of contact_id or deal_id must be provided
    if data.contact_id is None and data.deal_id is None:
        raise HTTPException(
            status_code=422,
            detail="At least one of contact_id or deal_id is required",
        )

    note = Note(**data.model_dump())
    db.add(note)
    await db.flush()
    await log_action(db, "note", str(note.id), "create")
    await db.commit()
    await db.refresh(note)
    return note


@router.get("", response_model=NoteListResponse)
async def list_notes(
    contact_id: uuid.UUID | None = Query(None, description="Filter by contact"),
    deal_id: uuid.UUID | None = Query(None, description="Filter by deal"),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List notes for a contact and/or deal. At least one filter recommended."""
    q = select(Note)

    if contact_id:
        q = q.where(Note.contact_id == contact_id)
    if deal_id:
        q = q.where(Note.deal_id == deal_id)

    # Count total before pagination
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Sort and paginate
    sort_col = getattr(Note, sort_by, Note.created_at)
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    notes = result.scalars().all()

    return NoteListResponse(items=notes, total=total, page=page, page_size=page_size)
