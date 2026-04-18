"""
Playwright Tool Library

Core library functions for browser automation.
"""

from .browser import start_browser, close_browser, login
from .actions import (
    goto,
    click,
    fill,
    check,
    uncheck,
    select,
    hover,
    press,
    wait_for_load_state,
    wait_for_selector,
)
from .utils import (
    take_screenshot,
    inspect_page,
    debug_page_state,
    get_page_html,
    capture_console_errors,
)
from .permissions import (
    get_user_permissions,
    get_user_permission,
    set_user_permission,
    reset_user_permissions,
    list_permission_fields,
    get_test_user_permissions,
    get_django_permissions,
    grant_app_permission,
    grant_full_app_access,
)

__all__ = [
    # Browser management
    'start_browser',
    'close_browser',
    'login',
    # Actions
    'goto',
    'click',
    'fill',
    'check',
    'uncheck',
    'select',
    'hover',
    'press',
    'wait_for_load_state',
    'wait_for_selector',
    # Utilities
    'take_screenshot',
    'inspect_page',
    'debug_page_state',
    'get_page_html',
    'capture_console_errors',
    # Permissions (UserProfile boolean fields)
    'get_user_permissions',
    'get_user_permission',
    'set_user_permission',
    'reset_user_permissions',
    'list_permission_fields',
    'get_test_user_permissions',
    # Permissions (Django standard - use grant_full_app_access for complete access)
    'get_django_permissions',
    'grant_app_permission',
    'grant_full_app_access',
]
