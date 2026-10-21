"""Author view tests for User Story 2."""

import pytest
from accounts.models import User
from django.urls import reverse

from blog.models import Article, ArticleRevision

pytestmark = pytest.mark.django_db


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author1', password='pass123', role=User.Role.AUTHOR)


@pytest.fixture
def other_author(db):
    return User.objects.create_user(username='author2', password='pass123', role=User.Role.AUTHOR)


def _make_draft(author, title='Draft', slug='draft', body='# Body'):
    article = Article.objects.create(author=author, status=Article.Status.DRAFT)
    ArticleRevision.objects.create(
        article=article,
        revision_number=1,
        title=title,
        slug=slug,
        body_markdown=body,
        created_by=author,
    )
    article.current_revision = 1
    article.save(update_fields=['current_revision'])
    return article


def test_dashboard_auth(client, author, other_author):
    _make_draft(author, slug='draft-author1')
    _make_draft(other_author, slug='draft-author2')

    client.force_login(author)
    response = client.get(reverse('author_dashboard'))
    assert response.status_code == 200
    assert response.context['articles'].count() == 1

    client.force_login(other_author)
    response = client.get(reverse('author_dashboard'))
    assert response.status_code == 200
    assert response.context['articles'].count() == 1


def test_create_draft(client, author):
    client.force_login(author)
    response = client.post(
        reverse('author_article_create'),
        {
            'title': 'New Article',
            'slug': 'new-article',
            'excerpt': 'Excerpt',
            'body_markdown': '# Content',
            'tags': 'tag1,tag2',
        },
        follow=True,
    )
    assert response.status_code == 200
    article = Article.objects.get(revisions__slug='new-article')
    assert article.status == Article.Status.DRAFT
    assert article.current_revision == 1
    assert article.author == author
    assert article.revisions.count() == 1
    assert article.revisions.first().revision_number == 1


def test_edit_creates_revision(client, author):
    article = _make_draft(author, slug='editable-draft')
    client.force_login(author)
    response = client.post(
        reverse('author_article_edit', kwargs={'pk': article.pk}),
        {
            'title': 'Updated',
            'slug': 'editable-draft',
            'excerpt': 'New excerpt',
            'body_markdown': '# Updated content',
            'tags': 'tag1',
        },
        follow=True,
    )
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.current_revision == 2
    assert article.revisions.count() == 2
    rev2 = article.revisions.get(revision_number=2)
    assert rev2.title == 'Updated'
    assert rev2.body_markdown == '# Updated content'
    rev1 = article.revisions.get(revision_number=1)
    assert rev1.title == 'Draft'
    assert rev1.body_markdown == '# Body'


def test_edit_no_change_no_revision(client, author):
    article = _make_draft(author, slug='no-change-draft')
    client.force_login(author)
    # Submit exact same data as original (no excerpt, no tags)
    response = client.post(
        reverse('author_article_edit', kwargs={'pk': article.pk}),
        {
            'title': 'Draft',
            'slug': 'no-change-draft',
            'excerpt': '',
            'body_markdown': '# Body',
            'tags': '',
        },
        follow=True,
    )
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.current_revision == 1
    assert article.revisions.count() == 1


def test_submit_for_review(client, author):
    article = _make_draft(author, slug='submit-draft')
    client.force_login(author)
    response = client.post(reverse('author_article_submit', kwargs={'pk': article.pk}), follow=True)
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.status == Article.Status.IN_EDITORIAL_REVIEW
    assert article.workflow_events.count() == 1
    event = article.workflow_events.first()
    assert event.action == 'SUBMIT_FOR_REVIEW'
    assert event.from_status == Article.Status.DRAFT
    assert event.to_status == Article.Status.IN_EDITORIAL_REVIEW


def test_author_isolation(client, author, other_author):
    article = _make_draft(other_author, slug='other-draft')
    client.force_login(author)
    assert client.get(reverse('author_article_edit', kwargs={'pk': article.pk})).status_code == 404
    assert (
        client.post(reverse('author_article_submit', kwargs={'pk': article.pk})).status_code == 404
    )


def test_duplicate_slug_rejected(client, author):
    _make_draft(author, slug='unique-slug')
    client.force_login(author)
    response = client.post(
        reverse('author_article_create'),
        {
            'title': 'Another',
            'slug': 'unique-slug',
            'excerpt': '',
            'body_markdown': '# Body',
            'tags': '',
        },
    )
    assert response.status_code == 200
    assert 'unique-slug' in response.content.decode()
    assert ArticleRevision.objects.filter(slug='unique-slug').count() == 1
