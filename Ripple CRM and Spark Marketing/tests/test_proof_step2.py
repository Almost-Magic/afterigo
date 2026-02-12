"""Proof/Playwright Verification — Step 2: Contact & Company CRUD
Ripple CRM v3 — Almost Magic Tech Lab
"""

from playwright.sync_api import expect

BASE = "http://localhost:3100"


def test_contacts_page_and_crud(page):
    # Navigate to contacts
    page.goto(f"{BASE}/contacts")
    page.wait_for_load_state("networkidle")
    assert page.locator("h1:has-text('Contacts')").first.is_visible()

    # Click Add Contact
    page.click("text=Add Contact")
    page.wait_for_timeout(500)

    # Fill form
    page.fill('input[placeholder="First name *"]', "Playwright")
    page.fill('input[placeholder="Last name *"]', "Test")
    page.fill('input[placeholder="Email"]', "playwright@test.com.au")
    page.fill('input[placeholder="Role"]', "Tester")

    # Submit
    page.click("button:has-text('Create')")
    page.wait_for_timeout(1000)

    # Verify contact appears in list
    assert page.locator("text=Playwright Test").first.is_visible()

    # Click on contact to view detail
    page.click("text=Playwright Test")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    assert page.locator("text=Playwright").first.is_visible()

    # Verify detail sections exist
    assert page.locator("text=Details").first.is_visible()
    assert page.locator("text=Activity Timeline").first.is_visible()


def test_companies_page_and_crud(page):
    page.goto(f"{BASE}/companies")
    page.wait_for_load_state("networkidle")
    assert page.locator("h1:has-text('Companies')").first.is_visible()

    # Create company
    page.click("text=Add Company")
    page.wait_for_timeout(500)
    page.fill('input[placeholder="Company name *"]', "Playwright Corp")
    page.fill('input[placeholder="ABN"]', "11111111111")
    page.fill('input[placeholder="Industry"]', "Testing")
    page.click("button:has-text('Create')")
    page.wait_for_timeout(1000)

    # Verify company appears
    assert page.locator("text=Playwright Corp").first.is_visible()


def test_contacts_search(page):
    page.goto(f"{BASE}/contacts")
    page.wait_for_load_state("networkidle")

    # Search for existing contact
    page.fill('input[placeholder="Search contacts..."]', "Playwright")
    page.wait_for_timeout(1000)
    assert page.locator("text=Playwright Test").first.is_visible()

    # Search for nonexistent
    page.fill('input[placeholder="Search contacts..."]', "ZZZZNONEXISTENT")
    page.wait_for_timeout(1000)
