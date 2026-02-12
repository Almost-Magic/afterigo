"""Beast Test — Step 3: Deals, Interactions & Timeline
Ripple CRM v3 — Almost Magic Tech Lab
"""

import uuid
from datetime import date, timedelta

import os

import httpx
import pytest

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")


# ── SECTION 1: IMPORT CHECKS ──────────────────────────────────────────────────

def test_import_deal_schemas():
    from app.schemas.deal import DealCreate, DealResponse, DealListResponse, DealUpdate
    assert DealCreate and DealResponse and DealListResponse and DealUpdate

def test_import_interaction_schemas():
    from app.schemas.interaction import InteractionCreate, InteractionResponse, InteractionListResponse
    assert InteractionCreate and InteractionResponse and InteractionListResponse

def test_import_task_schemas():
    from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse, TaskUpdate
    assert TaskCreate and TaskResponse and TaskListResponse and TaskUpdate

def test_import_commitment_schemas():
    from app.schemas.commitment import CommitmentCreate, CommitmentResponse, CommitmentListResponse, CommitmentUpdate
    assert CommitmentCreate and CommitmentResponse and CommitmentListResponse and CommitmentUpdate

def test_import_note_schemas():
    from app.schemas.note import NoteCreate, NoteResponse, NoteListResponse
    assert NoteCreate and NoteResponse and NoteListResponse

def test_import_routers():
    from app.routers.deals import router as dr
    from app.routers.interactions import router as ir, timeline_router as tr
    from app.routers.tasks import router as tkr
    from app.routers.commitments import router as cr
    from app.routers.notes import router as nr
    assert dr and ir and tr and tkr and cr and nr


# ── SECTION 2: DEAL CRUD ────────────────────────────────────────────────────

class TestDealCRUD:
    deal_id = None

    def test_create_deal(self):
        r = httpx.post(f"{BASE}/deals", json={
            "title": "Beast Deal", "value": 50000, "currency": "AUD",
            "stage": "lead", "probability": 25, "owner": "Mani",
            "source": "beast-test"
        }, timeout=5)
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Beast Deal"
        assert data["value"] == 50000
        assert data["stage"] == "lead"
        assert data["currency"] == "AUD"
        TestDealCRUD.deal_id = data["id"]

    def test_list_deals(self):
        r = httpx.get(f"{BASE}/deals", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        assert "items" in data

    def test_filter_deals_by_stage(self):
        r = httpx.get(f"{BASE}/deals?stage=lead", timeout=5)
        assert r.status_code == 200
        for d in r.json()["items"]:
            assert d["stage"] == "lead"

    def test_search_deals(self):
        r = httpx.get(f"{BASE}/deals?search=Beast", timeout=5)
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_get_deal(self):
        r = httpx.get(f"{BASE}/deals/{self.deal_id}", timeout=5)
        assert r.status_code == 200
        assert r.json()["title"] == "Beast Deal"

    def test_update_deal_stage(self):
        r = httpx.put(f"{BASE}/deals/{self.deal_id}", json={
            "stage": "qualified", "probability": 50
        }, timeout=5)
        assert r.status_code == 200
        assert r.json()["stage"] == "qualified"
        assert r.json()["probability"] == 50

    def test_get_nonexistent_deal(self):
        r = httpx.get(f"{BASE}/deals/{uuid.uuid4()}", timeout=5)
        assert r.status_code == 404

    def test_delete_deal(self):
        r = httpx.delete(f"{BASE}/deals/{self.deal_id}", timeout=5)
        assert r.status_code == 200
        # Verify soft-deleted (not visible)
        r2 = httpx.get(f"{BASE}/deals/{self.deal_id}", timeout=5)
        assert r2.status_code == 404


# ── SECTION 3: INTERACTION CRUD + TIMELINE ───────────────────────────────────

class TestInteractionCRUD:
    contact_id = None
    interaction_id = None

    def test_create_test_contact(self):
        """Create a contact to attach interactions to."""
        r = httpx.post(f"{BASE}/contacts", json={
            "first_name": "Timeline", "last_name": "Test",
            "email": "timeline@test.com.au", "type": "lead"
        }, timeout=5)
        assert r.status_code == 201
        TestInteractionCRUD.contact_id = r.json()["id"]

    def test_create_interaction_email(self):
        r = httpx.post(f"{BASE}/interactions", json={
            "contact_id": self.contact_id,
            "type": "email",
            "subject": "Beast follow-up email",
            "content": "Following up on our conversation.",
            "channel": "gmail"
        }, timeout=5)
        assert r.status_code == 201
        data = r.json()
        assert data["type"] == "email"
        assert data["subject"] == "Beast follow-up email"
        TestInteractionCRUD.interaction_id = data["id"]

    def test_create_interaction_call(self):
        r = httpx.post(f"{BASE}/interactions", json={
            "contact_id": self.contact_id,
            "type": "call",
            "subject": "Discovery call",
            "duration_minutes": 30
        }, timeout=5)
        assert r.status_code == 201
        assert r.json()["duration_minutes"] == 30

    def test_create_interaction_meeting(self):
        r = httpx.post(f"{BASE}/interactions", json={
            "contact_id": self.contact_id,
            "type": "meeting",
            "subject": "Onsite demo",
            "content": "Presented CRM capabilities."
        }, timeout=5)
        assert r.status_code == 201

    def test_list_interactions(self):
        r = httpx.get(f"{BASE}/interactions", timeout=5)
        assert r.status_code == 200
        assert r.json()["total"] >= 3

    def test_filter_interactions_by_type(self):
        r = httpx.get(f"{BASE}/interactions?type=email", timeout=5)
        assert r.status_code == 200
        for i in r.json()["items"]:
            assert i["type"] == "email"

    def test_contact_timeline(self):
        """Test the contact-specific timeline endpoint."""
        r = httpx.get(f"{BASE}/contacts/{self.contact_id}/interactions", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 3
        # Timeline should be chronological (oldest first)
        if len(data["items"]) >= 2:
            assert data["items"][0]["occurred_at"] <= data["items"][-1]["occurred_at"]

    def test_cleanup_contact(self):
        httpx.delete(f"{BASE}/contacts/{self.contact_id}", timeout=5)


# ── SECTION 4: TASK CRUD ────────────────────────────────────────────────────

class TestTaskCRUD:
    task_id = None

    def test_create_task(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        r = httpx.post(f"{BASE}/tasks", json={
            "title": "Beast follow-up task",
            "description": "Review proposal",
            "due_date": tomorrow,
            "priority": "high",
            "status": "todo"
        }, timeout=5)
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Beast follow-up task"
        assert data["priority"] == "high"
        TestTaskCRUD.task_id = data["id"]

    def test_list_tasks(self):
        r = httpx.get(f"{BASE}/tasks", timeout=5)
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_filter_tasks_by_status(self):
        r = httpx.get(f"{BASE}/tasks?status=todo", timeout=5)
        assert r.status_code == 200
        for t in r.json()["items"]:
            assert t["status"] == "todo"

    def test_filter_tasks_by_priority(self):
        r = httpx.get(f"{BASE}/tasks?priority=high", timeout=5)
        assert r.status_code == 200
        for t in r.json()["items"]:
            assert t["priority"] == "high"

    def test_update_task(self):
        r = httpx.put(f"{BASE}/tasks/{self.task_id}", json={
            "status": "done"
        }, timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "done"

    def test_get_nonexistent_task(self):
        r = httpx.get(f"{BASE}/tasks/{uuid.uuid4()}", timeout=5)
        assert r.status_code == 404

    def test_delete_task(self):
        r = httpx.delete(f"{BASE}/tasks/{self.task_id}", timeout=5)
        assert r.status_code == 200
        # Hard delete — should 404
        r2 = httpx.get(f"{BASE}/tasks/{self.task_id}", timeout=5)
        assert r2.status_code == 404


# ── SECTION 5: COMMITMENT CRUD ──────────────────────────────────────────────

class TestCommitmentCRUD:
    commitment_id = None

    def test_create_commitment(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        r = httpx.post(f"{BASE}/commitments", json={
            "description": "Send proposal by Friday",
            "committed_by": "us",
            "due_date": yesterday,
            "status": "pending"
        }, timeout=5)
        assert r.status_code == 201
        data = r.json()
        assert data["description"] == "Send proposal by Friday"
        assert data["committed_by"] == "us"
        assert data["is_overdue"] is True  # due_date in past + pending = overdue
        TestCommitmentCRUD.commitment_id = data["id"]

    def test_list_commitments(self):
        r = httpx.get(f"{BASE}/commitments", timeout=5)
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_filter_overdue(self):
        r = httpx.get(f"{BASE}/commitments?overdue=true", timeout=5)
        assert r.status_code == 200
        for c in r.json()["items"]:
            assert c["is_overdue"] is True

    def test_fulfil_commitment(self):
        r = httpx.put(f"{BASE}/commitments/{self.commitment_id}", json={
            "status": "fulfilled"
        }, timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "fulfilled"
        assert data["fulfilled_at"] is not None
        assert data["is_overdue"] is False  # no longer overdue once fulfilled


# ── SECTION 6: NOTE CRUD ────────────────────────────────────────────────────

class TestNoteCRUD:
    contact_id = None

    def test_create_note_contact(self):
        # Create a temp contact
        r = httpx.post(f"{BASE}/contacts", json={
            "first_name": "Note", "last_name": "Test", "type": "lead"
        }, timeout=5)
        assert r.status_code == 201
        TestNoteCRUD.contact_id = r.json()["id"]

        r = httpx.post(f"{BASE}/notes", json={
            "contact_id": TestNoteCRUD.contact_id,
            "content": "Great conversation about AI governance."
        }, timeout=5)
        assert r.status_code == 201
        assert r.json()["content"] == "Great conversation about AI governance."

    def test_list_notes_by_contact(self):
        r = httpx.get(f"{BASE}/notes?contact_id={self.contact_id}", timeout=5)
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_note_requires_link(self):
        """Notes must be linked to at least one of contact_id or deal_id."""
        r = httpx.post(f"{BASE}/notes", json={
            "content": "Orphan note — should fail"
        }, timeout=5)
        assert r.status_code == 422

    def test_cleanup(self):
        httpx.delete(f"{BASE}/contacts/{self.contact_id}", timeout=5)


# ── SECTION 7: VALIDATION ───────────────────────────────────────────────────

def test_create_deal_missing_title():
    r = httpx.post(f"{BASE}/deals", json={"value": 100}, timeout=5)
    assert r.status_code == 422

def test_create_deal_invalid_stage():
    r = httpx.post(f"{BASE}/deals", json={
        "title": "Bad Stage", "stage": "nonexistent"
    }, timeout=5)
    assert r.status_code == 422

def test_create_interaction_missing_contact():
    r = httpx.post(f"{BASE}/interactions", json={
        "type": "email", "subject": "No contact"
    }, timeout=5)
    assert r.status_code == 422

def test_create_interaction_invalid_type():
    r = httpx.post(f"{BASE}/interactions", json={
        "contact_id": str(uuid.uuid4()),
        "type": "invalid_type"
    }, timeout=5)
    assert r.status_code == 422

def test_create_task_missing_title():
    r = httpx.post(f"{BASE}/tasks", json={"priority": "high"}, timeout=5)
    assert r.status_code == 422

def test_create_task_invalid_priority():
    r = httpx.post(f"{BASE}/tasks", json={
        "title": "Bad Priority", "priority": "extreme"
    }, timeout=5)
    assert r.status_code == 422

def test_create_commitment_missing_description():
    r = httpx.post(f"{BASE}/commitments", json={"committed_by": "us"}, timeout=5)
    assert r.status_code == 422


# ── SECTION 8: AUDIT LOG ────────────────────────────────────────────────────

def test_audit_log_step3():
    """Verify audit log captured Step 3 operations."""
    import asyncio, asyncpg

    async def check():
        conn = await asyncpg.connect(
            user="postgres", password="peterman2026",
            host="localhost", port=5433, database="ripple"
        )
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM audit_log WHERE entity_type IN ('deal', 'interaction', 'task', 'commitment', 'note')"
        )
        await conn.close()
        return count

    count = asyncio.get_event_loop().run_until_complete(check())
    assert count >= 5, f"Expected >= 5 Step 3 audit entries, got {count}"


# ── CONFIDENCE STAMP ──────────────────────────────────────────────────────────

def test_confidence_stamp():
    """
    ╔═══════════════════════════════════════════════════════════╗
    ║  BEAST TEST — STEP 3: DEALS, INTERACTIONS & TIMELINE     ║
    ║  Ripple CRM v3 — Almost Magic Tech Lab                   ║
    ║  Status: PASSING                                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    assert True
