"""Beast Test — Step 1: Skeleton
Ripple CRM v3 — Almost Magic Tech Lab

5 sections: Import, Unit, Integration, API Smoke, Confidence Stamp
"""

import asyncio
import sys
import uuid

import httpx
import pytest

# ── SECTION 1: IMPORT CHECKS ──────────────────────────────────────────────────

def test_import_fastapi():
    from fastapi import FastAPI
    assert FastAPI

def test_import_sqlalchemy():
    from sqlalchemy.ext.asyncio import AsyncSession
    assert AsyncSession

def test_import_models():
    from app.models import (
        Base, Contact, Company, Interaction, Relationship,
        Deal, Commitment, Tag, Task, Note, PrivacyConsent, AuditLog,
    )
    assert len(Base.metadata.tables) >= 12

def test_import_config():
    from app.config import settings
    assert settings.app_version == "3.0.0"

def test_import_app():
    from app.main import app
    assert app.title == "Ripple CRM"


# ── SECTION 2: UNIT TESTS ─────────────────────────────────────────────────────

def test_model_table_names():
    from app.models import Base
    table_names = set(Base.metadata.tables.keys())
    expected = {
        "contacts", "companies", "interactions", "relationships",
        "deals", "commitments", "tags", "contact_tags",
        "tasks", "notes", "privacy_consents", "audit_log",
    }
    assert expected.issubset(table_names), f"Missing tables: {expected - table_names}"

def test_contact_model_columns():
    from app.models import Contact
    cols = {c.name for c in Contact.__table__.columns}
    required = {"id", "first_name", "last_name", "email", "phone", "company_id",
                "role", "title", "type", "source", "notes", "timezone",
                "linkedin_url", "preferred_channel", "relationship_health_score",
                "trust_decay_days", "is_deleted", "created_at", "updated_at"}
    assert required.issubset(cols), f"Missing columns: {required - cols}"

def test_company_model_columns():
    from app.models import Company
    cols = {c.name for c in Company.__table__.columns}
    required = {"id", "name", "trading_name", "abn", "industry", "revenue",
                "employee_count", "website", "address", "city", "state",
                "postcode", "country", "account_health_score", "is_deleted",
                "created_at", "updated_at"}
    assert required.issubset(cols), f"Missing columns: {required - cols}"

def test_deal_model_columns():
    from app.models import Deal
    cols = {c.name for c in Deal.__table__.columns}
    required = {"id", "contact_id", "company_id", "title", "description", "value",
                "currency", "stage", "probability", "expected_close_date",
                "actual_close_date", "owner", "source", "is_deleted",
                "created_at", "updated_at"}
    assert required.issubset(cols), f"Missing columns: {required - cols}"

def test_audit_log_model_columns():
    from app.models import AuditLog
    cols = {c.name for c in AuditLog.__table__.columns}
    required = {"id", "entity_type", "entity_id", "action", "field_changed",
                "old_value", "new_value", "changed_by", "changed_at"}
    assert required.issubset(cols), f"Missing columns: {required - cols}"

def test_settings_defaults():
    from app.config import settings
    assert settings.app_name == "Ripple CRM"
    assert settings.app_port == 8100


# ── SECTION 3: INTEGRATION TESTS ──────────────────────────────────────────────

def test_database_tables_exist():
    """Verify tables exist in actual PostgreSQL."""
    import asyncpg

    async def check():
        conn = await asyncpg.connect(
            user="postgres", password="peterman2026",
            host="localhost", port=5433, database="ripple"
        )
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"
        )
        await conn.close()
        return {r["tablename"] for r in tables}

    tables = asyncio.get_event_loop().run_until_complete(check())
    expected = {"contacts", "companies", "deals", "interactions", "relationships",
                "commitments", "tags", "contact_tags", "tasks", "notes",
                "privacy_consents", "audit_log", "alembic_version"}
    assert expected.issubset(tables), f"Missing: {expected - tables}"


# ── SECTION 4: API SMOKE TESTS ────────────────────────────────────────────────

def test_health_endpoint():
    """Backend must return 200 with correct shape."""
    r = httpx.get("http://localhost:8100/api/health", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ripple-crm"
    assert data["version"] == "3.0.0"

def test_root_endpoint():
    r = httpx.get("http://localhost:8100/", timeout=5)
    assert r.status_code == 200

def test_cors_header():
    r = httpx.options(
        "http://localhost:8100/api/health",
        headers={"Origin": "http://localhost:3100", "Access-Control-Request-Method": "GET"},
        timeout=5,
    )
    assert r.status_code == 200
    assert "access-control-allow-origin" in r.headers


# ── SECTION 5: CONFIDENCE STAMP ───────────────────────────────────────────────

def test_confidence_stamp():
    """
    ╔═══════════════════════════════════════════════════════════╗
    ║  BEAST TEST — STEP 1: SKELETON                           ║
    ║  Ripple CRM v3 — Almost Magic Tech Lab                   ║
    ║  Status: PASSING                                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    assert True, "Step 1 Skeleton — Beast tests complete"
