"""Touchstone — Attribution API endpoints."""

from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.attribution import (
    ATTRIBUTION_MODELS,
    CalculateRequest,
    CalculateResponse,
    CampaignAttributionResponse,
    ChannelAttributionResponse,
    ModelComparisonResponse,
)
from app.services.attribution import (
    calculate_attributions,
    get_campaign_attribution,
    get_channel_attribution,
    get_model_comparison,
)


router = APIRouter(prefix="/attribution", tags=["attribution"])


def _to_datetime(d: date | None) -> datetime | None:
    """Convert date to timezone-aware datetime for filtering."""
    if d is None:
        return None
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


@router.post("/calculate", response_model=CalculateResponse)
async def calculate(body: CalculateRequest, db: AsyncSession = Depends(get_db)):
    """Run attribution calculation for all won deals using the specified model.

    Idempotent: clears previous results for the model before recalculating.
    """
    result = await calculate_attributions(db, body.model, body.recalculate)
    return CalculateResponse(**result)


@router.get("/campaigns", response_model=CampaignAttributionResponse)
async def campaigns(
    model: ATTRIBUTION_MODELS = "linear",
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Campaigns ranked by attributed revenue for a given model."""
    result = await get_campaign_attribution(
        db, model, _to_datetime(date_from), _to_datetime(date_to)
    )
    return CampaignAttributionResponse(**result)


@router.get("/channels", response_model=ChannelAttributionResponse)
async def channels(
    model: ATTRIBUTION_MODELS = "linear",
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Channels ranked by attributed revenue for a given model."""
    result = await get_channel_attribution(
        db, model, _to_datetime(date_from), _to_datetime(date_to)
    )
    return ChannelAttributionResponse(**result)


@router.get("/compare", response_model=ModelComparisonResponse)
async def compare(
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Side-by-side comparison of all 5 attribution models by campaign."""
    result = await get_model_comparison(
        db, _to_datetime(date_from), _to_datetime(date_to)
    )
    return ModelComparisonResponse(**result)
