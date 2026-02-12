"""Meeting Intelligence Hub — router."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.meeting import Meeting, MeetingAction
from app.services.audit import log_action
from app.schemas.meeting import (
    FollowUpRequest,
    FollowUpResponse,
    MeetingActionCreate,
    MeetingActionListResponse,
    MeetingActionResponse,
    MeetingActionUpdate,
    MeetingAnalyticsResponse,
    MeetingCreate,
    MeetingListResponse,
    MeetingResponse,
    MeetingUpdate,
    PrepBriefResponse,
)
from app.services.meeting_intelligence import (
    calculate_meeting_analytics,
    generate_prep_brief,
    process_followup,
)

router = APIRouter(prefix="/meetings", tags=["meetings"])
contact_router = APIRouter(prefix="/contacts", tags=["meetings"])
deal_router = APIRouter(prefix="/deals", tags=["meetings"])


# ══════════════════════════════════════════════════════════════════════════════
# CRUD
# ══════════════════════════════════════════════════════════════════════════════

@router.post("", response_model=MeetingResponse, status_code=201)
async def create_meeting(data: MeetingCreate, db: AsyncSession = Depends(get_db)):
    """Create a new meeting."""
    # Validate contact exists
    contact = await db.get(Contact, data.contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    # Validate deal exists if provided
    if data.deal_id:
        deal = await db.get(Deal, data.deal_id)
        if not deal:
            raise HTTPException(404, "Deal not found")

    meeting = Meeting(**data.model_dump())
    db.add(meeting)
    await db.flush()
    await log_action(db, "meeting", str(meeting.id), "create")
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.get("", response_model=MeetingListResponse)
async def list_meetings(
    contact_id: uuid.UUID | None = Query(None),
    deal_id: uuid.UUID | None = Query(None),
    outcome: str | None = Query(None),
    meeting_type: str | None = Query(None),
    upcoming: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List meetings with filtering."""
    q = select(Meeting)
    count_q = select(func.count(Meeting.id))

    if contact_id:
        q = q.where(Meeting.contact_id == contact_id)
        count_q = count_q.where(Meeting.contact_id == contact_id)
    if deal_id:
        q = q.where(Meeting.deal_id == deal_id)
        count_q = count_q.where(Meeting.deal_id == deal_id)
    if outcome:
        q = q.where(Meeting.outcome == outcome)
        count_q = count_q.where(Meeting.outcome == outcome)
    if meeting_type:
        q = q.where(Meeting.meeting_type == meeting_type)
        count_q = count_q.where(Meeting.meeting_type == meeting_type)
    if upcoming is True:
        now = datetime.now(timezone.utc)
        q = q.where(Meeting.scheduled_at >= now)
        count_q = count_q.where(Meeting.scheduled_at >= now)
    elif upcoming is False:
        now = datetime.now(timezone.utc)
        q = q.where(Meeting.scheduled_at < now)
        count_q = count_q.where(Meeting.scheduled_at < now)

    total = (await db.execute(count_q)).scalar() or 0
    q = q.order_by(Meeting.scheduled_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(q)).scalars().all()

    return MeetingListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/analytics", response_model=MeetingAnalyticsResponse)
async def get_meeting_analytics(db: AsyncSession = Depends(get_db)):
    """Meeting analytics — frequency, duration, outcomes, action completion."""
    return await calculate_meeting_analytics(db)


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get meeting detail with actions."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(404, "Meeting not found")
    return meeting


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(meeting_id: uuid.UUID, data: MeetingUpdate, db: AsyncSession = Depends(get_db)):
    """Update meeting."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(404, "Meeting not found")

    updates = data.model_dump(exclude_unset=True)
    for key, val in updates.items():
        setattr(meeting, key, val)
    meeting.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await log_action(db, "meeting", str(meeting.id), "update")
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete meeting and its actions."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(404, "Meeting not found")
    await log_action(db, "meeting", str(meeting.id), "delete")
    await db.delete(meeting)
    await db.commit()


# ══════════════════════════════════════════════════════════════════════════════
# PREP ME
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/{meeting_id}/prep", response_model=PrepBriefResponse)
async def prep_me(meeting_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Generate a 'Prep Me' brief for an upcoming meeting."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(404, "Meeting not found")

    brief = await generate_prep_brief(db, meeting_id)
    return brief


# ══════════════════════════════════════════════════════════════════════════════
# FOLLOW ME
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/{meeting_id}/followup", response_model=FollowUpResponse)
async def follow_me(meeting_id: uuid.UUID, data: FollowUpRequest, db: AsyncSession = Depends(get_db)):
    """Process 'Follow Me' post-meeting data.

    Saves notes, creates actions, auto-creates tasks and commitments.
    """
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(404, "Meeting not found")

    actions_list = [a.model_dump() for a in data.actions]
    result = await process_followup(
        db,
        meeting_id,
        notes=data.notes,
        outcome=data.outcome,
        topics_json=data.topics_json,
        next_steps=data.next_steps,
        sentiment_score=data.sentiment_score,
        actions=actions_list,
        auto_create_tasks=data.auto_create_tasks,
        auto_create_commitments=data.auto_create_commitments,
    )

    return FollowUpResponse(
        meeting=result["meeting"],
        actions_created=result["actions_created"],
        tasks_created=result["tasks_created"],
        commitments_created=result["commitments_created"],
    )


# ══════════════════════════════════════════════════════════════════════════════
# MEETING ACTIONS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/{meeting_id}/actions", response_model=MeetingActionListResponse)
async def list_meeting_actions(meeting_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """List actions for a meeting."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(404, "Meeting not found")

    q = select(MeetingAction).where(MeetingAction.meeting_id == meeting_id).order_by(MeetingAction.created_at)
    items = (await db.execute(q)).scalars().all()
    return MeetingActionListResponse(items=items, total=len(items))


@router.post("/{meeting_id}/actions", response_model=MeetingActionResponse, status_code=201)
async def create_meeting_action(
    meeting_id: uuid.UUID,
    data: MeetingActionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add an action to a meeting."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(404, "Meeting not found")

    action = MeetingAction(
        meeting_id=meeting_id,
        contact_id=meeting.contact_id,
        deal_id=meeting.deal_id,
        **data.model_dump(),
    )
    db.add(action)
    await db.flush()
    await log_action(db, "meeting_action", str(action.id), "create")
    await db.commit()
    await db.refresh(action)
    return action


@router.put("/actions/{action_id}", response_model=MeetingActionResponse)
async def update_meeting_action(
    action_id: uuid.UUID,
    data: MeetingActionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a meeting action."""
    action = await db.get(MeetingAction, action_id)
    if not action:
        raise HTTPException(404, "Meeting action not found")

    updates = data.model_dump(exclude_unset=True)
    for key, val in updates.items():
        setattr(action, key, val)
    action.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await log_action(db, "meeting_action", str(action.id), "update")
    await db.commit()
    await db.refresh(action)
    return action


# ══════════════════════════════════════════════════════════════════════════════
# CONTACT + DEAL SCOPED
# ══════════════════════════════════════════════════════════════════════════════

@contact_router.get("/{contact_id}/meetings", response_model=MeetingListResponse)
async def get_contact_meetings(
    contact_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all meetings for a contact."""
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")

    count_q = select(func.count(Meeting.id)).where(Meeting.contact_id == contact_id)
    total = (await db.execute(count_q)).scalar() or 0

    q = (
        select(Meeting)
        .where(Meeting.contact_id == contact_id)
        .order_by(Meeting.scheduled_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = (await db.execute(q)).scalars().all()
    return MeetingListResponse(items=items, total=total, page=page, page_size=page_size)


@deal_router.get("/{deal_id}/meetings", response_model=MeetingListResponse)
async def get_deal_meetings(
    deal_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all meetings for a deal."""
    deal = await db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(404, "Deal not found")

    count_q = select(func.count(Meeting.id)).where(Meeting.deal_id == deal_id)
    total = (await db.execute(count_q)).scalar() or 0

    q = (
        select(Meeting)
        .where(Meeting.deal_id == deal_id)
        .order_by(Meeting.scheduled_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = (await db.execute(q)).scalars().all()
    return MeetingListResponse(items=items, total=total, page=page, page_size=page_size)
