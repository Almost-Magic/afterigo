"""Ripple CRM — Audit log service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_action(
    db: AsyncSession,
    entity_type: str,
    entity_id: str,
    action: str,
    field_changed: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    changed_by: str = "system",
):
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=str(entity_id),
        action=action,
        field_changed=field_changed,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        changed_by=changed_by,
    )
    db.add(entry)


async def log_changes(
    db: AsyncSession,
    entity_type: str,
    entity_id: str,
    old_data: dict,
    new_data: dict,
    changed_by: str = "system",
):
    for key, new_val in new_data.items():
        old_val = old_data.get(key)
        if old_val != new_val and new_val is not None:
            await log_action(
                db, entity_type, entity_id, "update",
                field_changed=key,
                old_value=old_val,
                new_value=new_val,
                changed_by=changed_by,
            )
