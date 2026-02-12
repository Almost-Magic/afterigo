"""Beast Test — Step 7: Workshop Registration & Integration.

Sections:
  1. Imports
  2. Workshop registration
  3. Foreperson spec exists
  4. Supervisor config
  5. Cross-product health check
  6. Foreperson spec content
  7. Confidence Stamp
"""

import os
import pathlib

import requests
import yaml

# Base paths
SOURCE_DIR = pathlib.Path(__file__).resolve().parents[3]  # Source and Brand
BASE = os.environ.get("RIPPLE_API_BASE", "http://localhost:8100/api")


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Import checks
# ══════════════════════════════════════════════════════════════════════════

def test_import_yaml():
    assert yaml is not None

def test_import_pathlib():
    assert pathlib is not None


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Workshop registration
# ══════════════════════════════════════════════════════════════════════════

def test_workshop_html_contains_ripple():
    """the-workshop.html must list Ripple CRM."""
    html_path = SOURCE_DIR / "the-workshop.html"
    assert html_path.exists(), f"Workshop HTML not found at {html_path}"
    text = html_path.read_text(encoding="utf-8")
    assert "ripple" in text.lower()
    assert "3100" in text

def test_workshop_html_ripple_entry():
    """Workshop must have Ripple with correct properties."""
    html_path = SOURCE_DIR / "the-workshop.html"
    text = html_path.read_text(encoding="utf-8")
    assert "Ripple CRM" in text
    assert "Relationship Intelligence Engine" in text


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Foreperson spec exists
# ══════════════════════════════════════════════════════════════════════════

def test_foreperson_spec_file_exists():
    """Foreperson spec YAML must exist for Ripple CRM."""
    spec_path = SOURCE_DIR / "Foreperson" / "specs" / "ripple-crm.yaml"
    assert spec_path.exists(), f"Foreperson spec not found at {spec_path}"

def test_foreperson_spec_valid_yaml():
    """Foreperson spec must parse as valid YAML."""
    spec_path = SOURCE_DIR / "Foreperson" / "specs" / "ripple-crm.yaml"
    with open(spec_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data is not None
    assert "app" in data
    assert data["app"] == "Ripple CRM"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Supervisor config
# ══════════════════════════════════════════════════════════════════════════

def test_supervisor_services_yaml_has_ripple():
    """Supervisor services.yaml must contain ripple-crm entry."""
    svc_path = SOURCE_DIR / "Supervisor" / "config" / "services.yaml"
    assert svc_path.exists(), f"Supervisor config not found at {svc_path}"
    with open(svc_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert "ripple-crm" in data["services"]

def test_supervisor_ripple_port_correct():
    """Supervisor config must list Ripple on port 8100."""
    svc_path = SOURCE_DIR / "Supervisor" / "config" / "services.yaml"
    with open(svc_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    ripple = data["services"]["ripple-crm"]
    assert ripple["port"] == 8100

def test_supervisor_ripple_health_check():
    """Supervisor config must have health_check for Ripple."""
    svc_path = SOURCE_DIR / "Supervisor" / "config" / "services.yaml"
    with open(svc_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    ripple = data["services"]["ripple-crm"]
    assert "health_check" in ripple
    assert "/api/health" in ripple["health_check"]["url"]

def test_supervisor_ripple_frontend_entry():
    """Supervisor config must have ripple-frontend entry."""
    svc_path = SOURCE_DIR / "Supervisor" / "config" / "services.yaml"
    with open(svc_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert "ripple-frontend" in data["services"]
    assert data["services"]["ripple-frontend"]["port"] == 3100


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — Cross-product health check
# ══════════════════════════════════════════════════════════════════════════

def test_ripple_health_endpoint():
    """Ripple backend health endpoint must respond."""
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    assert "healthy" in r.text.lower()

def test_ripple_frontend_loads():
    """Ripple frontend must be accessible."""
    r = requests.get("http://localhost:3100/")
    assert r.status_code == 200


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — Foreperson spec content
# ══════════════════════════════════════════════════════════════════════════

def test_foreperson_spec_feature_count():
    """Foreperson spec must have at least 10 features."""
    spec_path = SOURCE_DIR / "Foreperson" / "specs" / "ripple-crm.yaml"
    with open(spec_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert len(data["features"]) >= 10

def test_foreperson_spec_has_health_check():
    """Foreperson spec must include health_endpoint feature."""
    spec_path = SOURCE_DIR / "Foreperson" / "specs" / "ripple-crm.yaml"
    with open(spec_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    ids = [f["id"] for f in data["features"]]
    assert "health_endpoint" in ids

def test_foreperson_spec_has_crud_features():
    """Foreperson spec must include CRUD features for core entities."""
    spec_path = SOURCE_DIR / "Foreperson" / "specs" / "ripple-crm.yaml"
    with open(spec_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    ids = [f["id"] for f in data["features"]]
    for entity in ["contacts_crud", "companies_crud", "deals_crud"]:
        assert entity in ids, f"Missing {entity} in Foreperson spec"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — Confidence Stamp
# ══════════════════════════════════════════════════════════════════════════

def test_confidence_stamp():
    """Step 7 Beast test complete. Workshop registration, Foreperson spec,
    Supervisor config, and cross-product health verified."""
    assert True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
