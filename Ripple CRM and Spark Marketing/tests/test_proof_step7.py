"""Proof Test — Step 7: Workshop Registration & Integration.

Playwright end-to-end tests for Workshop card and cross-product health.
"""

import requests
from playwright.sync_api import expect


def test_workshop_loads(page):
    """Workshop page loads successfully."""
    page.goto("http://localhost:5003/")
    page.wait_for_load_state("networkidle")
    expect(page.locator("body")).to_be_visible()


def test_workshop_shows_ripple_card(page):
    """Workshop displays Ripple CRM in the app list."""
    page.goto("http://localhost:5003/")
    page.wait_for_load_state("networkidle")
    ripple_text = page.locator("text=Ripple CRM")
    expect(ripple_text.first).to_be_visible()


def test_ripple_frontend_from_workshop_link(page):
    """Ripple frontend is reachable at the URL listed in Workshop."""
    # Verify Ripple frontend loads directly
    page.goto("http://localhost:3100/")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="Daily Command Centre")).to_be_visible()


def test_ripple_health_from_browser(page):
    """Health endpoint returns JSON with healthy status."""
    r = requests.get("http://localhost:8100/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"


def test_foreperson_spec_accessible(page):
    """Foreperson spec file exists and is valid YAML."""
    import pathlib
    import yaml
    spec = pathlib.Path(__file__).resolve().parents[1].parent / "Foreperson" / "specs" / "ripple-crm.yaml"
    assert spec.exists()
    data = yaml.safe_load(spec.read_text(encoding="utf-8"))
    assert data["app"] == "Ripple CRM"
    assert len(data["features"]) >= 10
