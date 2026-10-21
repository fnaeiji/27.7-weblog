"""Pytest configuration for the blog platform."""

import os

# Must be set before Django imports to prevent bootstrap during test setup
os.environ['DJANGO_SKIP_BOOTSTRAP'] = 'true'


# Ensure test settings are used
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings.test')
