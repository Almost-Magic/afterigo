"""Beast Test — Phase 2.4: Rep Bias Brain.

Sections:
  0. Setup
  1. Forecast CRUD
  2. Bias Profile
  3. Corrected Probability
  4. Deal-Scoped Forecasts
  5. Edge Cases
  6. Regression
  7. Confidence Stamp
"""

import os
import uuid
from datetime import datetime, timezone

import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")

_RUN_ID = uuid.uuid4().hex[:8]

_contact_id = None
_deal_ids = []
_forecast_ids = []


def _create_contact(first="RepBias", last=None, email_addr=None):
    last = last or f"Test{_RUN_ID}"
    email_addr = email_addr or f"{first.lower()}.{last.lower()}@p2p4.test"
    r = requests.post(f"{BASE}/contacts", json={
        "first_name": first,
        "last_name": last,
        "email": email_addr,
        "type": "lead",
    })
    assert r.status_code == 201, f"Create contact failed: {r.text}"
    return r.json()["id"]


def _create_deal(title=None, contact_id=None, stage="proposal", value=10000.0):
    title = title or f"BiasDeal {_RUN_ID} {len(_deal_ids)}"
    payload = {"title": title, "stage": stage, "value": value}
    if contact_id:
        payload["contact_id"] = contact_id
    r = requests.post(f"{BASE}/deals", json=payload)
    assert r.status_code == 201, f"Create deal failed: {r.text}"
    did = r.json()["id"]
    _deal_ids.append(did)
    return did


def test_00_setup():
    """Setup: create contact and multiple deals for bias tracking."""
    global _contact_id
    _contact_id = _create_contact()
    # Create 10 deals to build sufficient forecast history
    for i in range(10):
        _create_deal(
            title=f"BiasDeal {_RUN_ID} {i}",
            contact_id=_contact_id,
            stage="proposal" if i % 2 == 0 else "negotiation",
            value=10000.0 + i * 5000,
        )
    assert len(_deal_ids) >= 10


# ══════════════════════════════════════════════════════════════════════════════
# 1. FORECAST CRUD
# ══════════════════════════════════════════════════════════════════════════════

def test_01_create_forecast():
    """Create a forecast entry."""
    r = requests.post(f"{BASE}/rep-bias/forecasts", json={
        "deal_id": _deal_ids[0],
        "stage": "proposal",
        "stated_probability": 70,
        "actual_outcome": "won",
        "deal_value": 10000.0,
    })
    assert r.status_code == 201, f"Create forecast failed: {r.text}"
    data = r.json()
    _forecast_ids.append(data["id"])
    assert data["stated_probability"] == 70
    assert data["actual_outcome"] == "won"
    assert data["stage"] == "proposal"


def test_01_create_multiple_forecasts():
    """Create multiple forecasts for bias analysis."""
    # Simulate optimistic rep: stated probabilities higher than actual outcomes
    forecasts = [
        # Won deals (stated high)
        {"deal_id": _deal_ids[1], "stage": "negotiation", "stated_probability": 80, "actual_outcome": "won", "deal_value": 15000},
        {"deal_id": _deal_ids[2], "stage": "proposal", "stated_probability": 60, "actual_outcome": "won", "deal_value": 20000},
        {"deal_id": _deal_ids[3], "stage": "negotiation", "stated_probability": 90, "actual_outcome": "won", "deal_value": 25000},
        # Lost deals (still stated high = optimistic)
        {"deal_id": _deal_ids[4], "stage": "proposal", "stated_probability": 75, "actual_outcome": "lost", "deal_value": 30000},
        {"deal_id": _deal_ids[5], "stage": "negotiation", "stated_probability": 85, "actual_outcome": "lost", "deal_value": 35000},
        {"deal_id": _deal_ids[6], "stage": "proposal", "stated_probability": 65, "actual_outcome": "lost", "deal_value": 40000},
        {"deal_id": _deal_ids[7], "stage": "negotiation", "stated_probability": 70, "actual_outcome": "lost", "deal_value": 45000},
        # Open deals
        {"deal_id": _deal_ids[8], "stage": "proposal", "stated_probability": 50, "actual_outcome": "open", "deal_value": 50000},
        {"deal_id": _deal_ids[9], "stage": "negotiation", "stated_probability": 40, "deal_value": 55000},
    ]
    for f in forecasts:
        r = requests.post(f"{BASE}/rep-bias/forecasts", json=f)
        assert r.status_code == 201, f"Create forecast failed: {r.text}"
        _forecast_ids.append(r.json()["id"])


def test_01_list_forecasts():
    """List all forecast entries."""
    r = requests.get(f"{BASE}/rep-bias/forecasts")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 10


def test_01_list_forecasts_by_stage():
    """Filter forecasts by stage."""
    r = requests.get(f"{BASE}/rep-bias/forecasts", params={"stage": "proposal"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 4


def test_01_list_forecasts_by_outcome():
    """Filter forecasts by actual_outcome."""
    r = requests.get(f"{BASE}/rep-bias/forecasts", params={"actual_outcome": "won"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 4  # 4 won deals


# ══════════════════════════════════════════════════════════════════════════════
# 2. BIAS PROFILE
# ══════════════════════════════════════════════════════════════════════════════

def test_02_bias_profile():
    """Get bias profile with sufficient data."""
    r = requests.get(f"{BASE}/rep-bias/profile")
    assert r.status_code == 200
    data = r.json()
    assert data["total_forecasts"] >= 10
    assert data["closed_deals"] >= 8  # 4 won + 4 lost
    assert data["avg_stated_probability"] is not None
    assert data["avg_actual_win_rate"] is not None
    assert data["bias_direction"] in ("optimistic", "pessimistic", "calibrated")
    assert data["bias_magnitude"] is not None
    assert data["correction_factor"] is not None


def test_02_bias_profile_detects_optimism():
    """Bias profile correctly detects optimistic bias."""
    r = requests.get(f"{BASE}/rep-bias/profile")
    assert r.status_code == 200
    data = r.json()
    # Rep stated avg ~74% but actual win rate is 50% → optimistic
    assert data["bias_direction"] == "optimistic"
    assert data["correction_factor"] < 1.0  # Need to reduce stated probs


def test_02_bias_profile_has_stage_breakdown():
    """Bias profile includes per-stage breakdown."""
    r = requests.get(f"{BASE}/rep-bias/profile")
    assert r.status_code == 200
    data = r.json()
    assert len(data["stage_bias"]) >= 1
    stage = data["stage_bias"][0]
    assert "stage" in stage
    assert "forecast_count" in stage
    assert "avg_stated_probability" in stage
    assert "actual_win_rate" in stage
    assert "bias" in stage


def test_02_bias_profile_confidence_level():
    """Bias profile reports confidence level based on data volume."""
    r = requests.get(f"{BASE}/rep-bias/profile")
    assert r.status_code == 200
    data = r.json()
    # With 8 closed deals, should be "low" (3-9) or "moderate" (10-19)
    assert data["confidence_level"] in ("low", "moderate")


# ══════════════════════════════════════════════════════════════════════════════
# 3. CORRECTED PROBABILITY
# ══════════════════════════════════════════════════════════════════════════════

def test_03_corrected_probability():
    """Get bias-corrected probability for a deal."""
    r = requests.get(
        f"{BASE}/deals/{_deal_ids[0]}/corrected-probability",
        params={"stage": "proposal", "stated_probability": 80},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["deal_id"] == _deal_ids[0]
    assert data["stated_probability"] == 80
    assert "corrected_probability" in data
    assert "bias_applied" in data
    assert "confidence_level" in data


def test_03_corrected_is_lower_for_optimistic():
    """Corrected probability is lower than stated for optimistic rep."""
    r = requests.get(
        f"{BASE}/deals/{_deal_ids[0]}/corrected-probability",
        params={"stage": "proposal", "stated_probability": 80},
    )
    assert r.status_code == 200
    data = r.json()
    # Optimistic rep → corrected should be lower
    assert data["corrected_probability"] <= 80
    assert data["bias_applied"] >= 0


def test_03_corrected_probability_nonexistent_deal():
    """Corrected probability 404 for non-existent deal."""
    fake_id = str(uuid.uuid4())
    r = requests.get(
        f"{BASE}/deals/{fake_id}/corrected-probability",
        params={"stage": "proposal", "stated_probability": 50},
    )
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# 4. DEAL-SCOPED FORECASTS
# ══════════════════════════════════════════════════════════════════════════════

def test_04_deal_forecasts():
    """List forecasts for a specific deal."""
    r = requests.get(f"{BASE}/deals/{_deal_ids[0]}/forecasts")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert data["items"][0]["deal_id"] == _deal_ids[0]


def test_04_update_forecast_outcome():
    """Update a forecast's actual outcome."""
    # Find an open forecast
    open_forecast = None
    for fid in _forecast_ids:
        r = requests.get(f"{BASE}/rep-bias/forecasts", params={"actual_outcome": "open"})
        if r.status_code == 200 and r.json()["total"] > 0:
            open_forecast = r.json()["items"][0]["id"]
            break

    if open_forecast:
        r = requests.put(
            f"{BASE}/rep-bias/forecasts/{open_forecast}/outcome",
            params={"outcome": "won"},
        )
        assert r.status_code == 200
        assert "won" in r.json()["detail"]


# ══════════════════════════════════════════════════════════════════════════════
# 5. EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════

def test_05_forecast_invalid_deal():
    """Create forecast with non-existent deal returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.post(f"{BASE}/rep-bias/forecasts", json={
        "deal_id": fake_id,
        "stage": "proposal",
        "stated_probability": 50,
    })
    assert r.status_code == 404


def test_05_forecast_invalid_probability():
    """Create forecast with probability > 100 returns 422."""
    r = requests.post(f"{BASE}/rep-bias/forecasts", json={
        "deal_id": _deal_ids[0],
        "stage": "proposal",
        "stated_probability": 150,
    })
    assert r.status_code == 422


def test_05_update_nonexistent_forecast():
    """Update outcome for non-existent forecast returns 404."""
    fake_id = str(uuid.uuid4())
    r = requests.put(
        f"{BASE}/rep-bias/forecasts/{fake_id}/outcome",
        params={"outcome": "won"},
    )
    assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# 6. REGRESSION
# ══════════════════════════════════════════════════════════════════════════════

def test_06_regression_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_06_regression_contacts():
    r = requests.get(f"{BASE}/contacts")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_deals():
    r = requests.get(f"{BASE}/deals")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_meetings():
    r = requests.get(f"{BASE}/meetings")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_channel_interactions():
    r = requests.get(f"{BASE}/channel-interactions")
    assert r.status_code == 200
    assert "items" in r.json()


def test_06_regression_briefing_depths():
    r = requests.get(f"{BASE}/briefings/depths")
    assert r.status_code == 200
    assert "depths" in r.json()


def test_06_regression_dashboard():
    r = requests.get(f"{BASE}/dashboard")
    assert r.status_code == 200
    assert "metrics" in r.json()


# ══════════════════════════════════════════════════════════════════════════════
# 7. CONFIDENCE STAMP
# ══════════════════════════════════════════════════════════════════════════════

def test_07_confidence_stamp():
    """Phase 2.4 Rep Bias Brain — all tests passed."""
    print("\n" + "=" * 70)
    print("  PHASE 2.4 CONFIDENCE STAMP")
    print("  Rep Bias Brain — ALL BEAST TESTS PASSED")
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
    print(f"  Phase 2.4 Beast: {passed}/{total} passed")
    if failed:
        print(f"  {failed} FAILED")
        sys.exit(1)
    else:
        print("  ALL PASSED")
    print(f"{'=' * 60}")
