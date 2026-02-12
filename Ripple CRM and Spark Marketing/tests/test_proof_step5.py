"""Proof Test — Step 5: Import/Export & Settings.

Playwright end-to-end tests for Settings and Import/Export pages.
"""

from playwright.sync_api import expect


def test_settings_page_loads(page):
    """Settings page loads with all sections."""
    page.goto("http://localhost:3100/settings")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="Settings")).to_be_visible()
    expect(page.locator("text=Profile")).to_be_visible()
    expect(page.locator("text=Appearance")).to_be_visible()
    expect(page.locator("text=Relationship Score Weights")).to_be_visible()
    expect(page.locator("text=Data Management")).to_be_visible()


def test_settings_theme_toggle(page):
    """Theme toggle button exists and is clickable."""
    page.goto("http://localhost:3100/settings")
    page.wait_for_load_state("networkidle")
    toggle_btn = page.locator("text=Switch to").first
    expect(toggle_btn).to_be_visible()
    toggle_btn.click()
    # Should still be on settings page
    expect(page.get_by_role("heading", name="Settings")).to_be_visible()


def test_settings_save_button(page):
    """Save settings button works."""
    page.goto("http://localhost:3100/settings")
    page.wait_for_load_state("networkidle")
    save_btn = page.locator("text=Save Settings")
    expect(save_btn).to_be_visible()
    save_btn.click()
    # Should show "Saved" confirmation
    page.wait_for_selector("text=Saved", timeout=3000)


def test_import_export_page_loads(page):
    """Import/Export page loads with tabs."""
    page.goto("http://localhost:3100/import-export")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("heading", name="Import / Export")).to_be_visible()
    # Import tab is default
    expect(page.locator("text=Import Contacts")).to_be_visible()
    expect(page.locator("text=Import Companies")).to_be_visible()


def test_import_export_switch_tab(page):
    """Can switch to Export tab."""
    page.goto("http://localhost:3100/import-export")
    page.wait_for_load_state("networkidle")
    page.locator("button:has-text('Export')").click()
    expect(page.locator("text=Export Contacts")).to_be_visible()
    expect(page.locator("text=Export Deals")).to_be_visible()
    expect(page.locator("text=Download Contacts CSV")).to_be_visible()
    expect(page.locator("text=Download Deals CSV")).to_be_visible()


def test_sidebar_has_import_export(page):
    """Sidebar includes Import/Export nav link."""
    page.goto("http://localhost:3100/")
    page.wait_for_load_state("networkidle")
    link = page.locator("nav a:has-text('Import/Export')")
    expect(link).to_be_visible()
    link.click()
    expect(page.get_by_role("heading", name="Import / Export")).to_be_visible()
