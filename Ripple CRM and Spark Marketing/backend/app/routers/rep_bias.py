"""Ripple CRM — Rep Bias Brain API routes (Phase 2.4)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.deal import Deal
from app.models.rep_forecast import RepForecastHistory
from app.schemas.rep_bias import (
    BiasProfileResponse,
    CorrectedProbabilityResponse,
    ForecastCreate,
    ForecastListResponse,
    ForecastResponse,
)
from app.services.audit import log_action
from app.services.rep_bias import get_bias_profile, get_corrected_probability

router = APIRouter(prefix="/rep-bias", tags=["rep-bias"])
deal_router = APIRouter(prefix="/deals", tags=["rep-bias"])


# ── Forecast CRUD ──────────────────────────────────────────────────────────

@router.post("/forecasts", response_model=ForecastResponse, status_code=201)
async def create_forecast(data: ForecastCreate, db: AsyncSession = Depends(get_db)):
    """Record a forecast entry (stated probability for a deal at a stage)."""
    # Verify deal exists
    result = await db.execute(select(Deal).where(Deal.id == data.deal_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Deal not found")

    forecast = RepForecastHistory(
        deal_id=data.deal_id,
        stage=data.stage,
        stated_probability=data.stated_probability,
        actual_outcome=data.actual_outcome,
        deal_value=data.deal_value,
    )
    db.add(forecast)
    await db.flush()
    await log_action(db, "rep_forecast", str(forecast.id), "create")
    await db.commit()
    await db.refresh(forecast)
    return forecast


@router.get("/forecasts", response_model=ForecastListResponse)
async def list_forecasts(
    deal_id: uuid.UUID | None = Query(None),
    stage: str | None = Query(None),
    actual_outcome: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List forecast history entries."""
    q = select(RepForecastHistory).order_by(RepForecastHistory.recorded_at.desc())

    if deal_id:
        q = q.where(RepForecastHistory.deal_id == deal_id)
    if stage:
        q = q.where(RepForecastHistory.stage == stage)
    if actual_outcome:
        q = q.where(RepForecastHistory.actual_outcome == actual_outcome)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    items = result.scalars().all()

    return ForecastListResponse(items=items, total=total)


@router.put("/forecasts/{forecast_id}/outcome")
async def update_forecast_outcome(
    forecast_id: uuid.UUID,
    outcome: str = Query(..., pattern="^(won|lost)$"),
    db: AsyncSession = Depends(get_db),
):
    """Update the actual outcome for a forecast entry."""
    result = await db.execute(
        select(RepForecastHistory).where(RepForecastHistory.id == forecast_id)
    )
    forecast = result.scalar_one_or_none()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")

    forecast.actual_outcome = outcome
    await log_action(db, "rep_forecast", str(forecast_id), "outcome_updated")
    await db.commit()
    await db.refresh(forecast)
    return {"detail": f"Outcome set to {outcome}", "forecast_id": str(forecast_id)}


# ── Bias Profile ───────────────────────────────────────────────────────────

@router.get("/profile", response_model=BiasProfileResponse)
async def bias_profile(db: AsyncSession = Depends(get_db)):
    """Get the overall rep bias profile."""
    return await get_bias_profile(db)


# ── Corrected Probability ─────────────────────────────────────────────────

@deal_router.get("/{deal_id}/corrected-probability", response_model=CorrectedProbabilityResponse)
async def corrected_probability(
    deal_id: uuid.UUID,
    stage: str = Query(...),
    stated_probability: int = Query(..., ge=0, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get bias-corrected probability for a deal at a given stage."""
    # Verify deal exists
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Deal not found")

    return await get_corrected_probability(db, deal_id, stage, stated_probability)


# ── Deal-scoped forecasts ─────────────────────────────────────────────────

@deal_router.get("/{deal_id}/forecasts", response_model=ForecastListResponse)
async def deal_forecasts(
    deal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all forecast entries for a specific deal."""
    q = (
        select(RepForecastHistory)
        .where(RepForecastHistory.deal_id == deal_id)
        .order_by(RepForecastHistory.recorded_at.desc())
    )
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    result = await db.execute(q)
    items = result.scalars().all()

    return ForecastListResponse(items=items, total=total)
