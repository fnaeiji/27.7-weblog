"""Create the bootstrap admin from environment variables (idempotent)."""

import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = 'Create the initial admin from APP_BOOTSTRAP_ADMIN_* env vars (idempotent).'

    def handle(self, *args, **options):
        username = os.environ.get('APP_BOOTSTRAP_ADMIN_USERNAME')
        password = os.environ.get('APP_BOOTSTRAP_ADMIN_PASSWORD')
        if not username or not password:
            self.stdout.write(self.style.WARNING('Bootstrap admin env vars not set; skipping.'))
            return
        if User.objects.filter(role=User.Role.ADMIN, is_active=True).exists():
            self.stdout.write(self.style.SUCCESS('Admin already exists, skipping.'))
            return
        User.objects.bootstrap_admin(username, password)
        self.stdout.write(self.style.SUCCESS(f'Bootstrap admin created: {username}'))
