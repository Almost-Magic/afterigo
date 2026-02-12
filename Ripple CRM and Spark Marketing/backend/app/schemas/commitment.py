"""Ripple CRM — Commitment Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class CommitmentCreate(BaseModel):
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    description: str = Field(..., min_length=1)
    committed_by: str = Field("us", pattern="^(us|them)$")
    due_date: date | None = None
    status: str = Field("pending", pattern="^(pending|fulfilled|broken)$")


class CommitmentUpdate(BaseModel):
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    description: str | None = Field(None, min_length=1)
    committed_by: str | None = Field(None, pattern="^(us|them)$")
    due_date: date | None = None
    status: str | None = Field(None, pattern="^(pending|fulfilled|broken)$")


class CommitmentResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    description: str
    committed_by: str
    due_date: date | None = None
    status: str
    is_overdue: bool = False
    fulfilled_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CommitmentListResponse(BaseModel):
    items: list[CommitmentResponse]
    total: int
    page: int
    page_size: int
