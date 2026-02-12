"""Ripple CRM — Audit log API routes.

Read-only access to the system audit trail.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/audit-log", tags=["audit"])


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: str
    action: str
    field_changed: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    changed_by: str
    changed_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=AuditLogListResponse)
async def list_audit_log(
    entity_type: str | None = Query(None, description="Filter by entity type"),
    entity_id: str | None = Query(None, description="Filter by entity ID"),
    action: str | None = Query(None, description="Filter by action (create/update/delete)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List audit log entries with optional filtering."""
    q = select(AuditLog)

    if entity_type:
        q = q.where(AuditLog.entity_type == entity_type)
    if entity_id:
        q = q.where(AuditLog.entity_id == entity_id)
    if action:
        q = q.where(AuditLog.action == action)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    q = q.order_by(AuditLog.changed_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    entries = result.scalars().all()

    return AuditLogListResponse(items=entries, total=total, page=page, page_size=page_size)
