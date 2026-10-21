"""Test settings for the blog platform.

Imported by pytest-django (see ``pyproject.toml``). Keeps tests fast and
deterministic: no network, in-memory-ish SQLite, fast password hashing.
"""

from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = 'test-secret-key-not-for-production'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Use a local SQLite file so ``--reuse-db`` can skip recreation between runs.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_db.sqlite3',
    }
}
