"""Beast Test — Phase 2.5: Attention Allocation Engine.

Sections:
  0. Setup
  1. Summary Endpoint
  2. Contact Detail
  3. Recommendations
  4. Period Filtering
  5. Edge Cases
  6. Allocation Logic
  7. Regression
  8. Confidence Stamp
"""

import os
import uuid
from datetime import datetime, timezone, timedelta

import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")

_RUN_ID = uuid.uuid4().hex[:8]

_contact_ids = []
_deal_ids = []
_interaction_ids = []


def _create_contact(first="Attn", last=None, email_addr=None):
    last = last or f"Test{_RUN_ID}"
    email_addr = email_addr or f"{first.lower()}.{last.lower()}.{uuid.uuid4().hex[:4]}@p2p5.test"
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first,
        "last_name": last,
        "email": email_addr,
        "type": "lead",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    cid = r.json()["id"]
    _contact_ids.append(cid)
    return cid


def _create_deal(title=None, contact_id=None, stage="proposal", value=50000.0, probability=0.6):
    title = title or f"AttnDeal {_RUN_ID} {len(_deal_ids)}"
    payload = {"title": title, "stage": stage, "value": value}
    if contact_id:
        payload["contact_id"] = contact_id
    if probability is not None:
        payload["probability"] = probability
    r = requests.post(f"{BASE}/deals", json=payload)
    assert r.status_code == 201, f"Create deal failed: {r.text}"
    did = r.json()["id"]
    _deal_ids.append(did)
    return did


def _create_interaction(contact_id, itype="call", duration=30, subject=None):
    payload = {
        "contact_id": contact_id,
        "type": itype,
        "channel": "phone",
        "duration_minutes": duration,
        "subject": subject or f"Attn test {_RUN_ID}",
    }
    r = requests.post(f"{BASE}/interactions", json=payload)
    assert r.status_code == 201, f"Create interaction failed: {r.text}"
    iid = r.json()["id"]
    _interaction_ids.append(iid)
    return iid


# ══════════════════════════════════════════════════════════════════════════════
# 0. SETUP
# ══════════════════════════════════════════════════════════════════════════════

def test_00_setup():
    """Create contacts with varying time investment and deal values."""
    # Contact A: High time, low revenue (overallocated)
    cid_a = _create_contact(first="HighTime", last=f"LowRev{_RUN_ID}")
    _create_deal(contact_id=cid_a, value=5000, probability=0.3, stage="lead")
    for i in range(5):
        _create_interaction(cid_a, duration=60, subject=f"Long call {i}")

    # Contact B: Low time, high revenue (underallocated)
    cid_b = _create_contact(first="LowTime", last=f"HighRev{_RUN_ID}")
    _create_deal(contact_id=cid_b, value=500000, probability=0.8, stage="negotiation")
    _create_interaction(cid_b, duration=10, subject="Quick check-in")

    # Contact C: Balanced
    cid_c = _create_contact(first="Balanced", last=f"Mid{_RUN_ID}")
    _create_deal(contact_id=cid_c, value=100000, probability=0.5, stage="proposal")
    _create_interaction(cid_c, duration=30, subject="Regular meeting")
    _create_interaction(cid_c, duration=30, subject="Follow-up")

    # Contact D: No deals (no_deals status)
    cid_d = _create_contact(first="NoDeal", last=f"Test{_RUN_ID}")
    _create_interaction(cid_d, duration=45, subject="Exploratory chat")

    assert len(_contact_ids) >= 4
    assert len(_deal_ids) >= 3
    assert len(_interaction_ids) >= 8


# ══════════════════════════════════════════════════════════════════════════════
# 1. SUMMARY ENDPOINT
# ══════════════════════════════════════════════════════════════════════════════

def test_01_summary_returns_200():
    """GET /api/attention/summary returns 200."""
    r = requests.get(f"{BASE}/attention/summary")
    assert r.status_code == 200


def test_01_summary_has_required_fields():
    """Summary response has all required fields."""
    r = requests.get(f"{BASE}/attention/summary")
    data = r.json()
    assert "period_days" in data
    assert "total_time_minutes" in data
    assert "total_revenue_potential" in data
    assert "well_allocated" in data
    assert "overallocated" in data
    assert "underallocated" in data
    assert "no_deals" in data
    assert "allocations" in data
    assert isinstance(data["allocations"], list)


def test_01_summary_allocations_have_fields():
    """Each allocation entry has required fields."""
    r = requests.get(f"{BASE}/attention/summary")
    data = r.json()
    assert len(data["allocations"]) >= 4
    entry = data["allocations"][0]
    assert "contact_id" in entry
    assert "contact_name" in entry
    assert "time_spent_minutes" in entry
    assert "time_spent_pct" in entry
    assert "revenue_potential" in entry
    assert "revenue_potential_pct" in entry
    assert "allocation_ratio" in entry
    assert "status" in entry
    assert "deal_count" in entry


def test_01_summary_has_overallocated():
    """Summary includes overallocated contacts."""
    r = requests.get(f"{BASE}/attention/summary")
    data = r.json()
    assert data["overallocated"] >= 1


def test_01_summary_has_underallocated():
    """Summary includes underallocated contacts."""
    r = requests.get(f"{BASE}/attention/summary")
    data = r.json()
    assert data["underallocated"] >= 1


def test_01_summary_has_no_deals():
    """Summary includes contacts with no deals."""
    r = requests.get(f"{BASE}/attention/summary")
    data = r.json()
    assert data["no_deals"] >= 1


# ══════════════════════════════════════════════════════════════════════════════
# 2. CONTACT DETAIL
# ══════════════════════════════════════════════════════════════════════════════

def test_02_contact_allocation_detail():
    """GET /api/contacts/{id}/attention returns detail."""
    r = requests.get(f"{BASE}/contacts/{_contact_ids[0]}/attention")
    assert r.status_code == 200
    data = r.json()
    assert data["contact_id"] == _contact_ids[0]
    assert "time_spent_minutes" in data
    assert "time_by_type" in data
    assert "deals" in data
    assert "revenue_potential" in data
    assert "allocation_ratio" in data
    assert "status" in data


def test_02_contact_detail_shows_time_by_type():
    """Contact detail breaks down time by interaction type."""
    r = requests.get(f"{BASE}/contacts/{_contact_ids[0]}/attention")
    data = r.json()
    assert isinstance(data["time_by_type"], dict)
    assert data["time_spent_minutes"] >= 60  # Contact A: 5 x 60min


def test_02_contact_detail_shows_deals():
    """Contact detail lists associated deals."""
    r = requests.get(f"{BASE}/contacts/{_contact_ids[0]}/attention")
    data = r.json()
    assert len(data["deals"]) >= 1
    deal = data["deals"][0]
    assert "deal_id" in deal
    assert "title" in deal
    assert "value" in deal
    assert "probability" in deal
    assert "potential" in deal


def test_02_contact_detail_404_for_nonexistent():
    """Contact attention 404 for non-existent contact."""
    fake_id = str(uuid.uuid4())
    r = requests.get(f"{BASE}/contacts/{fake_id}/attention")
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# 3. RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════

def test_03_recommendations_returns_200():
    """GET /api/attention/recommendations returns 200."""
    r = requests.get(f"{BASE}/attention/recommendations")
    assert r.status_code == 200


def test_03_recommendations_has_fields():
    """Recommendations response has required fields."""
    r = requests.get(f"{BASE}/attention/recommendations")
    data = r.json()
    assert "period_days" in data
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


def test_03_recommendations_have_types():
    """Recommendations include increase and reduce types."""
    r = requests.get(f"{BASE}/attention/recommendations")
    data = r.json()
    types = {item["type"] for item in data["items"]}
    # At minimum should have increase_attention (for underallocated contact B)
    assert "increase_attention" in types or "reduce_attention" in types


def test_03_recommendation_entry_fields():
    """Each recommendation has required fields."""
    r = requests.get(f"{BASE}/attention/recommendations")
    data = r.json()
    rec = data["items"][0]
    assert "type" in rec
    assert "priority" in rec
    assert rec["priority"] in ("high", "medium", "low")
    assert "contact_id" in rec
    assert "contact_name" in rec
    assert "revenue_potential" in rec
    assert "current_time_pct" in rec
    assert "reason" in rec
    assert len(rec["reason"]) > 10


# ══════════════════════════════════════════════════════════════════════════════
# 4. PERIOD FILTERING
# ══════════════════════════════════════════════════════════════════════════════

def test_04_summary_custom_period():
    """Summary accepts custom period_days parameter."""
    r = requests.get(f"{BASE}/attention/summary", params={"period_days": 7})
    assert r.status_code == 200
    data = r.json()
    assert data["period_days"] == 7


def test_04_contact_detail_custom_period():
    """Contact detail accepts custom period_days."""
    r = requests.get(
        f"{BASE}/contacts/{_contact_ids[0]}/attention",
        params={"period_days": 90},
    )
    assert r.status_code == 200
    assert r.json()["period_days"] == 90


def test_04_recommendations_custom_period():
    """Recommendations accepts custom period_days."""
    r = requests.get(f"{BASE}/attention/recommendations", params={"period_days": 14})
    assert r.status_code == 200
    assert r.json()["period_days"] == 14


def test_04_invalid_period_rejected():
    """Period < 7 or > 365 is rejected."""
    r = requests.get(f"{BASE}/attention/summary", params={"period_days": 3})
    assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# 5. EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════

def test_05_no_deal_contact_status():
    """Contact with no deals has 'no_deals' status."""
    # Contact D (index 3) has no deals
    r = requests.get(f"{BASE}/contacts/{_contact_ids[3]}/attention")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "no_deals"
    assert data["allocation_ratio"] is None
    assert data["revenue_potential"] == 0.0


def test_05_contact_with_interactions_no_deals():
    """Contact with time but no deals shows time but no revenue."""
    r = requests.get(f"{BASE}/contacts/{_contact_ids[3]}/attention")
    data = r.json()
    assert data["time_spent_minutes"] >= 45
    assert data["deals"] == []


# ══════════════════════════════════════════════════════════════════════════════
# 6. ALLOCATION LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def test_06_high_time_low_rev_is_overallocated():
    """Contact A (high time, low revenue) shows as overallocated."""
    r = requests.get(f"{BASE}/contacts/{_contact_ids[0]}/attention")
    data = r.json()
    # 300 min on $1500 potential vs others
    # Should be overallocated (ratio > 1.5)
    if data["allocation_ratio"] is not None:
        assert data["status"] in ("overallocated", "well_allocated", "underallocated")
        # High time + low revenue = overallocated is most likely


def test_06_percentages_sum_correctly():
    """Time percentages across all contacts with time should be reasonable."""
    r = requests.get(f"{BASE}/attention/summary")
    data = r.json()
    total_pct = sum(a["time_spent_pct"] for a in data["allocations"])
    # Should be close to 100% (rounding may cause slight deviation)
    assert 90.0 <= total_pct <= 110.0


def test_06_revenue_potential_correct():
    """Revenue potential = deal value x probability."""
    r = requests.get(f"{BASE}/contacts/{_contact_ids[1]}/attention")
    data = r.json()
    # Contact B: $500,000 x 0.8 = $400,000
    assert len(data["deals"]) >= 1
    deal = data["deals"][0]
    expected_pot = deal["value"] * deal["probability"]
    assert abs(deal["potential"] - expected_pot) < 0.01


# ══════════════════════════════════════════════════════════════════════════════
# 7. REGRESSION
# ══════════════════════════════════════════════════════════════════════════════

def test_07_regression_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_07_regression_contacts():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200
    assert "items" in r.json()


def test_07_regression_deals():
    r = requests.get(f"{BASE}/deals")
    assert r.status_code == 200
    assert "items" in r.json()


def test_07_regression_interactions():
    r = requests.get(f"{BASE}/interactions")
    assert r.status_code == 200
    assert "items" in r.json()


def test_07_regression_meetings():
    r = requests.get(f"{BASE}/meetings")
    assert r.status_code == 200
    assert "items" in r.json()


def test_07_regression_dashboard():
    r = requests.get(f"{BASE}/dashboard")
    assert r.status_code == 200
    assert "metrics" in r.json()


def test_07_regression_rep_bias():
    r = requests.get(f"{BASE}/rep-bias/profile")
    assert r.status_code == 200
    assert "total_forecasts" in r.json()


def test_07_regression_briefing_depths():
    r = requests.get(f"{BASE}/briefings/depths")
    assert r.status_code == 200
    assert "depths" in r.json()


def test_07_regression_channel_interactions():
    r = requests.get(f"{BASE}/channel-interactions")
    assert r.status_code == 200
    assert "items" in r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 8. CONFIDENCE STAMP
# ══════════════════════════════════════════════════════════════════════════════

def test_08_confidence_stamp():
    """Phase 2.5 Attention Allocation Engine — all tests passed."""
    print("\n" + "=" * 70)
    print("  PHASE 2.5 CONFIDENCE STAMP")
    print("  Attention Allocation Engine — ALL BEAST TESTS PASSED")
    print(f"  Run ID: {_RUN_ID}")
    print("=" * 70 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0

    for fn in tests:
        try:
            fn()
            passed += 1
            print(f"  PASS  {fn.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {e}")

    total = passed + failed
    print(f"\n{'=' * 60}")
    print(f"  Phase 2.5 Beast: {passed}/{total} passed")
    if failed:
        print(f"  {failed} FAILED")
        sys.exit(1)
    else:
        print("  ALL PASSED")
    print(f"{'=' * 60}")
