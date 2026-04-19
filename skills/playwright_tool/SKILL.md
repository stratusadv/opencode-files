---
name: playwright_tool
description: Browser automation library with reusable functions and test scripts
---

# Playwright Tool

> **Library Location**: `~/.config/opencode/tools/playwright_tool/`
>
> **Project Entry Points**: `{project_root}/.opencode/scripts/grant_perm.py`, `{project_root}/.opencode/scripts/playwright/`

## Overview

The Playwright Tool provides a browser automation library for testing web applications. It consists of reusable library functions and a structured folder for disposable test scripts.

### Key Principles
- **Library + Scripts Pattern**: Library provides building blocks, scripts are disposable test code
- **No Persistent State**: Each script starts fresh, browser closes when script ends
- **Absolute Imports**: Scripts import from library using absolute paths
- **Script Discovery**: Scripts live in `scripts/` folder with descriptive names

## Core Architecture

### File Structure

**Library** (`~/.config/opencode/tools/playwright_tool/lib/`):
```
lib/
├── __init__.py          # Exports all functions
├── browser.py           # Browser management (start, close, login)
├── actions.py           # Action functions (goto, click, fill, etc.)
├── utils.py             # Utilities (screenshot, inspect_page, etc.)
├── permissions.py       # Permission management
└── config.py            # Configuration
```

**Project-Specific** (`{project_root}/.opencode/`):
```
.opencode/
├── scripts/playwright/ # Test scripts (scratchpad)
│   ├── login.py
│   └── test_sales_order.py
└── screenshots/         # Screenshot output
```

### Library Functions

**Browser Management** (`lib/browser.py`):
- `start_browser(headless=False)` - Start browser, returns (p, browser, page)
- `close_browser(browser, p)` - Close browser and stop Playwright
- `login(page, user_type=None)` - Login to Django application (`user_type="test"` or `user_type="super"`)

**Actions** (`lib/actions.py`):
- `goto(page, url)` - Navigate to URL (relative or absolute)
- `click(page, selector)` - Click element
- `fill(page, selector, value)` - Fill input field
- `check(page, selector)` - Check checkbox/radio
- `uncheck(page, selector)` - Uncheck checkbox
- `select(page, selector, value)` - Select dropdown option
- `hover(page, selector)` - Hover over element
- `press(page, selector, key)` - Press key on element
- `wait_for_load_state(page, state)` - Wait for load state
- `wait_for_selector(page, selector, timeout)` - Wait for element

**Utilities** (`lib/utils.py`):
- `take_screenshot(page, filename)` - Take screenshot
- `inspect_page(page)` - List all clickable elements
- `debug_page_state(page, step_name)` - Debug page state
- `get_page_html(page, max_length)` - Get page HTML
- `capture_console_errors(page)` - Set up console error capture

## Permissions Tool

The permissions module (`lib/permissions.py`) manages Django user permissions for testing.

### Cascading Permission Structure

Child apps inherit parent app permissions through `MODEL_PERMISSIONS`. Grant parent app permissions to access all child apps:
- `company.change_company` cascades to `company_location.change_company`, `company_contact.change_company`, etc.

### Permission Types

1. **UserProfile Boolean Fields** - Custom `can_*` permissions defined on the UserProfile model
2. **Django Standard Permissions** - Standard `view`, `add`, `change`, `delete` permissions on models

### UserProfile Permissions (`lib/permissions.py`)

```python
from lib.permissions import (
    get_user_permissions,    # Get all UserProfile boolean fields
    get_user_permission,     # Get specific UserProfile field
    set_user_permission,     # Set a UserProfile boolean field
    reset_user_permissions,  # Set multiple UserProfile fields
    list_permission_fields,  # List available UserProfile fields
    get_test_user_permissions,  # Convenience for test user
)
```

### Django Standard Permissions

```python
from lib.permissions import (
    get_django_permissions,      # Get all Django permissions for user
    grant_app_permission,        # Grant single permission (view/add/change/delete)
    grant_full_app_access,       # Grant full CRUD access to an app
)
```

### Usage Examples

**Configure Credentials** (`lib/config.py`):
```python
SUPER_USER = "stratus"
SUPER_PASSWORD = "stratus"

TEST_USER = "test"
TEST_PASSWORD = "test"
```

**Login as Test User**:
```python
from lib.browser import start_browser, close_browser, login

p, browser, page = start_browser(headless=False)
try:
    login(page, user_type="test")  # Uses TEST_USER/TEST_PASSWORD
finally:
    close_browser(browser, p)
```

**Grant Full App Access** (includes all CRUD + cascading to child apps):
```python
from lib.permissions import grant_full_app_access, get_django_permissions

# Grant full access to company app
grant_full_app_access("test", "company")
# Now has: company.view_company, company.add_company,
#          company.change_company, company.delete_company
# Plus cascades to company_location, company_contact, etc.

print(get_django_permissions("test"))
```

**Grant Single Permission**:
```python
from lib.permissions import grant_app_permission

grant_app_permission("test", "view", "company")
# Adds: company.view_company only
```

**Check User Permissions**:
```python
from lib.permissions import get_django_permissions, get_user_permissions

# Django standard permissions
print(get_django_permissions("test"))
# ['add_salespurchaseorder', 'change_salespurchaseorder', ...]

# UserProfile boolean fields
print(get_user_permissions("test"))
# {'can_approve_procurement_purchase_orders': True}
```

**Set UserProfile Permission**:
```python
from lib.permissions import set_user_permission

set_user_permission("test", "can_approve_procurement_purchase_orders", True)
```

### Running Permission Scripts (CLI)

Run from project root (where `manage.py` is). Uses `Path.home()` to dynamically locate the tool:

```bash
# Grant view permission to an app
python .opencode/scripts/grant_perm.py grant -u test -a asset --action view

# Grant full CRUD access to an app
python .opencode/scripts/grant_perm.py full -u test -a company

# List user's permissions
python .opencode/scripts/grant_perm.py list -u test

# Filter by app
python .opencode/scripts/grant_perm.py list -u test --app asset

# Check specific permission
python .opencode/scripts/grant_perm.py check -u test -p view_asset

# List available UserProfile permission fields
python .opencode/scripts/grant_perm.py fields

# Set UserProfile boolean permission
python .opencode/scripts/grant_perm.py set -u test --perm can_approve -v True
```

### Running Playwright Scripts

```bash
# Run a playwright script from project root
python .opencode/scripts/playwright/__main__.py login.py

# Run another script
python .opencode/scripts/playwright/__main__.py check_sidebar.py
```

## Implementation Guide

### Writing Scripts

Scripts are disposable test code. Write them in `scripts/`, run them, modify as needed.

**DON'T**: Create reusable modules or import scripts into other code

```python
# ❌ DON'T: Importing scripts as modules
from scripts.login import main
main()  # Scripts are not meant to be imported
```

**DO**: Write self-contained scripts that use library functions

```python
# ✅ DO: Self-contained script using library
from __future__ import annotations
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.browser import start_browser, close_browser, login
from lib.actions import goto, click
from lib.utils import inspect_page, take_screenshot

def main():
    p, browser, page = start_browser(headless=False)
    
    try:
        # Login and let redirect happen naturally
        login(page)
        page.wait_for_timeout(2000)  # Allow redirect to complete
        
        # Now inspect the home page or navigate from there
        inspect_page(page)
        
        # To click sidebar links, use text selectors
        # click(page, "text=Sales Orders")
        
        take_screenshot(page, "home.png")
    finally:
        close_browser(browser, p)

if __name__ == "__main__":
    main()
```

### Running Scripts

Execute scripts directly with Python:

```bash
python .config/opencode/tools/playwright_tool/scripts/login.py
```

### Configuration

Edit `lib/config.py` to customize settings:

```python
BASE_URL = "http://localhost:8000"
LOGIN_URL = "/django_spire/auth/login/"
DEFAULT_TIMEOUT = 10000
SCREENSHOT_DIR = ".opencode/screenshots"

SUPER_USER = "stratus"
SUPER_PASSWORD = "stratus"

TEST_USER = "test"
TEST_PASSWORD = "test"
```

### Example: Complete Workflow

```python
# .config/opencode/tools/playwright_tool/scripts/check_user_form.py
from __future__ import annotations
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.browser import start_browser, close_browser, login
from lib.actions import goto
from lib.utils import (
    inspect_page,
    debug_page_state,
    take_screenshot,
    capture_console_errors,
)
from lib.permissions import grant_full_app_access, get_django_permissions

def main():
    p, browser, page = start_browser(headless=False)
    get_errors = capture_console_errors(page)
    
    try:
        # Login
        login(page)
        
        # Navigate to company page
        goto(page, "/django_spire/companies/")
        
        # Inspect page
        inspect_page(page)
        
        # Debug state
        debug_page_state(page, "company_list")
        
        # Take screenshot
        take_screenshot(page, "company_page.png")
        
        # Check console errors
        errors = get_errors()
        print(f"Console errors: {len(errors)}")
        for err in errors:
            print(f"  - {err['text']}")
            
    finally:
        close_browser(browser, p)

if __name__ == "__main__":
    main()
```

## Login Redirect Behavior

After login, always let the redirect happen naturally. The login function should:
1. Submit the login form
2. Wait for `domcontentloaded` state (not `networkidle`)
3. Add a small timeout (1-2s) to allow redirects to complete naturally

```python
def main():
    p, browser, page = start_browser(headless=False)
    
    try:
        # Login - let redirect happen naturally
        login(page)
        page.wait_for_timeout(2000)  # Allow redirect to complete
        
        # Now navigate from the home page
        # DO NOT manually goto() the home page - the redirect handles it
        
        inspect_page(page)
        
    finally:
        close_browser(browser, p)
```

### Why Not Use `networkidle`?

- `networkidle` waits for all network requests to finish, which can timeout on pages with:
  - Live reload connections (`__reload__`, `__debug__`)
  - WebSocket connections
  - Third-party analytics/tracking scripts
- `domcontentloaded` + timeout is faster and more reliable for SPA navigation

### Navigation from Home Page

After login redirect lands on the home page (`/`), you can navigate using:
- `inspect_page(page)` to see available navigation links
- `click(page, "text=Link Text")` to click sidebar links
- Direct URL navigation via `goto()`

## Code Review Checklist

When reviewing Playwright scripts, verify the following:

1. **Absolute Imports**: Verify scripts use absolute imports from `lib/`, not relative imports
2. **Self-Contained**: Confirm scripts are standalone and not imported by other code
3. **Proper Cleanup**: Check that `close_browser()` is called in `finally` block
4. **Error Capture**: Verify `capture_console_errors()` is used for debugging
5. **Screenshots**: Confirm screenshots are taken at key workflow steps
6. **Descriptive Names**: Scripts should have descriptive names (not `test.py`, `temp.py`)
7. **No Hardcoded URLs**: Use `BASE_URL` from config, not hardcoded URLs
8. **Headless Mode**: Scripts should default to `headless=False` for debugging
9. **Wait States**: Verify `wait_for_load_state()` is called after navigation
10. **Selectors**: Prefer specific selectors (`text=`, `#id`, `[name='field']`) over generic ones

## Known Limitations

- **No Persistent State**: Browser closes when script ends. Cannot maintain state across scripts.
- **No Interactive Mode**: REPL/interactive mode not supported. Use scripts instead.
- **Sequential Execution**: Scripts run sequentially, not in parallel.

## Related Skills

- [python-style](../python-style/SKILL.md) - Python coding standards
- [testing](../testing/SKILL.md) - Django testing best practices
- [permissions](../permissions/SKILL.md) - Django permission patterns and cascading structure
