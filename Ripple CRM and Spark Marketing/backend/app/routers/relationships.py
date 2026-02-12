"""Ripple CRM — Relationship Intelligence API routes.

Endpoints for health score calculation and recalculation.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.services.relationship_health import calculate_health_score, recalculate_all

router = APIRouter(prefix="/relationships", tags=["relationships"])


@router.get("/contacts/{contact_id}/health")
async def get_contact_health(
    contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Get the relationship health breakdown for a single contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False)  # noqa: E712
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    health = await calculate_health_score(db, contact_id)
    return {
        "contact_id": str(contact_id),
        "name": f"{contact.first_name} {contact.last_name}",
        **health,
    }


@router.post("/recalculate")
async def trigger_recalculate(db: AsyncSession = Depends(get_db)):
    """Recalculate health scores for all contacts."""
    count = await recalculate_all(db)
    return {"detail": f"Recalculated {count} contacts", "count": count}
