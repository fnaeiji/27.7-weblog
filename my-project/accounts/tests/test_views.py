"""Authentication view tests for User Story 5."""

import pytest
from django.urls import reverse

from accounts.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin(db):
    return User.objects.create_user(username='admin1', password='pass123', role=User.Role.ADMIN)


@pytest.fixture
def editor(db):
    return User.objects.create_user(username='editor1', password='pass123', role=User.Role.EDITOR)


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author1', password='pass123', role=User.Role.AUTHOR)


@pytest.fixture
def inactive_user(db):
    return User.objects.create_user(
        username='inactive1', password='pass123', role=User.Role.AUTHOR, is_active=False
    )


def test_login_page_accessible(client):
    """Login page loads correctly (T095)."""
    response = client.get(reverse('login'))
    assert response.status_code == 200
    assert 'accounts/login.html' in [t.name for t in response.templates]


def test_login_post_authenticates(client, admin):
    """Valid credentials authenticate and redirect (T095)."""
    response = client.post(
        reverse('login'),
        {'username': 'admin1', 'password': 'pass123'},
        follow=True,
    )
    assert response.status_code == 200
    # Should redirect to manager dashboard for admin
    assert response.redirect_chain[-1][0].endswith('/manager/dashboard/')


def test_role_redirect_admin(client, admin):
    """Admin redirects to manager dashboard on login (T097)."""
    response = client.post(
        reverse('login'),
        {'username': 'admin1', 'password': 'pass123'},
        follow=True,
    )
    assert response.status_code == 200
    assert response.redirect_chain[-1][0].endswith('/manager/dashboard/')


def test_role_redirect_editor(client, editor):
    """Editor redirects to editor queue on login (T097)."""
    response = client.post(
        reverse('login'),
        {'username': 'editor1', 'password': 'pass123'},
        follow=True,
    )
    assert response.status_code == 200
    assert response.redirect_chain[-1][0].endswith('/editor/queue/')


def test_role_redirect_author(client, author):
    """Author redirects to author dashboard on login (T097)."""
    response = client.post(
        reverse('login'),
        {'username': 'author1', 'password': 'pass123'},
        follow=True,
    )
    assert response.status_code == 200
    assert response.redirect_chain[-1][0].endswith('/author/dashboard/')


def test_inactive_user_login_denied(client, inactive_user):
    """Inactive user cannot log in (T098)."""
    response = client.post(
        reverse('login'),
        {'username': 'inactive1', 'password': 'pass123'},
        follow=True,
    )
    # Should not authenticate, stay on login page or show error
    assert response.status_code == 200
    # User should not be authenticated
    assert '_auth_user_id' not in client.session


def test_admin_create_user_and_access(client, admin):
    """Admin creates author user, user can log in and access author features (T099)."""
    client.force_login(admin)
    # Create author via admin user management
    response = client.post(
        reverse('admin_users'),
        {
            'create_user': '1',
            'username': 'newauthor',
            'role': 'AUTHOR',
            'is_active': 'on',
            'password': 'newpass123',
        },
        follow=True,
    )
    assert response.status_code == 200
    new_user = User.objects.get(username='newauthor')
    assert new_user.role == User.Role.AUTHOR
    assert new_user.is_active is True

    # Log out admin, log in as new author
    client.logout()
    response = client.post(
        reverse('login'),
        {'username': 'newauthor', 'password': 'newpass123'},
        follow=True,
    )
    assert response.status_code == 200
    assert response.redirect_chain[-1][0].endswith('/author/dashboard/')

    # Access author dashboard
    response = client.get(reverse('author_dashboard'))
    assert response.status_code == 200
    assert 'articles' in response.context
