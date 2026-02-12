"""Ripple CRM — Deal Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class DealCreate(BaseModel):
    contact_id: uuid.UUID | None = None
    company_id: uuid.UUID | None = None
    title: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    value: float | None = None
    currency: str = Field("AUD", max_length=10)
    stage: str = Field(
        "lead",
        pattern="^(lead|qualified|proposal|negotiation|closed_won|closed_lost)$",
    )
    probability: float | None = Field(None, ge=0, le=100)
    expected_close_date: date | None = None
    owner: str | None = Field(None, max_length=100)
    source: str | None = Field(None, max_length=100)


class DealUpdate(BaseModel):
    contact_id: uuid.UUID | None = None
    company_id: uuid.UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = None
    value: float | None = None
    currency: str | None = Field(None, max_length=10)
    stage: str | None = Field(
        None,
        pattern="^(lead|qualified|proposal|negotiation|closed_won|closed_lost)$",
    )
    probability: float | None = Field(None, ge=0, le=100)
    expected_close_date: date | None = None
    actual_close_date: date | None = None
    owner: str | None = Field(None, max_length=100)
    source: str | None = Field(None, max_length=100)


class DealResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID | None = None
    company_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    value: float | None = None
    currency: str
    stage: str
    probability: float | None = None
    expected_close_date: date | None = None
    actual_close_date: date | None = None
    owner: str | None = None
    source: str | None = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DealListResponse(BaseModel):
    items: list[DealResponse]
    total: int
    page: int
    page_size: int
