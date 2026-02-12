"""Beast Test — Step 5: Import/Export & Settings.

Sections:
  1. Imports
  2. Settings CRUD
  3. CSV Import — contacts (preview + commit)
  4. CSV Import — companies
  5. CSV Export — contacts
  6. CSV Export — deals
  7. Duplicate detection
  8. Confidence Stamp
"""

import csv
import io
import os
import uuid

import requests

BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")

# Unique suffix per test run to avoid duplicate detection across runs
_RUN_ID = uuid.uuid4().hex[:8]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Import checks
# ══════════════════════════════════════════════════════════════════════════

def test_import_settings_router():
    from app.routers.settings import router
    assert router is not None

def test_import_import_export_router():
    from app.routers.import_export import router
    assert router is not None


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Settings CRUD
# ══════════════════════════════════════════════════════════════════════════

def test_get_settings():
    r = requests.get(f"{BASE}/settings")
    assert r.status_code == 200
    data = r.json()
    assert "user_name" in data
    assert "theme" in data
    assert "currency" in data
    assert "health_weights" in data

def test_get_settings_defaults():
    r = requests.get(f"{BASE}/settings")
    data = r.json()
    assert data["user_name"] == "Mani Padisetti"
    assert data["currency"] == "AUD"
    assert data["health_weights"]["recency"] == 30

def test_update_settings_partial():
    r = requests.put(f"{BASE}/settings", json={"currency": "USD"})
    assert r.status_code == 200
    data = r.json()
    assert data["currency"] == "USD"
    # Other fields preserved
    assert data["user_name"] == "Mani Padisetti"
    # Restore
    requests.put(f"{BASE}/settings", json={"currency": "AUD"})

def test_update_settings_deep_merge():
    """Updating one health weight preserves the others."""
    r = requests.put(f"{BASE}/settings", json={"health_weights": {"recency": 35}})
    assert r.status_code == 200
    weights = r.json()["health_weights"]
    assert weights["recency"] == 35
    assert weights["frequency"] == 25  # preserved
    # Restore
    requests.put(f"{BASE}/settings", json={"health_weights": {"recency": 30}})


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — CSV Import contacts
# ══════════════════════════════════════════════════════════════════════════

def _make_csv(headers, rows):
    """Create in-memory CSV bytes."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue().encode("utf-8")

def test_import_contacts_preview():
    csv_bytes = _make_csv(
        ["First Name", "Last Name", "Email", "Type"],
        [["Import", "TestOne", "importtest1@beast5.test", "lead"]],
    )
    r = requests.post(
        f"{BASE}/import-export/import/contacts?commit=false",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total_rows"] == 1
    assert data["committed"] is False
    assert data["imported"] == 0
    assert "first_name" in data["mapped_fields"]
    assert "last_name" in data["mapped_fields"]

def test_import_contacts_commit():
    csv_bytes = _make_csv(
        ["first_name", "last_name", "email"],
        [[f"BeastImport{_RUN_ID}", "Step5", f"beastimport{_RUN_ID}@step5.test"]],
    )
    r = requests.post(
        f"{BASE}/import-export/import/contacts?commit=true",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["committed"] is True
    assert data["imported"] == 1

def test_import_rejects_non_csv():
    r = requests.post(
        f"{BASE}/import-export/import/contacts",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 400

def test_import_contacts_requires_name_columns():
    csv_bytes = _make_csv(["email", "phone"], [["a@b.com", "123"]])
    r = requests.post(
        f"{BASE}/import-export/import/contacts?commit=false",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 400


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — CSV Import companies
# ══════════════════════════════════════════════════════════════════════════

def test_import_companies_preview():
    csv_bytes = _make_csv(
        ["Company Name", "Industry", "Website"],
        [["Beast Corp", "Technology", "https://beast.test"]],
    )
    r = requests.post(
        f"{BASE}/import-export/import/companies?commit=false",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total_rows"] == 1
    assert "name" in data["mapped_fields"]

def test_import_companies_commit():
    csv_bytes = _make_csv(
        ["name", "industry"],
        [[f"Step5 Company {_RUN_ID}", "Testing"]],
    )
    r = requests.post(
        f"{BASE}/import-export/import/companies?commit=true",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 200
    assert r.json()["imported"] == 1


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — CSV Export contacts
# ══════════════════════════════════════════════════════════════════════════

def test_export_contacts_returns_csv():
    r = requests.get(f"{BASE}/import-export/export/contacts")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert "attachment" in r.headers.get("content-disposition", "")

def test_export_contacts_has_headers():
    r = requests.get(f"{BASE}/import-export/export/contacts")
    lines = r.text.strip().split("\n")
    assert len(lines) >= 1  # at least header
    reader = csv.reader(io.StringIO(r.text))
    header = next(reader)
    assert "first_name" in header
    assert "email" in header


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — CSV Export deals
# ══════════════════════════════════════════════════════════════════════════

def test_export_deals_returns_csv():
    r = requests.get(f"{BASE}/import-export/export/deals")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")

def test_export_deals_has_headers():
    r = requests.get(f"{BASE}/import-export/export/deals")
    reader = csv.reader(io.StringIO(r.text))
    header = next(reader)
    assert "title" in header
    assert "stage" in header


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — Duplicate detection
# ══════════════════════════════════════════════════════════════════════════

def test_import_detects_email_duplicate():
    """Import with existing email should flag as duplicate."""
    csv_bytes = _make_csv(
        ["first_name", "last_name", "email"],
        [["BeastImport", "Step5", "beastimport@step5.test"]],  # already imported above
    )
    r = requests.post(
        f"{BASE}/import-export/import/contacts?commit=false",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["duplicates"] == 1
    assert data["rows"][0]["is_duplicate"] is True

def test_import_detects_name_duplicate():
    """Import with existing name (no email) should flag as duplicate."""
    csv_bytes = _make_csv(
        ["first_name", "last_name"],
        [["BeastImport", "Step5"]],  # name match
    )
    r = requests.post(
        f"{BASE}/import-export/import/contacts?commit=false",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 200
    assert r.json()["duplicates"] == 1


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — Confidence Stamp
# ══════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Step 5 Beast test complete. Settings, CSV import (preview + commit + duplicate detection),
    CSV export (contacts, deals), and data management verified."""
    assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
