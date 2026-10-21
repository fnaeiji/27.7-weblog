"""Admin view tests for User Story 4."""

import pytest
from accounts.models import User
from blog.models import Article, ArticleRevision
from django.urls import reverse

from workflow.models import WorkflowEvent

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


def _make_article(author, *, status, slug, body='# Body'):
    article = Article.objects.create(author=author, status=status)
    ArticleRevision.objects.create(
        article=article,
        revision_number=1,
        title='Test Article',
        slug=slug,
        body_markdown=body,
        created_by=author,
    )
    article.current_revision = 1
    if status == Article.Status.PUBLISHED:
        article.published_at = article.created_at
    article.save(update_fields=['current_revision', 'published_at'])
    return article


def test_admin_dashboard_auth(client, admin, editor):
    client.force_login(admin)
    assert client.get(reverse('admin_dashboard')).status_code == 200

    client.force_login(editor)
    assert client.get(reverse('admin_dashboard')).status_code == 403


def test_publish_revision_match(client, admin, author, editor):
    """Publish succeeds only when current revision matches reviewed revision (SC-004)."""
    article = _make_article(author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='pending-pub')
    article.status = Article.Status.PENDING_ADMIN_APPROVAL
    article.save(update_fields=['status'])
    # Editor approves, binding to revision 1
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=editor,
        action=WorkflowEvent.Action.APPROVE_EDITORIAL,
        from_status=Article.Status.IN_EDITORIAL_REVIEW,
        to_status=Article.Status.PENDING_ADMIN_APPROVAL,
    )

    client.force_login(admin)
    response = client.post(
        reverse('admin_pending'),
        {'action': 'publish', 'article_id': article.pk, 'revision_id': 1},
        follow=True,
    )
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.status == Article.Status.PUBLISHED
    assert article.published_at is not None


def test_publish_stale_revision_rejected(client, admin, author, editor):
    """Publish rejected when content edited after editorial review (SC-004)."""
    article = _make_article(author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='stale-pub')
    article.status = Article.Status.PENDING_ADMIN_APPROVAL
    article.save(update_fields=['status'])
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=editor,
        action=WorkflowEvent.Action.APPROVE_EDITORIAL,
        from_status=Article.Status.IN_EDITORIAL_REVIEW,
        to_status=Article.Status.PENDING_ADMIN_APPROVAL,
    )

    # Author edits, creating revision 2
    _ = ArticleRevision.objects.create(
        article=article,
        revision_number=2,
        title='Edited',
        slug='stale-pub',
        body_markdown='# Edited',
        created_by=author,
    )
    article.current_revision = 2
    article.save(update_fields=['current_revision'])

    client.force_login(admin)
    response = client.post(
        reverse('admin_pending'),
        {'action': 'publish', 'article_id': article.pk, 'revision_id': 1},
        follow=True,
    )
    article.refresh_from_db()
    assert article.status == Article.Status.PENDING_ADMIN_APPROVAL  # Still pending
    assert 'revision' in response.content.decode().lower() or 'نسخه' in response.content.decode()


def test_admin_reject(client, admin, author, editor):
    """Admin reject with note → CHANGES_REQUESTED, workflow event logged (FR-017)."""
    article = _make_article(
        author, status=Article.Status.PENDING_ADMIN_APPROVAL, slug='reject-test'
    )
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=editor,
        action=WorkflowEvent.Action.APPROVE_EDITORIAL,
        from_status=Article.Status.IN_EDITORIAL_REVIEW,
        to_status=Article.Status.PENDING_ADMIN_APPROVAL,
    )

    client.force_login(admin)
    response = client.post(
        reverse('admin_pending'),
        {'action': 'reject', 'article_id': article.pk, 'note': 'Needs more research.'},
        follow=True,
    )
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.status == Article.Status.CHANGES_REQUESTED
    event = article.workflow_events.latest('created_at')
    assert event.action == WorkflowEvent.Action.REJECT_EDITORIAL
    assert event.note == 'Needs more research.'


def test_unpublish(client, admin, author):
    """Admin unpublish → DRAFT, published_at cleared, removed from public (SC-005)."""
    article = _make_article(author, status=Article.Status.PUBLISHED, slug='unpublish-test')

    client.force_login(admin)
    response = client.post(
        reverse('admin_published'),
        {'action': 'unpublish', 'article_id': article.pk, 'note': 'Typo in content.'},
        follow=True,
    )
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.status == Article.Status.DRAFT
    assert article.published_at is None
    event = article.workflow_events.latest('created_at')
    assert event.action == WorkflowEvent.Action.UNPUBLISH
    assert event.note == 'Typo in content.'

    # Verify public 404
    response = client.get(reverse('article_detail', kwargs={'slug': 'unpublish-test'}))
    assert response.status_code == 404


def test_last_admin_protection(client, admin):
    """Last active admin cannot be deactivated/demoted (SC-011)."""
    client.force_login(admin)
    response = client.post(
        reverse('admin_users'),
        {'deactivate_user': '1', 'user_id': admin.pk},
        follow=True,
    )
    admin.refresh_from_db()
    assert admin.is_active is True  # Still active
    assert response.status_code == 200
