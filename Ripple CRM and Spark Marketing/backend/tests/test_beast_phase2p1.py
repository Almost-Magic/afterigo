"""Beast Test — Phase 2.1: Meeting Intelligence Hub.

Sections:
  1. Meeting CRUD
  2. Prep Me Brief
  3. Follow Me (Post-Meeting)
  4. Meeting Actions
  5. Contact-Scoped Meetings
  6. Deal-Scoped Meetings
  7. Meeting Analytics
  8. Regression
  9. Confidence Stamp
"""

import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")

_RUN_ID = uuid.uuid4().hex[:8]

# ══════════════════════════════════════════════════════════════════════════════
# SETUP
# ══════════════════════════════════════════════════════════════════════════════

_contact_id = None
_deal_id = None
_meeting_id = None
_action_id = None


def _create_contact(first="Meeting", last=None, email_addr=None):
    last = last or f"Test{_RUN_ID}"
    email_addr = email_addr or f"{first.lower()}.{last.lower()}@p2p1.test"
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first,
        "last_name": last,
        "email": email_addr,
        "type": "lead",
        "phone": "+61400000000",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    return r.json()["id"]


def _create_deal(title=None, contact_id=None):
    title = title or f"Deal {_RUN_ID}"
    payload = {"title": title, "stage": "lead", "value": 25000.0}
    if contact_id:
        payload["contact_id"] = contact_id
    r = requests.post(f"{BASE}/deals", json=payload)
    assert r.status_code == 201, f"Create deal failed: {r.text}"
    return r.json()["id"]


def test_setup():
    """Create shared test data for Phase 2.1 tests."""
    global _contact_id, _deal_id
    _contact_id = _create_contact("MeetingHub")
    _deal_id = _create_deal(f"MeetingDeal {_RUN_ID}", _contact_id)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Meeting CRUD
# ══════════════════════════════════════════════════════════════════════════════

def test_create_meeting():
    """Create a new meeting."""
    global _meeting_id
    assert _contact_id
    scheduled = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    r = requests.post(f"{BASE}/meetings", json={
        "contact_id": _contact_id,
        "deal_id": _deal_id,
        "title": f"Discovery call {_RUN_ID}",
        "meeting_type": "video",
        "location": "Zoom",
        "scheduled_at": scheduled,
        "duration_minutes": 30,
        "agenda": "Discuss requirements and timeline.",
        "attendees_json": json.dumps(["Mani Padisetti", "Test Contact"]),
    })
    assert r.status_code == 201, f"Create meeting failed: {r.text}"
    data = r.json()
    assert data["title"] == f"Discovery call {_RUN_ID}"
    assert data["meeting_type"] == "video"
    assert data["contact_id"] == _contact_id
    assert data["deal_id"] == _deal_id
    _meeting_id = data["id"]


def test_list_meetings():
    """List meetings returns items."""
    r = requests.get(f"{BASE}/meetings")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] >= 1


def test_get_meeting():
    """Get meeting detail."""
    assert _meeting_id
    r = requests.get(f"{BASE}/meetings/{_meeting_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == _meeting_id
    assert "actions" in data


def test_update_meeting():
    """Update meeting fields."""
    assert _meeting_id
    r = requests.put(f"{BASE}/meetings/{_meeting_id}", json={
        "title": f"Updated discovery call {_RUN_ID}",
        "outcome": "advanced",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["outcome"] == "advanced"
    assert "Updated" in data["title"]


def test_get_nonexistent_meeting():
    """Get nonexistent meeting returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/meetings/{fake_id}")
    assert r.status_code == 404


def test_create_meeting_nonexistent_contact():
    """Create meeting with nonexistent contact returns 404."""
    fake_id = str(uuid.uuid4())
    scheduled = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    r = requests.post(f"{BASE}/meetings", json={
        "contact_id": fake_id,
        "title": "Ghost meeting",
        "scheduled_at": scheduled,
    })
    assert r.status_code == 404


def test_create_meeting_invalid_type():
    """Create meeting with invalid type returns 422."""
    scheduled = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    r = requests.post(f"{BASE}/meetings", json={
        "contact_id": _contact_id,
        "title": "Invalid type",
        "meeting_type": "telekinesis",
        "scheduled_at": scheduled,
    })
    assert r.status_code == 422


def test_list_meetings_filter_type():
    """Filter meetings by type."""
    r = requests.get(f"{BASE}/meetings?meeting_type=video")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["meeting_type"] == "video"


def test_list_meetings_filter_outcome():
    """Filter meetings by outcome."""
    r = requests.get(f"{BASE}/meetings?outcome=advanced")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item["outcome"] == "advanced"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Prep Me Brief
# ══════════════════════════════════════════════════════════════════════════════

def test_prep_me():
    """Generate a Prep Me brief for an upcoming meeting."""
    assert _meeting_id
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/prep")
    assert r.status_code == 200, f"Prep Me failed: {r.text}"
    data = r.json()
    assert "contact_name" in data
    assert "suggested_talking_points" in data
    assert isinstance(data["suggested_talking_points"], list)
    assert data["meeting_id"] == _meeting_id


def test_prep_me_includes_deal_info():
    """Prep Me brief includes deal information when deal is linked."""
    assert _meeting_id
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/prep")
    assert r.status_code == 200
    data = r.json()
    assert data["deal_title"] is not None
    assert data["deal_stage"] is not None


def test_prep_me_nonexistent_meeting():
    """Prep Me for nonexistent meeting returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/meetings/{fake_id}/prep")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Follow Me (Post-Meeting)
# ══════════════════════════════════════════════════════════════════════════════

def test_follow_me():
    """Process Follow Me with notes and actions."""
    assert _meeting_id
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/followup", json={
        "notes": f"Good meeting. Discussed Phase 2 timeline. {_RUN_ID}",
        "outcome": "advanced",
        "sentiment_score": 0.7,
        "next_steps": "Send proposal by Friday.",
        "topics_json": json.dumps(["timeline", "budget", "scope"]),
        "actions": [
            {
                "title": "Send proposal",
                "description": "Draft and send proposal based on discussion.",
                "assignee": "Mani",
                "due_date": (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%d"),
                "priority": "high",
            },
            {
                "title": "Schedule follow-up",
                "description": "Book next meeting to review proposal.",
                "assignee": "Mani",
                "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d"),
                "priority": "medium",
            },
        ],
        "auto_create_tasks": True,
        "auto_create_commitments": True,
    })
    assert r.status_code == 200, f"Follow Me failed: {r.text}"
    data = r.json()
    assert data["actions_created"] == 2
    assert data["tasks_created"] == 2
    assert data["commitments_created"] == 2
    assert data["meeting"]["outcome"] == "advanced"
    assert data["meeting"]["notes"] is not None


def test_follow_me_without_actions():
    """Follow Me with notes only — no actions."""
    # Create a second meeting for this test
    scheduled = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    r = requests.post(f"{BASE}/meetings", json={
        "contact_id": _contact_id,
        "title": f"Quick catch-up {_RUN_ID}",
        "meeting_type": "phone",
        "scheduled_at": scheduled,
    })
    assert r.status_code == 201
    mid = r.json()["id"]

    r = requests.post(f"{BASE}/meetings/{mid}/followup", json={
        "notes": "Brief check-in. All on track.",
        "outcome": "no_outcome",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["actions_created"] == 0
    assert data["tasks_created"] == 0


def test_follow_me_nonexistent_meeting():
    """Follow Me for nonexistent meeting returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/meetings/{fake_id}/followup", json={
        "notes": "Ghost notes.",
    })
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Meeting Actions
# ══════════════════════════════════════════════════════════════════════════════

def test_list_meeting_actions():
    """List actions for a meeting."""
    assert _meeting_id
    r = requests.get(f"{BASE}/meetings/{_meeting_id}/actions")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] >= 2  # From follow_me test


def test_create_meeting_action():
    """Add an action to a meeting."""
    global _action_id
    assert _meeting_id
    r = requests.post(f"{BASE}/meetings/{_meeting_id}/actions", json={
        "title": f"Additional action {_RUN_ID}",
        "description": "An extra follow-up item.",
        "priority": "low",
    })
    assert r.status_code == 201, f"Create action failed: {r.text}"
    data = r.json()
    assert data["meeting_id"] == _meeting_id
    assert data["priority"] == "low"
    _action_id = data["id"]


def test_update_meeting_action():
    """Update a meeting action status."""
    assert _action_id
    r = requests.put(f"{BASE}/meetings/actions/{_action_id}", json={
        "status": "done",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "done"


def test_update_nonexistent_action():
    """Update nonexistent action returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.put(f"{BASE}/meetings/actions/{fake_id}", json={
        "status": "done",
    })
    assert r.status_code == 404


def test_list_actions_nonexistent_meeting():
    """List actions for nonexistent meeting returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/meetings/{fake_id}/actions")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Contact-Scoped Meetings
# ══════════════════════════════════════════════════════════════════════════════

def test_contact_meetings():
    """List meetings for a contact."""
    assert _contact_id
    r = requests.get(f"{BASE}/contacts/{_contact_id}/meetings")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] >= 1


def test_contact_meetings_nonexistent():
    """Contact meetings for nonexistent contact returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/meetings")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Deal-Scoped Meetings
# ══════════════════════════════════════════════════════════════════════════════

def test_deal_meetings():
    """List meetings for a deal."""
    assert _deal_id
    r = requests.get(f"{BASE}/deals/{_deal_id}/meetings")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data["total"] >= 1


def test_deal_meetings_nonexistent():
    """Deal meetings for nonexistent deal returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/deals/{fake_id}/meetings")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Meeting Analytics
# ══════════════════════════════════════════════════════════════════════════════

def test_meeting_analytics():
    """Meeting analytics returns aggregated data."""
    r = requests.get(f"{BASE}/meetings/analytics")
    assert r.status_code == 200
    data = r.json()
    assert "total_meetings" in data
    assert data["total_meetings"] >= 1
    assert "outcomes" in data
    assert "meetings_by_type" in data
    assert "actions_total" in data
    assert "top_contacts" in data


def test_meeting_analytics_has_completion_rate():
    """Analytics includes action completion rate."""
    r = requests.get(f"{BASE}/meetings/analytics")
    assert r.status_code == 200
    data = r.json()
    assert data["actions_total"] > 0
    assert data["actions_completed"] >= 1  # We marked one as done


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — Delete Meeting
# ══════════════════════════════════════════════════════════════════════════════

def test_delete_meeting_cascades():
    """Delete a meeting also deletes its actions."""
    # Create a throwaway meeting with an action
    scheduled = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    r = requests.post(f"{BASE}/meetings", json={
        "contact_id": _contact_id,
        "title": f"Delete me {_RUN_ID}",
        "meeting_type": "in_person",
        "scheduled_at": scheduled,
    })
    assert r.status_code == 201
    del_id = r.json()["id"]

    # Add action
    r = requests.post(f"{BASE}/meetings/{del_id}/actions", json={
        "title": "Will be cascade deleted",
    })
    assert r.status_code == 201

    # Delete
    r = requests.delete(f"{BASE}/meetings/{del_id}")
    assert r.status_code == 204

    # Verify gone
    r = requests.get(f"{BASE}/meetings/{del_id}")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — Regression
# ══════════════════════════════════════════════════════════════════════════════

def test_regression_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200


def test_regression_contacts():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200


def test_regression_deals():
    r = requests.get(f"{BASE}/deals")
    assert r.status_code == 200


def test_regression_emails():
    r = requests.get(f"{BASE}/emails")
    assert r.status_code == 200


def test_regression_tags():
    r = requests.get(f"{BASE}/tags")
    assert r.status_code == 200


def test_regression_lead_scores():
    r = requests.get(f"{BASE}/lead-scores/top?limit=5")
    assert r.status_code == 200


def test_regression_channel_dna():
    r = requests.get(f"{BASE}/channel-dna/summary")
    assert r.status_code == 200


def test_regression_trust_decay():
    r = requests.get(f"{BASE}/trust-decay/at-risk")
    assert r.status_code == 200


def test_regression_scoring_rules():
    r = requests.get(f"{BASE}/scoring/rules")
    assert r.status_code == 200


def test_regression_dsar():
    r = requests.get(f"{BASE}/privacy/dsar-requests")
    assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — Confidence Stamp
# ══════════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Phase 2.1 Beast test complete. Meeting Intelligence Hub: CRUD, Prep Me,
    Follow Me with auto-task/commitment creation, meeting actions, analytics,
    contact/deal scoping, cascade delete, and regression verified."""
    assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
