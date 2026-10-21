"""Custom user manager with role-aware helpers (FR-002)."""

from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """Manager for :class:`accounts.models.User`."""

    def create_user(self, username, password=None, role=None, **extra_fields):
        """Create and save a regular user."""
        if not username:
            msg = 'Users must have a username.'
            raise ValueError(msg)
        role = role or self.model.Role.AUTHOR
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Create and save an admin user (used by ``createsuperuser``)."""
        extra_fields.setdefault('role', self.model.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

    def bootstrap_admin(self, username, password):
        """Create the initial admin if none exists (idempotent)."""
        if self.filter(role=self.model.Role.ADMIN, is_active=True).exists():
            return None
        return self.create_superuser(username, password)
