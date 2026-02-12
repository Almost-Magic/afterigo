"""Ripple CRM — Company Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    trading_name: str | None = Field(None, max_length=255)
    abn: str | None = Field(None, max_length=20)
    industry: str | None = Field(None, max_length=100)
    revenue: float | None = None
    employee_count: int | None = None
    website: str | None = Field(None, max_length=500)
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=50)
    postcode: str | None = Field(None, max_length=20)
    country: str = Field("Australia", max_length=50)


class CompanyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    trading_name: str | None = Field(None, max_length=255)
    abn: str | None = Field(None, max_length=20)
    industry: str | None = Field(None, max_length=100)
    revenue: float | None = None
    employee_count: int | None = None
    website: str | None = Field(None, max_length=500)
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=50)
    postcode: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=50)


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    trading_name: str | None = None
    abn: str | None = None
    industry: str | None = None
    revenue: float | None = None
    employee_count: int | None = None
    website: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postcode: str | None = None
    country: str
    account_health_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    total: int
    page: int
    page_size: int
