from __future__ import annotations
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    from .config import (
        BASE_URL,
        LOGIN_URL,
        DEFAULT_TIMEOUT,
        SUPER_USER,
        SUPER_PASSWORD,
        TEST_USER,
        TEST_PASSWORD,
    )
except ImportError:
    from config import (
        BASE_URL,
        LOGIN_URL,
        DEFAULT_TIMEOUT,
        SUPER_USER,
        SUPER_PASSWORD,
        TEST_USER,
        TEST_PASSWORD,
    )

UserType = str | None


def start_browser(headless: bool = False):
    """Start a new Playwright browser instance.

    Returns:
        Tuple of (playwright, browser, page)
    """
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=headless)
    page = browser.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)
    return p, browser, page


def close_browser(browser, p):
    """Close the browser and stop Playwright."""
    browser.close()
    p.stop()


def login(
    page, username: str | None = None, password: str | None = None, user_type: UserType = None
) -> str:
    """Login to the Django application.

    Args:
        page: Playwright page instance
        username: Username (defaults based on user_type or config)
        password: Password (defaults based on user_type or config)
        user_type: "test" for test user, "super" for super user, None for explicit credentials

    Returns:
        Current URL after login
    """
    if user_type == 'test':
        username = TEST_USER if username is None else username
        password = TEST_PASSWORD if password is None else password
    elif user_type == 'super':
        username = SUPER_USER if username is None else username
        password = SUPER_PASSWORD if password is None else password
    else:
        if username is None:
            username = SUPER_USER
        if password is None:
            password = SUPER_PASSWORD

    page.goto(f'{BASE_URL}{LOGIN_URL}')
    page.wait_for_load_state('domcontentloaded')

    try:
        page.locator('#djHideToolBarButton').click()
    except Exception:
        pass

    page.fill('input[name=username]', username)
    page.fill('input[name=password]', password)
    page.click('button[type=submit]')

    return page.url
