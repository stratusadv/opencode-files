"""
Permissions management for Playwright testing.

Cascading Permission Structure:
- Child apps inherit parent app permissions through MODEL_PERMISSIONS
- Grant parent app permissions (view, add, change, delete) to access all child apps
- Example: company.change_company cascades to company_location.change_company, etc.

Permission Sources:
1. UserProfile boolean fields (custom can_* permissions)
2. user.user_permissions (Django standard permissions)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _find_project_root() -> Path | None:
    """Find the Django project root by looking for known project files."""
    current = Path.cwd()
    if (current / 'manage.py').exists() or (current / 'system').is_dir():
        return current

    current = Path(__file__).resolve().parent
    search_paths = [current] + list(current.parents)

    for parent in search_paths:
        if (parent / 'manage.py').exists() or (parent / 'system').is_dir():
            return parent

    return None


def _setup_django() -> None:
    """Set up Django environment for ORM access."""
    if 'django' in sys.modules and hasattr(sys.modules['django'], 'setup'):
        return

    project_root = _find_project_root()
    if project_root is None:
        project_root_env = os.environ.get('PLAYWRIGHT_PROJECT_ROOT')
        if project_root_env:
            project_root = Path(project_root_env)
        else:
            raise RuntimeError(
                'Could not find Django project root. '
                'Set PLAYWRIGHT_PROJECT_ROOT env var or ensure project has manage.py or system/ directory.'
            )

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system.development.settings')

    import django

    django.setup()


def get_user_permissions(username: str) -> dict[str, bool]:
    """Get all permission fields for a user from UserProfile.

    Args:
        username: The username to look up

    Returns:
        Dict mapping permission field names to their boolean values
    """
    _setup_django()

    from app.user_profile.models import UserProfile
    from django_spire.auth.user.models import AuthUser

    try:
        user = AuthUser.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
    except AuthUser.DoesNotExist:
        raise ValueError(
            f"User '{username}' does not exist. Ensure migrations are run and the user exists."
        )
    except UserProfile.DoesNotExist:
        raise ValueError(
            f"UserProfile does not exist for user '{username}'. Ensure the user exists."
        )

    permissions = {}
    skip_fields = {
        'id',
        'user',
        'is_active',
        'is_deleted',
        'created_datetime',
        'created_by',
        'updated_by',
        'history_events',
        '_options',
    }

    for field in profile._meta.get_fields():
        if not hasattr(field, 'name'):
            continue
        field_name = field.name
        if field_name in skip_fields:
            continue
        if hasattr(field, 'related_model') and field.related_model:
            continue
        value = getattr(profile, field_name, None)
        if isinstance(value, bool):
            permissions[field_name] = value

    return permissions


def get_user_permission(username: str, permission: str) -> bool | None:
    """Get a specific permission value for a user.

    Args:
        username: The username to look up
        permission: The permission field name

    Returns:
        The boolean value of the permission, or None if not found
    """
    permissions = get_user_permissions(username)
    return permissions.get(permission)


def set_user_permission(username: str, permission: str, value: bool) -> bool:
    """Set a specific permission for a user.

    Args:
        username: The username to modify
        permission: The permission field name
        value: The boolean value to set

    Returns:
        The new value that was set

    Examples:
        # Set UserProfile boolean field:
        set_user_permission('test', 'can_approve_procurement_purchase_orders', True)

        # Grant Django standard permission (cascades to child apps):
        # from django.contrib.auth.models import Permission
        # from django_spire.auth.user.models import AuthUser
        # user = AuthUser.objects.get(username='test')
        # perm = Permission.objects.get(codename='change_company')
        # user.user_permissions.add(perm)
        # Now user can: company.change_company, company_location.change_company, etc.
    """
    _setup_django()

    from app.user_profile.models import UserProfile
    from django_spire.auth.user.models import AuthUser

    user = AuthUser.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)

    if not hasattr(profile, permission):
        raise ValueError(f"UserProfile does not have permission field '{permission}'")

    setattr(profile, permission, value)
    profile.save()

    return value


def reset_user_permissions(username: str, **permissions: bool) -> dict[str, bool]:
    """Set multiple permission fields at once.

    Args:
        username: The username to modify
        **permissions: Key-value pairs of permission_name=value

    Returns:
        Dict of all permission values after update
    """
    _setup_django()

    from app.user_profile.models import UserProfile
    from django_spire.auth.user.models import AuthUser

    user = AuthUser.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)

    for permission, value in permissions.items():
        if hasattr(profile, permission):
            setattr(profile, permission, value)

    profile.save()

    return get_user_permissions(username)


def list_permission_fields() -> list[str]:
    """List all available permission field names.

    Returns:
        List of permission field names available on UserProfile
    """
    _setup_django()

    from app.user_profile.models import UserProfile
    from django.db.models import BooleanField

    skip_fields = {
        'id',
        'user',
        'is_active',
        'is_deleted',
        'created_datetime',
        'created_by',
        'updated_by',
        'history_events',
        '_options',
    }

    fields = []
    for field in UserProfile._meta.get_fields():
        if not hasattr(field, 'name'):
            continue
        field_name = field.name
        if field_name in skip_fields:
            continue
        if hasattr(field, 'related_model') and field.related_model:
            continue
        try:
            field_obj = UserProfile._meta.get_field(field_name)
            if isinstance(field_obj, BooleanField):
                fields.append(field_name)
        except Exception:
            continue

    return fields


def get_test_user_permissions() -> dict[str, bool]:
    """Convenience function to get permissions for the default test user.

    Returns:
        Dict of test user's permission fields
    """
    try:
        from ..config import TEST_USER

        return get_user_permissions(TEST_USER)
    except ImportError:
        return get_user_permissions('test')


def get_django_permissions(username: str) -> list[str]:
    """Get Django standard permissions for a user.

    Args:
        username: The username to look up

    Returns:
        List of permission codenames (e.g., 'change_company', 'view_company')
    """
    _setup_django()

    from django_spire.auth.user.models import AuthUser

    try:
        user = AuthUser.objects.get(username=username)
    except AuthUser.DoesNotExist:
        raise ValueError(f"User '{username}' does not exist.")

    return [perm.codename for perm in user.user_permissions.all()]


def grant_app_permission(username: str, action: str, app_label: str) -> list[str]:
    """Grant a Django permission to a user. Use this for standard CRUD permissions.

    IMPORTANT: This adds only ONE action (e.g., 'change'). To fully access an app,
    you typically need all four: view, add, change, delete.

    Args:
        username: The username to modify
        action: The permission action ('view', 'add', 'change', 'delete')
        app_label: The Django app label (e.g., 'company', 'asset')

    Returns:
        List of all user's Django permissions after the update

    Examples:
        # Add single permission:
        grant_app_permission('test', 'change', 'company')

        # To fully access an app, grant all CRUD permissions:
        grant_app_permission('test', 'view', 'company')
        grant_app_permission('test', 'add', 'company')
        grant_app_permission('test', 'change', 'company')
        grant_app_permission('test', 'delete', 'company')
    """
    _setup_django()

    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    from django_spire.auth.user.models import AuthUser

    user = AuthUser.objects.get(username=username)

    content_types = ContentType.objects.filter(model__in=[app_label, app_label.rstrip('s')])
    if not content_types.exists():
        raise ValueError(f"App '{app_label}' not found in ContentTypes.")

    content_type = content_types.first()
    codename = f'{action}_{app_label}'

    perm = Permission.objects.get(codename=codename, content_type=content_type)
    user.user_permissions.add(perm)

    return get_django_permissions(username)


def grant_full_app_access(username: str, app_label: str) -> list[str]:
    """Grant full CRUD access to an app (all four: view, add, change, delete).

    Args:
        username: The username to modify
        app_label: The Django app label (e.g., 'company', 'asset')

    Returns:
        List of all user's Django permissions after the update

    Example:
        grant_full_app_access('test', 'company')
        # Grants: company.view_company, company.add_company,
        #         company.change_company, company.delete_company
        # Cascades to: company_location, company_contact, etc.
    """
    _setup_django()

    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    from django_spire.auth.user.models import AuthUser

    user = AuthUser.objects.get(username=username)

    content_types = ContentType.objects.filter(model__in=[app_label, app_label.rstrip('s')])
    if not content_types.exists():
        raise ValueError(f"App '{app_label}' not found in ContentTypes.")

    content_type = content_types.first()

    permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=[
            f'view_{app_label}',
            f'add_{app_label}',
            f'change_{app_label}',
            f'delete_{app_label}',
        ],
    )

    user.user_permissions.add(*permissions)

    return get_django_permissions(username)
