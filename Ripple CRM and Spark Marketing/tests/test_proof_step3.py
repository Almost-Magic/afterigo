"""Proof/Playwright Verification — Step 3: Deals, Interactions & Timeline
Ripple CRM v3 — Almost Magic Tech Lab
"""

from playwright.sync_api import sync_playwright

BASE = "http://localhost:3100"


def test_deals_pipeline_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(f"{BASE}/deals")
        page.wait_for_load_state("networkidle")
        assert page.locator("h1:has-text('Deal Pipeline')").first.is_visible()

        # Verify Kanban columns exist
        assert page.locator("text=Lead").first.is_visible()
        assert page.locator("text=Qualified").first.is_visible()
        assert page.locator("text=Proposal").first.is_visible()

        # Create a deal
        page.click("text=Add Deal")
        page.wait_for_timeout(500)
        page.fill('input[placeholder="Deal title *"]', "Playwright Deal")
        page.fill('input[placeholder="Value"]', "75000")
        page.click("button:has-text('Create Deal')")
        page.wait_for_timeout(1000)

        # Verify deal appears in pipeline
        assert page.locator("text=Playwright Deal").first.is_visible()
        assert page.locator("text=$75,000").first.is_visible()

        browser.close()


def test_interactions_timeline_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(f"{BASE}/interactions")
        page.wait_for_load_state("networkidle")
        assert page.locator("h1:has-text('Interactions')").first.is_visible()

        # Verify type filter buttons exist
        assert page.locator("button:has-text('Email')").first.is_visible()
        assert page.locator("button:has-text('Call')").first.is_visible()
        assert page.locator("button:has-text('Meeting')").first.is_visible()

        # Verify Log Interaction button
        assert page.locator("text=Log Interaction").first.is_visible()

        browser.close()


def test_tasks_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(f"{BASE}/tasks")
        page.wait_for_load_state("networkidle")
        assert page.locator("h1:has-text('Tasks')").first.is_visible()

        # Create a task
        page.click("text=Add Task")
        page.wait_for_timeout(500)
        page.fill('input[placeholder="Task title *"]', "Playwright Task")
        page.click("button:has-text('Create Task')")
        page.wait_for_timeout(1000)

        # Verify task appears
        assert page.locator("text=Playwright Task").first.is_visible()

        # Verify status filters
        assert page.locator("button:has-text('To Do')").first.is_visible()
        assert page.locator("button:has-text('Done')").first.is_visible()

        browser.close()


def test_commitments_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(f"{BASE}/commitments")
        page.wait_for_load_state("networkidle")
        assert page.locator("h1:has-text('Commitments')").first.is_visible()

        # Create a commitment
        page.locator("button:has-text('Add Commitment')").first.click()
        page.wait_for_timeout(500)
        page.fill('textarea[placeholder="What was promised? *"]', "Deliver proposal by Monday")
        # Click the submit button inside the modal (not the header button)
        page.locator(".fixed >> button[type='submit']").click()
        page.wait_for_timeout(1000)

        # Verify commitment appears
        assert page.locator("text=Deliver proposal by Monday").first.is_visible()

        # Verify filter buttons
        assert page.locator("button:has-text('Pending')").first.is_visible()
        assert page.locator("button:has-text('Fulfilled')").first.is_visible()
        assert page.locator("button:has-text('Overdue Only')").first.is_visible()

        browser.close()


def test_contact_detail_timeline():
    """Verify the activity timeline on the contact detail page."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Create a contact first
        page.goto(f"{BASE}/contacts")
        page.wait_for_load_state("networkidle")
        page.click("text=Add Contact")
        page.wait_for_timeout(500)
        page.fill('input[placeholder="First name *"]', "TimelineProof")
        page.fill('input[placeholder="Last name *"]', "Test")
        page.click("button:has-text('Create')")
        page.wait_for_timeout(1000)

        # Click on the contact to view detail
        page.click("text=TimelineProof Test")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # Verify Activity Timeline section exists
        assert page.locator("text=Activity Timeline").first.is_visible()
        assert page.locator("text=Log Interaction").first.is_visible()

        # Verify Notes section exists
        assert page.locator("text=Notes").first.is_visible()
        assert page.locator('input[placeholder="Add a note..."]').first.is_visible()

        browser.close()
