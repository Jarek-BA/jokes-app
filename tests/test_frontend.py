import pytest
from playwright.sync_api import sync_playwright, expect

@pytest.mark.frontend
def test_get_a_joke_button():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("http://127.0.0.1:8000")

        # Check the button is visible
        assert page.locator("#joke-btn").is_visible()

        # Click the button
        page.click("#joke-btn")

        # Explicitly wait until the joke paragraph has non-empty text
        joke_el = page.locator("#joke")
        expect(joke_el).not_to_have_text("", timeout=5000)  # wait up to 5s

        # Now check that some text was actually returned
        joke_text = joke_el.inner_text()
        assert joke_text.strip() != ""

        browser.close()
