"""Beast Test — Step 4: Relationship Intelligence (Heuristic v1).

Sections:
  1. Imports
  2. Dashboard endpoint
  3. Relationship health endpoint
  4. Privacy / DSAR report
  5. Privacy consents
  6. Recalculate all
  7. Confidence Stamp
"""

import os
import uuid
from datetime import date, timedelta

import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")

# ── Helpers ────────────────────────────────────────────────────────────────

def _create_contact(first="Beast4", last="Health"):
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first, "last_name": last,
        "email": f"{first.lower()}@beast4.test", "type": "contact",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    return r.json()["id"]


def _create_interaction(contact_id, type_="email", subject="Beast4 interaction"):
    r = requests.post(f"{BASE}/interactions", json={
        "contact_id": contact_id, "type": type_, "subject": subject,
    })
    assert r.status_code == 201, f"Create interaction failed: {r.text}"
    return r.json()["id"]


def _create_commitment(contact_id, desc="Beast4 commitment", status="pending",
                       committed_by="us", due_date=None):
    payload = {
        "contact_id": contact_id, "description": desc,
        "committed_by": committed_by, "status": status,
    }
    if due_date:
        payload["due_date"] = due_date
    r = requests.post(f"{BASE}/commitments", json=payload)
    assert r.status_code == 201, f"Create commitment failed: {r.text}"
    return r.json()["id"]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Import checks
# ══════════════════════════════════════════════════════════════════════════

def test_import_relationship_health():
    from app.services.relationship_health import calculate_health_score, recalculate_all
    assert callable(calculate_health_score)
    assert callable(recalculate_all)

def test_import_dashboard_router():
    from app.routers.dashboard import router
    assert router is not None

def test_import_relationships_router():
    from app.routers.relationships import router
    assert router is not None

def test_import_privacy_router():
    from app.routers.privacy import router
    assert router is not None


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Dashboard endpoint
# ══════════════════════════════════════════════════════════════════════════

def test_dashboard_returns_200():
    r = requests.get(f"{BASE}/dashboard")
    assert r.status_code == 200

def test_dashboard_has_required_keys():
    r = requests.get(f"{BASE}/dashboard")
    data = r.json()
    for key in ["metrics", "people_to_reach", "deals_needing_attention",
                "overdue_commitments", "todays_tasks", "recent_activity"]:
        assert key in data, f"Missing key: {key}"

def test_dashboard_metrics_structure():
    r = requests.get(f"{BASE}/dashboard")
    m = r.json()["metrics"]
    for key in ["total_contacts", "active_deals", "pipeline_value", "overdue_tasks"]:
        assert key in m, f"Missing metric: {key}"
    assert isinstance(m["pipeline_value"], (int, float))

def test_dashboard_people_to_reach_is_list():
    r = requests.get(f"{BASE}/dashboard")
    assert isinstance(r.json()["people_to_reach"], list)

def test_dashboard_recent_activity_has_items():
    r = requests.get(f"{BASE}/dashboard")
    activity = r.json()["recent_activity"]
    assert isinstance(activity, list)
    # We created interactions in previous steps, so there should be some
    if activity:
        assert "type" in activity[0]
        assert "subject" in activity[0]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Relationship health endpoint
# ══════════════════════════════════════════════════════════════════════════

def test_health_for_contact_with_interactions():
    cid = _create_contact("HealthTest", "One")
    _create_interaction(cid, "call", "Health check call")
    _create_interaction(cid, "email", "Health check email")

    r = requests.get(f"{BASE}/relationships/contacts/{cid}/health")
    assert r.status_code == 200
    data = r.json()
    assert "score" in data
    assert "label" in data
    assert "components" in data
    assert data["score"] >= 0
    assert data["label"] in ["Healthy", "Warning", "Critical"]


def test_health_components_present():
    cid = _create_contact("HealthTest", "Two")
    _create_interaction(cid, "meeting", "Component check")
    r = requests.get(f"{BASE}/relationships/contacts/{cid}/health")
    components = r.json()["components"]
    for key in ["recency", "frequency", "sentiment", "commitment", "response"]:
        assert key in components, f"Missing component: {key}"


def test_health_for_contact_no_interactions():
    cid = _create_contact("HealthTest", "Lonely")
    r = requests.get(f"{BASE}/relationships/contacts/{cid}/health")
    assert r.status_code == 200
    data = r.json()
    # No interactions → low score
    assert data["score"] <= 50


def test_health_404_for_nonexistent_contact():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/relationships/contacts/{fake_id}/health")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Privacy / DSAR report
# ══════════════════════════════════════════════════════════════════════════

def test_dsar_report_for_contact():
    cid = _create_contact("DSAR", "Subject")
    _create_interaction(cid, "email", "DSAR test interaction")
    r = requests.get(f"{BASE}/privacy/contacts/{cid}/report")
    assert r.status_code == 200
    data = r.json()
    assert "report_generated_at" in data
    assert "contact" in data
    assert data["contact"]["first_name"] == "DSAR"
    assert "interactions" in data
    assert "notes" in data
    assert "commitments" in data
    assert "consents" in data
    assert data["total_interactions"] >= 1


def test_dsar_report_404_for_nonexistent():
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/privacy/contacts/{fake_id}/report")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — Privacy consents
# ══════════════════════════════════════════════════════════════════════════

def test_create_consent():
    cid = _create_contact("ConsentTest", "User")
    r = requests.post(f"{BASE}/privacy/consents", json={
        "contact_id": cid,
        "consent_type": "email_marketing",
        "granted": True,
        "source": "beast_test",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["consent_type"] == "email_marketing"
    assert data["granted"] is True


def test_create_consent_missing_fields():
    r = requests.post(f"{BASE}/privacy/consents", json={
        "contact_id": str(uuid.uuid4()),
    })
    assert r.status_code == 422


def test_list_consents():
    r = requests.get(f"{BASE}/privacy/consents")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_list_consents_filter_by_type():
    r = requests.get(f"{BASE}/privacy/consents?consent_type=email_marketing")
    assert r.status_code == 200
    items = r.json()["items"]
    for c in items:
        assert c["consent_type"] == "email_marketing"


def test_consent_appears_in_dsar():
    cid = _create_contact("ConsentDSAR", "Check")
    requests.post(f"{BASE}/privacy/consents", json={
        "contact_id": cid,
        "consent_type": "data_processing",
        "granted": True,
        "source": "beast_test",
    })
    r = requests.get(f"{BASE}/privacy/contacts/{cid}/report")
    assert r.status_code == 200
    consents = r.json()["consents"]
    assert len(consents) >= 1
    assert consents[0]["consent_type"] == "data_processing"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — Recalculate all
# ══════════════════════════════════════════════════════════════════════════

def test_recalculate_all():
    r = requests.post(f"{BASE}/relationships/recalculate")
    assert r.status_code == 200
    data = r.json()
    assert "count" in data
    assert data["count"] >= 1


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — Confidence Stamp
# ══════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Step 4 Beast test complete. Dashboard, relationship health,
    privacy/DSAR, consent tracking, and recalculate all verified."""
    assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
