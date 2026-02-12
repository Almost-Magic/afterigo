"""Meeting schemas — Meeting Intelligence Hub."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# ── Meeting ──────────────────────────────────────────────────────────────────

class MeetingCreate(BaseModel):
    contact_id: uuid.UUID
    deal_id: uuid.UUID | None = None
    title: str = Field(..., min_length=1, max_length=300)
    meeting_type: str = Field("in_person", pattern="^(in_person|video|phone)$")
    location: str | None = Field(None, max_length=500)
    scheduled_at: datetime
    duration_minutes: int | None = Field(None, ge=1)
    outcome: str | None = Field(None, pattern="^(advanced|stalled|won|lost|no_outcome)$")
    attendees_json: str | None = None
    agenda: str | None = None
    notes: str | None = None
    topics_json: str | None = None
    next_steps: str | None = None
    sentiment_score: float | None = Field(None, ge=-1, le=1)


class MeetingUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    meeting_type: str | None = Field(None, pattern="^(in_person|video|phone)$")
    location: str | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(None, ge=1)
    outcome: str | None = Field(None, pattern="^(advanced|stalled|won|lost|no_outcome)$")
    attendees_json: str | None = None
    agenda: str | None = None
    notes: str | None = None
    topics_json: str | None = None
    next_steps: str | None = None
    sentiment_score: float | None = Field(None, ge=-1, le=1)


class MeetingActionResponse(BaseModel):
    id: uuid.UUID
    meeting_id: uuid.UUID
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    assignee: str | None = None
    due_date: datetime | None = None
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MeetingResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    deal_id: uuid.UUID | None = None
    title: str
    meeting_type: str
    location: str | None = None
    scheduled_at: datetime
    duration_minutes: int | None = None
    outcome: str | None = None
    attendees_json: str | None = None
    agenda: str | None = None
    notes: str | None = None
    topics_json: str | None = None
    next_steps: str | None = None
    sentiment_score: float | None = None
    ai_summary: str | None = None
    prep_brief_json: str | None = None
    actions: list[MeetingActionResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MeetingListResponse(BaseModel):
    items: list[MeetingResponse]
    total: int
    page: int
    page_size: int


# ── Meeting Actions ──────────────────────────────────────────────────────────

class MeetingActionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    assignee: str | None = Field(None, max_length=100)
    due_date: date | None = None
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")


class MeetingActionUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = None
    assignee: str | None = None
    due_date: date | None = None
    priority: str | None = Field(None, pattern="^(low|medium|high|urgent)$")
    status: str | None = Field(None, pattern="^(todo|in_progress|done|cancelled)$")


class MeetingActionListResponse(BaseModel):
    items: list[MeetingActionResponse]
    total: int


# ── Prep Me Brief ────────────────────────────────────────────────────────────

class PrepBriefResponse(BaseModel):
    meeting_id: uuid.UUID
    contact_name: str
    deal_title: str | None = None
    deal_stage: str | None = None
    deal_value: float | None = None
    relationship_health: dict | None = None
    recent_interactions: list[dict] = []
    open_commitments: list[dict] = []
    open_tasks: list[dict] = []
    suggested_talking_points: list[str] = []
    ai_summary: str | None = None


# ── Follow Me ────────────────────────────────────────────────────────────────

class FollowUpRequest(BaseModel):
    notes: str | None = None
    outcome: str | None = Field(None, pattern="^(advanced|stalled|won|lost|no_outcome)$")
    topics_json: str | None = None
    next_steps: str | None = None
    sentiment_score: float | None = Field(None, ge=-1, le=1)
    actions: list[MeetingActionCreate] = []
    auto_create_tasks: bool = True
    auto_create_commitments: bool = True


class FollowUpResponse(BaseModel):
    meeting: MeetingResponse
    actions_created: int
    tasks_created: int
    commitments_created: int


# ── Analytics ────────────────────────────────────────────────────────────────

class MeetingAnalyticsResponse(BaseModel):
    total_meetings: int
    meetings_this_month: int
    avg_duration_minutes: float | None
    outcomes: dict
    meetings_by_type: dict
    actions_total: int
    actions_completed: int
    actions_completion_rate: float | None
    top_contacts: list[dict]
