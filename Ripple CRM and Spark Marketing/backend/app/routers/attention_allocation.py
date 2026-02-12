"""Ripple CRM — Attention Allocation API routes.

Shows where attention is misallocated by comparing time spent
(interactions + meetings) vs revenue potential (deal value x probability).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.attention_allocation import (
    get_attention_summary,
    get_contact_allocation,
    get_recommendations,
)

router = APIRouter(prefix="/attention", tags=["attention-allocation"])

contact_router = APIRouter(prefix="/contacts", tags=["attention-allocation"])


@router.get("/summary")
async def attention_summary(
    period_days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Attention allocation summary across all contacts."""
    return await get_attention_summary(db, period_days)


@router.get("/recommendations")
async def attention_recommendations(
    period_days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Actionable recommendations for attention reallocation."""
    return await get_recommendations(db, period_days)


@contact_router.get("/{contact_id}/attention")
async def contact_attention(
    contact_id: str,
    period_days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Detailed attention allocation breakdown for a single contact."""
    result = await get_contact_allocation(db, contact_id, period_days)
    if result is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return result
