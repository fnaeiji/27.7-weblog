"""Bootstrap admin tests for User Story 5."""

import pytest
from django.core.management import call_command

from accounts.models import User

pytestmark = pytest.mark.django_db


def test_bootstrap_admin_creates_admin(db):
    """Bootstrap admin created on first run (T096, SC-008)."""
    # Ensure no admin exists
    User.objects.filter(role=User.Role.ADMIN).delete()
    assert User.objects.filter(role=User.Role.ADMIN, is_active=True).count() == 0

    call_command('bootstrap_admin')

    assert User.objects.filter(role=User.Role.ADMIN, is_active=True).count() == 1
    admin = User.objects.get(username='admin')
    assert admin.is_active is True
    assert admin.is_staff is True
    assert admin.is_superuser is True


def test_bootstrap_admin_idempotent(db):
    """Bootstrap admin not duplicated on subsequent runs (T096)."""
    User.objects.filter(role=User.Role.ADMIN).delete()
    call_command('bootstrap_admin')
    call_command('bootstrap_admin')
    call_command('bootstrap_admin')

    assert User.objects.filter(role=User.Role.ADMIN, is_active=True).count() == 1


def test_bootstrap_admin_uses_env_vars(db, monkeypatch):
    """Bootstrap admin uses environment variables for credentials."""
    User.objects.filter(role=User.Role.ADMIN).delete()
    monkeypatch.setenv('APP_BOOTSTRAP_ADMIN_USERNAME', 'customadmin')
    monkeypatch.setenv('APP_BOOTSTRAP_ADMIN_PASSWORD', 'custompass123')

    call_command('bootstrap_admin')

    admin = User.objects.get(role=User.Role.ADMIN)
    assert admin.username == 'customadmin'
    assert admin.check_password('custompass123') is True


def test_bootstrap_admin_skips_when_env_missing(db, monkeypatch):
    """Bootstrap admin skipped when env vars not set (graceful)."""
    User.objects.filter(role=User.Role.ADMIN).delete()
    monkeypatch.delenv('APP_BOOTSTRAP_ADMIN_USERNAME', raising=False)
    monkeypatch.delenv('APP_BOOTSTRAP_ADMIN_PASSWORD', raising=False)

    call_command('bootstrap_admin')

    assert User.objects.filter(role=User.Role.ADMIN, is_active=True).count() == 0
