"""Ripple CRM — Settings & Data Management API routes.

Settings are persisted as a simple JSON file (single-user CRM — no need for a DB table).
Also provides data management endpoints for purging all records.
"""

import json
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.commitment import Commitment
from app.models.company import Company
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.interaction import Interaction
from app.models.note import Note
from app.models.privacy_consent import PrivacyConsent
from app.models.relationship import Relationship
from app.models.tag import Tag, contact_tags
from app.models.task import Task

router = APIRouter(prefix="/settings", tags=["settings"])

# Path to the settings JSON file — sits alongside the backend package
SETTINGS_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS: dict = {
    "user_name": "Mani Padisetti",
    "user_email": "mani@almostmagic.tech",
    "theme": "dark",
    "currency": "AUD",
    "health_weights": {
        "recency": 30,
        "frequency": 25,
        "sentiment": 20,
        "commitment": 15,
        "response": 10,
    },
}


def _ensure_dir() -> None:
    """Create the data directory if it doesn't exist."""
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)


def _read_settings() -> dict:
    """Load settings from disk, returning defaults if the file is missing or invalid."""
    _ensure_dir()
    if not SETTINGS_FILE.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge defaults for any missing keys (defensive against partial files)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)


def _write_settings(data: dict) -> None:
    """Persist settings to disk."""
    _ensure_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# GET / — retrieve current settings
# ---------------------------------------------------------------------------

@router.get("")
async def get_settings():
    """Return the current application settings."""
    return _read_settings()


# ---------------------------------------------------------------------------
# PUT / — partial update of settings
# ---------------------------------------------------------------------------

@router.put("")
async def update_settings(data: dict):
    """Update settings (partial merge with existing values)."""
    current = _read_settings()

    # Deep merge for nested dicts (e.g. health_weights)
    for key, value in data.items():
        if isinstance(value, dict) and isinstance(current.get(key), dict):
            current[key].update(value)
        else:
            current[key] = value

    _write_settings(current)
    return current


# ---------------------------------------------------------------------------
# DELETE /data — purge all CRM data (not settings)
# ---------------------------------------------------------------------------

@router.delete("/data")
async def delete_all_data(db: AsyncSession = Depends(get_db)):
    """Delete all contacts, companies, deals, interactions, tasks,
    commitments, notes, relationships, privacy consents, tags, and audit logs.

    Settings are preserved. This is the nuclear option — use with care.
    """
    counts: dict[str, int] = {}

    # Order matters — delete child tables before parents to respect FK constraints.
    # contact_tags (junction table) first, then leaf tables, then parents.

    # 1. Junction table: contact_tags
    result = await db.execute(select(func.count()).select_from(contact_tags))
    counts["contact_tags"] = result.scalar() or 0
    await db.execute(delete(contact_tags))

    # 2. Privacy consents (FK -> contacts)
    result = await db.execute(select(func.count()).select_from(PrivacyConsent))
    counts["privacy_consents"] = result.scalar() or 0
    await db.execute(delete(PrivacyConsent))

    # 3. Relationships (FK -> contacts)
    result = await db.execute(select(func.count()).select_from(Relationship))
    counts["relationships"] = result.scalar() or 0
    await db.execute(delete(Relationship))

    # 4. Interactions (FK -> contacts, companies)
    result = await db.execute(select(func.count()).select_from(Interaction))
    counts["interactions"] = result.scalar() or 0
    await db.execute(delete(Interaction))

    # 5. Notes (FK -> contacts, deals)
    result = await db.execute(select(func.count()).select_from(Note))
    counts["notes"] = result.scalar() or 0
    await db.execute(delete(Note))

    # 6. Tasks (FK -> contacts, deals)
    result = await db.execute(select(func.count()).select_from(Task))
    counts["tasks"] = result.scalar() or 0
    await db.execute(delete(Task))

    # 7. Commitments (FK -> contacts, deals)
    result = await db.execute(select(func.count()).select_from(Commitment))
    counts["commitments"] = result.scalar() or 0
    await db.execute(delete(Commitment))

    # 8. Deals (FK -> contacts, companies)
    result = await db.execute(select(func.count()).select_from(Deal))
    counts["deals"] = result.scalar() or 0
    await db.execute(delete(Deal))

    # 9. Contacts (FK -> companies)
    result = await db.execute(select(func.count()).select_from(Contact))
    counts["contacts"] = result.scalar() or 0
    await db.execute(delete(Contact))

    # 10. Companies
    result = await db.execute(select(func.count()).select_from(Company))
    counts["companies"] = result.scalar() or 0
    await db.execute(delete(Company))

    # 11. Tags (no FK dependants left after contact_tags cleared)
    result = await db.execute(select(func.count()).select_from(Tag))
    counts["tags"] = result.scalar() or 0
    await db.execute(delete(Tag))

    # 12. Audit logs
    result = await db.execute(select(func.count()).select_from(AuditLog))
    counts["audit_logs"] = result.scalar() or 0
    await db.execute(delete(AuditLog))

    await db.commit()

    total = sum(counts.values())
    return {
        "detail": "All CRM data deleted. Settings preserved.",
        "total_deleted": total,
        "counts": counts,
    }
