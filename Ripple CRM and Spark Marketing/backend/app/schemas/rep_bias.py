"""Rep Bias Brain schemas (Phase 2.4)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ForecastCreate(BaseModel):
    deal_id: uuid.UUID
    stage: str = Field(..., min_length=1, max_length=50)
    stated_probability: int = Field(..., ge=0, le=100)
    actual_outcome: str | None = Field(None, pattern="^(won|lost|open)$")
    deal_value: float | None = None


class ForecastResponse(BaseModel):
    id: uuid.UUID
    deal_id: uuid.UUID
    stage: str
    stated_probability: int
    actual_outcome: str | None = None
    deal_value: float | None = None
    recorded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ForecastListResponse(BaseModel):
    items: list[ForecastResponse]
    total: int


class BiasProfileResponse(BaseModel):
    total_forecasts: int
    closed_deals: int
    avg_stated_probability: float | None = None
    avg_actual_win_rate: float | None = None
    bias_direction: str | None = None  # "optimistic", "pessimistic", "calibrated"
    bias_magnitude: float | None = None  # percentage points of overestimate/underestimate
    correction_factor: float | None = None  # multiply stated prob by this
    stage_bias: list[dict] = []  # per-stage breakdown
    confidence_level: str = "insufficient_data"  # "insufficient_data", "low", "moderate", "high"
    min_deals_for_reliable: int = 20


class CorrectedProbabilityResponse(BaseModel):
    deal_id: str
    stage: str
    stated_probability: int
    corrected_probability: float
    bias_applied: float
    confidence_level: str
