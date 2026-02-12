"""Ripple CRM — Task Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    title: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    due_date: date | None = None
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    status: str = Field("todo", pattern="^(todo|in_progress|done|cancelled)$")


class TaskUpdate(BaseModel):
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = None
    due_date: date | None = None
    priority: str | None = Field(None, pattern="^(low|medium|high|urgent)$")
    status: str | None = Field(None, pattern="^(todo|in_progress|done|cancelled)$")


class TaskResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    due_date: date | None = None
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
