"""User model with role-based authorization (FR-004/FR-005)."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """Extends Django's AbstractUser with an explicit editorial role."""

    class Role(models.TextChoices):
        AUTHOR = 'AUTHOR', 'نویسنده'
        EDITOR = 'EDITOR', 'ویراستار'
        ADMIN = 'ADMIN', 'مدیر'

    username = models.CharField(max_length=100, unique=True, verbose_name='نام کاربری')
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.AUTHOR, verbose_name='نقش'
    )

    objects = UserManager()

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def is_editor(self) -> bool:
        return self.role == self.Role.EDITOR

    @property
    def is_author(self) -> bool:
        return self.role == self.Role.AUTHOR

    def __str__(self) -> str:
        return f'{self.username} ({self.get_role_display()})'
