"""Ripple CRM — Privacy / Transparency Portal API routes.

DSAR report generation, consent tracking, and privacy management.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.commitment import Commitment
from app.models.contact import Contact
from app.models.interaction import Interaction
from app.models.note import Note
from app.models.privacy_consent import PrivacyConsent

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.get("/contacts/{contact_id}/report")
async def generate_dsar_report(
    contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Generate a DSAR (Data Subject Access Request) report for a contact.
    Returns all data held about the contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Interactions
    result = await db.execute(
        select(Interaction).where(Interaction.contact_id == contact_id)
        .order_by(Interaction.occurred_at.desc())
    )
    interactions = result.scalars().all()

    # Notes
    result = await db.execute(
        select(Note).where(Note.contact_id == contact_id)
        .order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()

    # Commitments
    result = await db.execute(
        select(Commitment).where(Commitment.contact_id == contact_id)
    )
    commitments = result.scalars().all()

    # Consents
    result = await db.execute(
        select(PrivacyConsent).where(PrivacyConsent.contact_id == contact_id)
        .order_by(PrivacyConsent.created_at.desc())
    )
    consents = result.scalars().all()

    return {
        "report_generated_at": datetime.now(timezone.utc).isoformat(),
        "contact": {
            "id": str(contact.id),
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "role": contact.role,
            "type": contact.type,
            "source": contact.source,
            "created_at": contact.created_at.isoformat() if contact.created_at else None,
        },
        "interactions": [
            {
                "id": str(i.id),
                "type": i.type,
                "subject": i.subject,
                "content": i.content,
                "occurred_at": i.occurred_at.isoformat() if i.occurred_at else None,
            }
            for i in interactions
        ],
        "notes": [
            {
                "id": str(n.id),
                "content": n.content,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notes
        ],
        "commitments": [
            {
                "id": str(c.id),
                "description": c.description,
                "committed_by": c.committed_by,
                "status": c.status,
                "due_date": c.due_date.isoformat() if c.due_date else None,
            }
            for c in commitments
        ],
        "consents": [
            {
                "id": str(c.id),
                "consent_type": c.consent_type,
                "granted": c.granted,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
                "source": c.source,
            }
            for c in consents
        ],
        "total_interactions": len(interactions),
        "total_notes": len(notes),
        "total_commitments": len(commitments),
    }


@router.get("/consents")
async def list_consents(
    contact_id: uuid.UUID | None = Query(None),
    consent_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List privacy consents with optional filtering."""
    q = select(PrivacyConsent)
    if contact_id:
        q = q.where(PrivacyConsent.contact_id == contact_id)
    if consent_type:
        q = q.where(PrivacyConsent.consent_type == consent_type)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(PrivacyConsent.created_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    consents = result.scalars().all()

    return {
        "items": [
            {
                "id": str(c.id),
                "contact_id": str(c.contact_id),
                "consent_type": c.consent_type,
                "granted": c.granted,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
                "source": c.source,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in consents
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/consents")
async def create_consent(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Record a privacy consent for a contact."""
    required = ["contact_id", "consent_type", "granted"]
    for field in required:
        if field not in data:
            raise HTTPException(status_code=422, detail=f"Missing required field: {field}")

    consent = PrivacyConsent(
        contact_id=uuid.UUID(data["contact_id"]),
        consent_type=data["consent_type"],
        granted=data["granted"],
        granted_at=datetime.now(timezone.utc) if data["granted"] else None,
        source=data.get("source"),
    )
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    return {
        "id": str(consent.id),
        "contact_id": str(consent.contact_id),
        "consent_type": consent.consent_type,
        "granted": consent.granted,
        "created_at": consent.created_at.isoformat() if consent.created_at else None,
    }
