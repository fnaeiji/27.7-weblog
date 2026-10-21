"""Editor view tests for User Story 3."""

import pytest
from accounts.models import User
from blog.models import Article, ArticleRevision
from django.urls import reverse
from django.utils import timezone

from workflow.models import WorkflowEvent

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


def test_queue_auth(client, editor, admin):
    client.force_login(editor)
    assert client.get(reverse('editor_queue')).status_code == 200

    client.force_login(admin)
    assert client.get(reverse('editor_queue')).status_code == 200

    # Author should be denied
    author = User.objects.create_user(username='author2', password='pass', role=User.Role.AUTHOR)
    client.force_login(author)
    assert client.get(reverse('editor_queue')).status_code == 403


def test_queue_listing(client, editor, author):
    _make_article(author, status=Article.Status.DRAFT, slug='draft-1')
    a3 = _make_article(author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='review-2')
    a2 = _make_article(author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='review-1')
    # Force a2 to have a later updated_at
    a2.updated_at = timezone.now()
    a2.save(update_fields=['updated_at'])

    client.force_login(editor)
    response = client.get(reverse('editor_queue'))
    assert response.status_code == 200
    articles = list(response.context['articles'])
    assert len(articles) == 2
    # Ordered by -updated_at (newest first)
    assert articles[0].pk == a2.pk
    assert articles[1].pk == a3.pk


def test_request_changes(client, editor, author):
    article = _make_article(
        author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='review-changes'
    )
    client.force_login(editor)
    response = client.post(
        reverse('editor_review', kwargs={'pk': article.pk}),
        {'action': 'request_changes', 'note': 'Please expand the introduction.'},
        follow=True,
    )
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.status == Article.Status.CHANGES_REQUESTED
    event = article.workflow_events.latest('created_at')
    assert event.action == WorkflowEvent.Action.REQUEST_CHANGES
    assert event.note == 'Please expand the introduction.'
    assert event.from_status == Article.Status.IN_EDITORIAL_REVIEW
    assert event.to_status == Article.Status.CHANGES_REQUESTED


def test_approve_editorial(client, editor, author):
    article = _make_article(
        author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='review-approve'
    )
    client.force_login(editor)
    response = client.post(
        reverse('editor_review', kwargs={'pk': article.pk}),
        {'action': 'approve'},
        follow=True,
    )
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.status == Article.Status.PENDING_ADMIN_APPROVAL
    event = article.workflow_events.latest('created_at')
    assert event.action == WorkflowEvent.Action.APPROVE_EDITORIAL
    assert event.revision == article.get_current_revision()


def test_edit_during_review(client, editor, author):
    article = _make_article(author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='review-edit')
    client.force_login(editor)
    response = client.post(
        reverse('editor_review', kwargs={'pk': article.pk}),
        {
            'action': 'edit',
            'title': 'Edited',
            'slug': 'review-edit',
            'excerpt': '',
            'body_markdown': '# Edited',
            'tags': '',
        },
        follow=True,
    )
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.status == Article.Status.DRAFT
    assert article.current_revision == 2
    event = article.workflow_events.latest('created_at')
    assert event.action == WorkflowEvent.Action.UPDATE_CONTENT
    assert event.to_status == Article.Status.DRAFT


def test_editor_cannot_publish(client, editor, author):
    article = _make_article(
        author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='review-publish'
    )
    client.force_login(editor)
    # No publish action in form; direct POST should fail
    _ = client.post(
        reverse('editor_review', kwargs={'pk': article.pk}),
        {'action': 'publish'},
        follow=True,
    )
    # Should not succeed; article remains in review
    article.refresh_from_db()
    assert article.status == Article.Status.IN_EDITORIAL_REVIEW
