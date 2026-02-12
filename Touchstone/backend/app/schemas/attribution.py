"""Touchstone — Schemas for attribution engine."""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel


ATTRIBUTION_MODELS = Literal[
    "first_touch", "last_touch", "linear", "time_decay", "position_based"
]


# ── Requests ──────────────────────────────────────────────────

class CalculateRequest(BaseModel):
    model: ATTRIBUTION_MODELS
    recalculate: bool = True


# ── Responses ─────────────────────────────────────────────────

class CalculateResponse(BaseModel):
    model: str
    deals_processed: int
    attributions_created: int
    total_revenue_attributed: Decimal


class CampaignAttribution(BaseModel):
    campaign_id: UUID | None
    campaign_name: str | None
    channel: str | None
    attributed_revenue: Decimal
    touchpoint_count: int
    deal_count: int
    budget: Decimal | None
    roi: Decimal | None


class CampaignAttributionResponse(BaseModel):
    model: str
    items: list[CampaignAttribution]
    total_attributed_revenue: Decimal


class ChannelAttribution(BaseModel):
    channel: str
    attributed_revenue: Decimal
    touchpoint_count: int
    deal_count: int
    percentage: Decimal


class ChannelAttributionResponse(BaseModel):
    model: str
    items: list[ChannelAttribution]
    total_attributed_revenue: Decimal


class ModelCampaignRow(BaseModel):
    campaign_id: UUID | None
    campaign_name: str | None
    first_touch: Decimal = Decimal("0")
    last_touch: Decimal = Decimal("0")
    linear: Decimal = Decimal("0")
    time_decay: Decimal = Decimal("0")
    position_based: Decimal = Decimal("0")


class ModelComparisonResponse(BaseModel):
    campaigns: list[ModelCampaignRow]


class ContactAttributionRecord(BaseModel):
    deal_id: UUID
    deal_name: str | None
    deal_amount: Decimal | None
    touchpoint_id: UUID
    touchpoint_timestamp: datetime
    channel: str | None
    source: str | None
    utm_campaign: str | None
    model: str
    attribution_weight: Decimal
    attributed_amount: Decimal


class ContactAttributionResponse(BaseModel):
    contact_id: UUID
    contact_name: str | None
    models: list[str]
    items: list[ContactAttributionRecord]
    total_attributed: Decimal
