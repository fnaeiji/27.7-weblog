"""Revision and workflow history tests for User Story 6."""

import pytest
from accounts.models import User
from django.urls import reverse
from workflow.models import WorkflowEvent

from blog.models import Article, ArticleRevision

pytestmark = pytest.mark.django_db


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author1', password='pass123', role=User.Role.AUTHOR)


@pytest.fixture
def editor(db):
    return User.objects.create_user(username='editor1', password='pass123', role=User.Role.EDITOR)


@pytest.fixture
def admin(db):
    return User.objects.create_user(username='admin1', password='pass123', role=User.Role.ADMIN)


@pytest.fixture
def other_author(db):
    return User.objects.create_user(username='author2', password='pass123', role=User.Role.AUTHOR)


def _make_article_with_revisions(author, status=Article.Status.DRAFT):
    """Create article with multiple revisions."""
    article = Article.objects.create(author=author, status=status)
    rev1 = ArticleRevision.objects.create(
        article=article,
        revision_number=1,
        title='Original Title',
        slug='original-title',
        body_markdown='# Original\n\nContent 1',
        tags='tag1',
        created_by=author,
    )
    rev2 = ArticleRevision.objects.create(
        article=article,
        revision_number=2,
        title='Updated Title',
        slug='updated-title',
        body_markdown='# Updated\n\nContent 2',
        tags='tag1, tag2',
        created_by=author,
    )
    article.current_revision = 2
    article.save(update_fields=['current_revision'])
    return article, [rev1, rev2]


def test_revision_history_author_access(client, author):
    """Author can view revision history of own article (T106)."""
    article, _ = _make_article_with_revisions(author)
    client.force_login(author)
    response = client.get(reverse('author_article_history', kwargs={'pk': article.pk}))
    assert response.status_code == 200
    assert 'revisions' in response.context
    assert response.context['revisions'].count() == 2


def test_revision_history_editor_access(client, editor, author):
    """Editor can view revision history (T106)."""
    article, _ = _make_article_with_revisions(author)
    client.force_login(editor)
    response = client.get(reverse('editor_article_history', kwargs={'pk': article.pk}))
    assert response.status_code == 200
    assert 'revisions' in response.context


def test_revision_history_admin_access(client, admin, author):
    """Admin can view revision history (T106)."""
    article, _ = _make_article_with_revisions(author)
    client.force_login(admin)
    response = client.get(reverse('admin_article_history', kwargs={'pk': article.pk}))
    assert response.status_code == 200
    assert 'revisions' in response.context


def test_revision_history_unauthorized_access(client, author, other_author):
    """Other author cannot view revision history (T108)."""
    article, _ = _make_article_with_revisions(author)
    client.force_login(other_author)
    response = client.get(reverse('author_article_history', kwargs={'pk': article.pk}))
    assert response.status_code == 404


def test_revision_history_content(client, author):
    """Revision history shows revision number, editor, date, preview (T106)."""
    article, revisions = _make_article_with_revisions(author)
    client.force_login(author)
    response = client.get(reverse('author_article_history', kwargs={'pk': article.pk}))
    assert response.status_code == 200
    content = response.content.decode()
    assert 'Original Title' in content
    assert 'Updated Title' in content
    assert revisions[0].created_by.username in content
    assert revisions[1].created_by.username in content


def test_workflow_history_author_access(client, author, editor, admin):
    """Author can view workflow history (T107)."""
    article, _ = _make_article_with_revisions(author, status=Article.Status.IN_EDITORIAL_REVIEW)
    # Add workflow events
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=author,
        action=WorkflowEvent.Action.SUBMIT_FOR_REVIEW,
        from_status=Article.Status.DRAFT,
        to_status=Article.Status.IN_EDITORIAL_REVIEW,
    )
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=editor,
        action=WorkflowEvent.Action.APPROVE_EDITORIAL,
        from_status=Article.Status.IN_EDITORIAL_REVIEW,
        to_status=Article.Status.PENDING_ADMIN_APPROVAL,
    )
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=admin,
        action=WorkflowEvent.Action.PUBLISH,
        from_status=Article.Status.PENDING_ADMIN_APPROVAL,
        to_status=Article.Status.PUBLISHED,
    )

    client.force_login(author)
    response = client.get(reverse('author_article_workflow_history', kwargs={'pk': article.pk}))
    assert response.status_code == 200
    assert 'events' in response.context
    assert response.context['events'].count() == 3


def test_workflow_history_editor_access(client, editor, author, admin):
    """Editor can view workflow history (T107)."""
    article, _ = _make_article_with_revisions(author)
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=author,
        action=WorkflowEvent.Action.SUBMIT_FOR_REVIEW,
        from_status=Article.Status.DRAFT,
        to_status=Article.Status.IN_EDITORIAL_REVIEW,
    )
    client.force_login(editor)
    response = client.get(reverse('editor_article_workflow_history', kwargs={'pk': article.pk}))
    assert response.status_code == 200


def test_workflow_history_admin_access(client, admin, author):
    """Admin can view workflow history (T107)."""
    article, _ = _make_article_with_revisions(author)
    client.force_login(admin)
    response = client.get(reverse('admin_article_workflow_history', kwargs={'pk': article.pk}))
    assert response.status_code == 200


def test_workflow_history_content(client, author, editor, admin):
    """Workflow history shows actor, action, from/to, note, timestamp (T107)."""
    article, _ = _make_article_with_revisions(author, status=Article.Status.IN_EDITORIAL_REVIEW)
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=author,
        action=WorkflowEvent.Action.SUBMIT_FOR_REVIEW,
        from_status=Article.Status.DRAFT,
        to_status=Article.Status.IN_EDITORIAL_REVIEW,
        note='Please review',
    )
    article.workflow_events.create(
        revision=article.get_current_revision(),
        actor=editor,
        action=WorkflowEvent.Action.APPROVE_EDITORIAL,
        from_status=Article.Status.IN_EDITORIAL_REVIEW,
        to_status=Article.Status.PENDING_ADMIN_APPROVAL,
        note='Looks good',
    )

    client.force_login(author)
    response = client.get(reverse('author_article_workflow_history', kwargs={'pk': article.pk}))
    assert response.status_code == 200
    content = response.content.decode()
    assert 'SUBMIT_FOR_REVIEW' in content or 'ارسال برای بررسی' in content
    assert 'APPROVE_EDITORIAL' in content or 'تأیید ویراستاری' in content
    assert 'Please review' in content
    assert 'Looks good' in content


def test_workflow_history_unauthorized_access(client, author, other_author):
    """Other author cannot view workflow history (T108)."""
    article, _ = _make_article_with_revisions(author)
    client.force_login(other_author)
    response = client.get(reverse('author_article_workflow_history', kwargs={'pk': article.pk}))
    assert response.status_code == 404
