"""Ripple CRM — Import/Export API routes.

CSV import (with duplicate detection) and export for contacts, companies, and deals.
"""

import csv
import io
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.company import Company
from app.models.contact import Contact
from app.models.deal import Deal
from app.services.audit import log_action

router = APIRouter(prefix="/import-export", tags=["import-export"])

# ---------------------------------------------------------------------------
# Header mapping — normalise common CSV column names to model field names
# ---------------------------------------------------------------------------

CONTACT_HEADER_MAP = {
    "first_name": "first_name",
    "firstname": "first_name",
    "first name": "first_name",
    "last_name": "last_name",
    "lastname": "last_name",
    "last name": "last_name",
    "email": "email",
    "phone": "phone",
    "role": "role",
    "job title": "role",
    "job_title": "role",
    "type": "type",
    "source": "source",
    "company_name": "company_name",
    "company": "company_name",
    "company name": "company_name",
}

COMPANY_HEADER_MAP = {
    "name": "name",
    "company name": "name",
    "company_name": "name",
    "industry": "industry",
    "website": "website",
    "address": "address",
    "phone": "phone",
}


def _normalise_headers(raw_headers: list[str], mapping: dict[str, str]) -> dict[int, str]:
    """Return {column_index: field_name} for recognised headers."""
    result: dict[int, str] = {}
    for idx, raw in enumerate(raw_headers):
        key = raw.strip().lower()
        if key in mapping:
            result[idx] = mapping[key]
    return result


def _parse_csv_bytes(raw: bytes) -> list[dict[str, str]]:
    """Decode uploaded bytes and return a list of row dicts (keys are raw headers)."""
    # Try UTF-8 first, fall back to latin-1 (handles most Windows CSVs)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if len(rows) < 2:
        return []

    headers = rows[0]
    result = []
    for row in rows[1:]:
        if not any(cell.strip() for cell in row):
            continue  # skip blank rows
        entry: dict[str, str] = {}
        for idx, value in enumerate(row):
            if idx < len(headers):
                entry[headers[idx]] = value.strip()
        result.append(entry)
    return result


# ---------------------------------------------------------------------------
# Contact import
# ---------------------------------------------------------------------------

@router.post("/import/contacts")
async def import_contacts(
    file: UploadFile = File(...),
    commit: bool = Query(False, description="Set to true to actually import; false for preview"),
    db: AsyncSession = Depends(get_db),
):
    """Import contacts from a CSV file.

    With commit=false (default), returns a preview with duplicate detection.
    With commit=true, creates the contact records in the database.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    raw = await file.read()
    raw_rows = _parse_csv_bytes(raw)
    if not raw_rows:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no data rows")

    # Build header mapping from raw keys
    raw_headers = list(raw_rows[0].keys())
    col_map = _normalise_headers(raw_headers, CONTACT_HEADER_MAP)
    mapped_fields = set(col_map.values())

    if "first_name" not in mapped_fields or "last_name" not in mapped_fields:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain at least first_name and last_name columns",
        )

    # Map rows to normalised dicts
    mapped_rows: list[dict[str, str]] = []
    for raw_row in raw_rows:
        mapped: dict[str, str] = {}
        for idx, raw_header in enumerate(raw_headers):
            if idx in col_map:
                mapped[col_map[idx]] = raw_row.get(raw_header, "")
        mapped_rows.append(mapped)

    # Fetch existing contacts for duplicate detection (non-deleted only)
    result = await db.execute(select(Contact).where(Contact.is_deleted == False))  # noqa: E712
    existing_contacts = result.scalars().all()

    # Build lookup structures for fuzzy matching
    email_set: set[str] = set()
    name_set: set[str] = set()
    for c in existing_contacts:
        if c.email:
            email_set.add(c.email.strip().lower())
        name_key = f"{(c.first_name or '').strip().lower()}|{(c.last_name or '').strip().lower()}"
        name_set.add(name_key)

    # Analyse each row for duplicates
    preview: list[dict] = []
    imported_count = 0
    duplicate_count = 0

    for row in mapped_rows:
        first = row.get("first_name", "").strip()
        last = row.get("last_name", "").strip()
        email = row.get("email", "").strip()

        is_duplicate = False
        duplicate_reason = None

        # Case-insensitive exact email match
        if email and email.lower() in email_set:
            is_duplicate = True
            duplicate_reason = f"Email '{email}' already exists"
        # First + last name match
        elif f"{first.lower()}|{last.lower()}" in name_set:
            is_duplicate = True
            duplicate_reason = f"Name '{first} {last}' already exists"

        row_info = {
            "row_data": row,
            "is_duplicate": is_duplicate,
            "duplicate_reason": duplicate_reason,
        }

        if is_duplicate:
            duplicate_count += 1
            row_info["action"] = "skip"
        else:
            row_info["action"] = "import"

        if commit and not is_duplicate:
            # Look up or skip company_name — we don't auto-create companies here
            company_name = row.get("company_name", "").strip()
            company_id = None
            if company_name:
                comp_result = await db.execute(
                    select(Company).where(
                        func.lower(Company.name) == company_name.lower(),
                        Company.is_deleted == False,  # noqa: E712
                    )
                )
                comp = comp_result.scalar_one_or_none()
                if comp:
                    company_id = comp.id

            contact = Contact(
                first_name=first,
                last_name=last,
                email=email or None,
                phone=row.get("phone", "").strip() or None,
                role=row.get("role", "").strip() or None,
                type=row.get("type", "").strip() or "lead",
                source=row.get("source", "").strip() or "csv_import",
                company_id=company_id,
            )
            db.add(contact)
            await db.flush()
            await log_action(db, "contact", str(contact.id), "create")
            imported_count += 1

            # Add to lookup sets so later rows in the same file detect intra-file duplicates
            if email:
                email_set.add(email.lower())
            name_set.add(f"{first.lower()}|{last.lower()}")

        preview.append(row_info)

    if commit:
        await db.commit()

    return {
        "total_rows": len(mapped_rows),
        "duplicates": duplicate_count,
        "to_import": len(mapped_rows) - duplicate_count,
        "imported": imported_count if commit else 0,
        "committed": commit,
        "mapped_fields": sorted(mapped_fields),
        "rows": preview,
    }


# ---------------------------------------------------------------------------
# Company import
# ---------------------------------------------------------------------------

@router.post("/import/companies")
async def import_companies(
    file: UploadFile = File(...),
    commit: bool = Query(False, description="Set to true to actually import; false for preview"),
    db: AsyncSession = Depends(get_db),
):
    """Import companies from a CSV file.

    With commit=false (default), returns a preview with duplicate detection.
    With commit=true, creates the company records in the database.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    raw = await file.read()
    raw_rows = _parse_csv_bytes(raw)
    if not raw_rows:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no data rows")

    raw_headers = list(raw_rows[0].keys())
    col_map = _normalise_headers(raw_headers, COMPANY_HEADER_MAP)
    mapped_fields = set(col_map.values())

    if "name" not in mapped_fields:
        raise HTTPException(status_code=400, detail="CSV must contain a 'name' or 'Company Name' column")

    mapped_rows: list[dict[str, str]] = []
    for raw_row in raw_rows:
        mapped: dict[str, str] = {}
        for idx, raw_header in enumerate(raw_headers):
            if idx in col_map:
                mapped[col_map[idx]] = raw_row.get(raw_header, "")
        mapped_rows.append(mapped)

    # Fetch existing companies for duplicate detection
    result = await db.execute(select(Company).where(Company.is_deleted == False))  # noqa: E712
    existing = result.scalars().all()
    name_set: set[str] = {c.name.strip().lower() for c in existing if c.name}

    preview: list[dict] = []
    imported_count = 0
    duplicate_count = 0

    for row in mapped_rows:
        name = row.get("name", "").strip()
        is_duplicate = name.lower() in name_set if name else False
        duplicate_reason = f"Company '{name}' already exists" if is_duplicate else None

        row_info = {
            "row_data": row,
            "is_duplicate": is_duplicate,
            "duplicate_reason": duplicate_reason,
            "action": "skip" if is_duplicate else "import",
        }

        if commit and not is_duplicate and name:
            company = Company(
                name=name,
                industry=row.get("industry", "").strip() or None,
                website=row.get("website", "").strip() or None,
                address=row.get("address", "").strip() or None,
            )
            # Phone is not a Company model field — skip silently
            db.add(company)
            await db.flush()
            imported_count += 1
            name_set.add(name.lower())

        if is_duplicate:
            duplicate_count += 1

        preview.append(row_info)

    if commit:
        await db.commit()

    return {
        "total_rows": len(mapped_rows),
        "duplicates": duplicate_count,
        "to_import": len(mapped_rows) - duplicate_count,
        "imported": imported_count if commit else 0,
        "committed": commit,
        "mapped_fields": sorted(mapped_fields),
        "rows": preview,
    }


# ---------------------------------------------------------------------------
# Contact export
# ---------------------------------------------------------------------------

@router.get("/export/contacts")
async def export_contacts(db: AsyncSession = Depends(get_db)):
    """Export all non-deleted contacts as a CSV download."""
    result = await db.execute(
        select(Contact).where(Contact.is_deleted == False).order_by(Contact.created_at.desc())  # noqa: E712
    )
    contacts = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        "id", "first_name", "last_name", "email", "phone",
        "role", "title", "type", "source", "timezone",
        "linkedin_url", "preferred_channel",
        "relationship_health_score", "created_at", "updated_at",
    ]
    writer.writerow(headers)

    for c in contacts:
        writer.writerow([
            str(c.id),
            c.first_name,
            c.last_name,
            c.email or "",
            c.phone or "",
            c.role or "",
            c.title or "",
            c.type,
            c.source or "",
            c.timezone or "",
            c.linkedin_url or "",
            c.preferred_channel or "",
            c.relationship_health_score if c.relationship_health_score is not None else "",
            c.created_at.isoformat() if c.created_at else "",
            c.updated_at.isoformat() if c.updated_at else "",
        ])

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"ripple_contacts_{timestamp}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Deal export
# ---------------------------------------------------------------------------

@router.get("/export/deals")
async def export_deals(db: AsyncSession = Depends(get_db)):
    """Export all non-deleted deals as a CSV download."""
    result = await db.execute(
        select(Deal).where(Deal.is_deleted == False).order_by(Deal.created_at.desc())  # noqa: E712
    )
    deals = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        "id", "title", "description", "contact_id", "company_id",
        "value", "currency", "stage", "probability",
        "expected_close_date", "actual_close_date",
        "owner", "source", "created_at", "updated_at",
    ]
    writer.writerow(headers)

    for d in deals:
        writer.writerow([
            str(d.id),
            d.title,
            d.description or "",
            str(d.contact_id) if d.contact_id else "",
            str(d.company_id) if d.company_id else "",
            d.value if d.value is not None else "",
            d.currency,
            d.stage,
            d.probability if d.probability is not None else "",
            d.expected_close_date.isoformat() if d.expected_close_date else "",
            d.actual_close_date.isoformat() if d.actual_close_date else "",
            d.owner or "",
            d.source or "",
            d.created_at.isoformat() if d.created_at else "",
            d.updated_at.isoformat() if d.updated_at else "",
        ])

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"ripple_deals_{timestamp}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
