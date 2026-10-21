"""Accounts app configuration with first-run admin bootstrap."""

import contextlib
import os

from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.db import OperationalError, ProgrammingError
from django.db.models.signals import post_migrate


def _bootstrap_admin(sender, **kwargs) -> None:
    """Create the initial admin after migrations, if env vars are present."""
    # Skip during tests
    if getattr(settings, 'TESTING', False):
        return
    if 'test' in getattr(settings, 'SETTINGS_MODULE', '').lower():
        return
    # Check if test database
    db_name = settings.DATABASES.get('default', {}).get('NAME', '').lower()
    if hasattr(settings, 'DATABASES') and 'test' in db_name:
        return
    if os.environ.get('DJANGO_SKIP_BOOTSTRAP'):
        return
    with contextlib.suppress(OperationalError, ProgrammingError):
        call_command('bootstrap_admin')


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    @staticmethod
    def ready() -> None:
        """Hook bootstrap admin creation to the post-migrate signal."""
        post_migrate.connect(_bootstrap_admin, dispatch_uid='accounts.bootstrap_admin')
