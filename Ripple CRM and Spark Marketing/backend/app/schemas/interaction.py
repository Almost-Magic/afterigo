"""Ripple CRM — Interaction Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class InteractionCreate(BaseModel):
    contact_id: uuid.UUID
    company_id: uuid.UUID | None = None
    type: str = Field(
        ...,
        max_length=20,
        pattern="^(email|call|meeting|note)$",
    )
    channel: str | None = Field(None, max_length=50)
    subject: str | None = Field(None, max_length=500)
    content: str | None = None
    sentiment_score: float | None = Field(None, ge=-1, le=1)
    duration_minutes: int | None = Field(None, ge=0)
    occurred_at: datetime | None = None


class InteractionResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    company_id: uuid.UUID | None = None
    type: str
    channel: str | None = None
    subject: str | None = None
    content: str | None = None
    sentiment_score: float | None = None
    duration_minutes: int | None = None
    occurred_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class InteractionListResponse(BaseModel):
    items: list[InteractionResponse]
    total: int
    page: int
    page_size: int
