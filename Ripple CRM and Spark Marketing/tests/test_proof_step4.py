"""Proof Test — Step 4: Relationship Intelligence (Heuristic v1).

Playwright end-to-end tests for Dashboard and Transparency Portal.
"""

import re
from playwright.sync_api import expect


def test_dashboard_command_centre(page):
    """Dashboard loads with metrics cards and sections."""
    page.goto("http://localhost:3100/")
    page.wait_for_load_state("networkidle")
    # Header — use get_by_role to avoid matching sidebar h1
    expect(page.get_by_role("heading", name="Daily Command Centre")).to_be_visible()
    # 4 metric cards
    expect(page.locator("text=Contacts").first).to_be_visible()
    expect(page.locator("text=Active Deals").first).to_be_visible()
    expect(page.locator("text=Pipeline Value").first).to_be_visible()
    expect(page.locator("text=Overdue Tasks").first).to_be_visible()


def test_dashboard_sections_visible(page):
    """Dashboard shows all data sections."""
    page.goto("http://localhost:3100/")
    page.wait_for_load_state("networkidle")
    for section in ["People to Reach", "Deals Needing Attention",
                    "Overdue Commitments", "Today's Tasks", "Recent Activity"]:
        expect(page.locator(f"text={section}").first).to_be_visible()


def test_dashboard_refresh_button(page):
    """Refresh button exists and is clickable."""
    page.goto("http://localhost:3100/")
    page.wait_for_load_state("networkidle")
    refresh_btn = page.locator("button[title='Refresh']")
    expect(refresh_btn).to_be_visible()
    refresh_btn.click()
    # Should still show dashboard after refresh
    expect(page.get_by_role("heading", name="Daily Command Centre")).to_be_visible()


def test_privacy_dsar_tab(page):
    """Privacy page DSAR tab loads with contact dropdown."""
    page.goto("http://localhost:3100/privacy")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="Transparency Portal")).to_be_visible()
    # DSAR tab should be default
    expect(page.locator("text=Data Subject Access Request")).to_be_visible()
    # Contact dropdown
    expect(page.locator("select").first).to_be_visible()
    # Generate button
    expect(page.locator("text=Generate Report")).to_be_visible()


def test_privacy_consent_log_tab(page):
    """Can switch to Consent Log tab."""
    page.goto("http://localhost:3100/privacy")
    page.locator("button:has-text('Consent Log')").click()
    expect(page.locator("text=Consent Log").first).to_be_visible()


def test_privacy_record_consent_tab(page):
    """Can switch to Record Consent tab and see the form."""
    page.goto("http://localhost:3100/privacy")
    page.locator("button:has-text('Record Consent')").click()
    expect(page.locator("text=Record New Consent")).to_be_visible()
    # Form has required fields
    expect(page.locator("select[name='contact_id']")).to_be_visible()
    expect(page.locator("select[name='consent_type']")).to_be_visible()
    expect(page.locator("select[name='granted']")).to_be_visible()


def test_privacy_generate_dsar_report(page):
    """Generate a DSAR report for an existing contact."""
    import requests
    import uuid
    run_id = uuid.uuid4().hex[:6]
    r = requests.post("http://localhost:8100/api/contacts", json={
        "first_name": f"ProofDSAR{run_id}", "last_name": "Step4",
        "email": f"proofdsar{run_id}@step4.test", "type": "contact",
    })
    assert r.status_code == 201, f"Failed to create contact: {r.status_code} {r.text}"
    contact_id = r.json()["id"]

    page.goto("http://localhost:3100/privacy")
    page.wait_for_load_state("networkidle")

    # Wait for the select dropdown to have options loaded
    dropdown = page.locator("select").first
    dropdown.wait_for(state="visible", timeout=10000)
    # Wait for options to populate (async data fetch)
    page.wait_for_timeout(1000)
    dropdown.select_option(value=contact_id)
    page.locator("text=Generate Report").click()

    # Wait for report to appear
    page.wait_for_selector("text=DSAR Report", timeout=10000)
    expect(page.get_by_role("heading", name="DSAR Report")).to_be_visible()
    expect(page.locator("text=Personal Data")).to_be_visible()
