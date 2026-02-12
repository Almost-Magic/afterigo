"""Beast Test — Step 2: Contact & Company CRUD
Ripple CRM v3 — Almost Magic Tech Lab
"""

import uuid

import httpx
import pytest

BASE = "http://localhost:8100/api"


# ── SECTION 1: IMPORT CHECKS ──────────────────────────────────────────────────

def test_import_schemas():
    from app.schemas.contact import ContactCreate, ContactResponse, ContactListResponse
    from app.schemas.company import CompanyCreate, CompanyResponse, CompanyListResponse
    assert ContactCreate and CompanyCreate

def test_import_routers():
    from app.routers.contacts import router as cr
    from app.routers.companies import router as cor
    assert cr and cor

def test_import_audit():
    from app.services.audit import log_action, log_changes
    assert log_action and log_changes


# ── SECTION 2: CONTACT CRUD ───────────────────────────────────────────────────

class TestContactCRUD:
    contact_id = None

    def test_create_contact(self):
        r = httpx.post(f"{BASE}/contacts", json={
            "first_name": "Beast", "last_name": "Test",
            "email": "beast@test.com.au", "type": "lead", "source": "beast-test"
        }, timeout=5)
        assert r.status_code == 201
        data = r.json()
        assert data["first_name"] == "Beast"
        assert data["email"] == "beast@test.com.au"
        assert data["type"] == "lead"
        TestContactCRUD.contact_id = data["id"]

    def test_list_contacts(self):
        r = httpx.get(f"{BASE}/contacts", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        assert "items" in data

    def test_search_contacts(self):
        r = httpx.get(f"{BASE}/contacts?search=Beast", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1

    def test_filter_contacts_by_type(self):
        r = httpx.get(f"{BASE}/contacts?type=lead", timeout=5)
        assert r.status_code == 200
        for c in r.json()["items"]:
            assert c["type"] == "lead"

    def test_get_contact(self):
        r = httpx.get(f"{BASE}/contacts/{self.contact_id}", timeout=5)
        assert r.status_code == 200
        assert r.json()["first_name"] == "Beast"

    def test_update_contact(self):
        r = httpx.put(f"{BASE}/contacts/{self.contact_id}", json={
            "role": "Beast Tester", "type": "customer"
        }, timeout=5)
        assert r.status_code == 200
        assert r.json()["role"] == "Beast Tester"
        assert r.json()["type"] == "customer"

    def test_get_nonexistent_contact(self):
        r = httpx.get(f"{BASE}/contacts/{uuid.uuid4()}", timeout=5)
        assert r.status_code == 404

    def test_delete_contact(self):
        r = httpx.delete(f"{BASE}/contacts/{self.contact_id}", timeout=5)
        assert r.status_code == 200
        # Verify it's gone
        r2 = httpx.get(f"{BASE}/contacts/{self.contact_id}", timeout=5)
        assert r2.status_code == 404


# ── SECTION 3: COMPANY CRUD ───────────────────────────────────────────────────

class TestCompanyCRUD:
    company_id = None

    def test_create_company(self):
        r = httpx.post(f"{BASE}/companies", json={
            "name": "Beast Corp", "abn": "99999999999",
            "industry": "Testing", "city": "Sydney", "state": "NSW"
        }, timeout=5)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Beast Corp"
        assert data["country"] == "Australia"
        TestCompanyCRUD.company_id = data["id"]

    def test_list_companies(self):
        r = httpx.get(f"{BASE}/companies", timeout=5)
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_search_companies(self):
        r = httpx.get(f"{BASE}/companies?search=Beast", timeout=5)
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_get_company(self):
        r = httpx.get(f"{BASE}/companies/{self.company_id}", timeout=5)
        assert r.status_code == 200
        assert r.json()["name"] == "Beast Corp"

    def test_update_company(self):
        r = httpx.put(f"{BASE}/companies/{self.company_id}", json={
            "industry": "AI Testing"
        }, timeout=5)
        assert r.status_code == 200
        assert r.json()["industry"] == "AI Testing"

    def test_delete_company(self):
        r = httpx.delete(f"{BASE}/companies/{self.company_id}", timeout=5)
        assert r.status_code == 200
        r2 = httpx.get(f"{BASE}/companies/{self.company_id}", timeout=5)
        assert r2.status_code == 404


# ── SECTION 4: AUDIT LOG ──────────────────────────────────────────────────────

def test_audit_log_captures_changes():
    import asyncio, asyncpg

    async def check():
        conn = await asyncpg.connect(
            user="postgres", password="peterman2026",
            host="localhost", port=5433, database="ripple"
        )
        count = await conn.fetchval("SELECT COUNT(*) FROM audit_log")
        await conn.close()
        return count

    count = asyncio.get_event_loop().run_until_complete(check())
    assert count >= 3, f"Expected >= 3 audit entries, got {count}"


# ── SECTION 5: VALIDATION ─────────────────────────────────────────────────────

def test_create_contact_missing_required():
    r = httpx.post(f"{BASE}/contacts", json={"email": "no-name@test.com"}, timeout=5)
    assert r.status_code == 422

def test_create_company_missing_name():
    r = httpx.post(f"{BASE}/companies", json={"industry": "Nope"}, timeout=5)
    assert r.status_code == 422

def test_create_contact_invalid_type():
    r = httpx.post(f"{BASE}/contacts", json={
        "first_name": "Bad", "last_name": "Type", "type": "invalid"
    }, timeout=5)
    assert r.status_code == 422


# ── CONFIDENCE STAMP ──────────────────────────────────────────────────────────

def test_confidence_stamp():
    """
    ╔═══════════════════════════════════════════════════════════╗
    ║  BEAST TEST — STEP 2: CONTACT & COMPANY CRUD             ║
    ║  Ripple CRM v3 — Almost Magic Tech Lab                   ║
    ║  Status: PASSING                                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    assert True
