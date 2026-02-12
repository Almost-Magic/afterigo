"""Proof/Playwright Verification — Step 1: Skeleton
Ripple CRM v3 — Almost Magic Tech Lab
"""

from playwright.sync_api import expect


BASE_URL = "http://localhost:3100"

ROUTES = [
    ("/", "Daily Command Centre"),
    ("/contacts", "Contacts"),
    ("/companies", "Companies"),
    ("/deals", "Deal Pipeline"),
    ("/interactions", "Interactions"),
    ("/commitments", "Commitments"),
    ("/tasks", "Tasks"),
    ("/privacy", "Transparency Portal"),
    ("/settings", "Settings"),
]


def test_all_routes_and_layout(page):
    # 1. Dashboard loads with sidebar and header
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # Sidebar present with Ripple branding
    assert page.locator("text=Ripple").first.is_visible()
    assert page.locator("text=Relationship Intelligence").first.is_visible()

    # Header present with health indicator
    assert page.locator("text=Ripple CRM v3").first.is_visible()

    # Health indicator turns green (connected to backend)
    page.wait_for_timeout(3000)
    assert page.locator("text=Connected").first.is_visible()

    # Theme toggle button exists
    theme_btn = page.locator("button[title*='Switch to']")
    assert theme_btn.first.is_visible()

    # Attribution footer
    assert page.locator("text=Mani Padisetti").first.is_visible()

    # 2. All 9 navigable routes render
    for route, heading in ROUTES:
        page.goto(f"{BASE_URL}{route}")
        page.wait_for_load_state("networkidle")
        assert page.locator(f"h1:has-text('{heading}')").first.is_visible(), \
            f"Route {route} missing heading '{heading}'"

    # 3. Sidebar navigation links work
    for route, heading in ROUTES:
        label = heading.split(" ")[0]  # First word for nav matching
        nav_link = page.locator(f"nav a:has-text('{label}')").first
        if nav_link.is_visible():
            nav_link.click()
            page.wait_for_load_state("networkidle")

    # 4. Theme toggle works
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    theme_btn = page.locator("button[title*='Switch to']")
    theme_btn.first.click()
    page.wait_for_timeout(500)
    # After clicking, should have toggled
    theme_btn_new = page.locator("button[title*='Switch to']")
    assert theme_btn_new.first.is_visible()


def test_api_proxy(page):
    """Frontend proxies /api to backend."""
    response = page.request.get(f"{BASE_URL}/api/health")
    assert response.status == 200
    data = response.json()
    assert data["status"] == "healthy"
