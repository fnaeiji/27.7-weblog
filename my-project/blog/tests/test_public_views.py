"""Public blog view tests for User Story 1 (anonymous visitor)."""

import pytest
from accounts.models import User
from django.urls import reverse
from django.utils import timezone

from blog.models import Article, ArticleRevision

pytestmark = pytest.mark.django_db


@pytest.fixture
def author(db):
    return User.objects.create_user(username='author1', password='pass123', role=User.Role.AUTHOR)


def _make_article(author, *, status, slug, body='# Title\n\nBody text.'):
    """Create an article with a single revision in the given status."""
    article = Article.objects.create(author=author, status=status)
    ArticleRevision.objects.create(
        article=article,
        revision_number=1,
        title='Test Article',
        slug=slug,
        excerpt='An excerpt',
        body_markdown=body,
        created_by=author,
    )
    article.current_revision = 1
    if status == Article.Status.PUBLISHED:
        article.published_at = timezone.now()
    article.save(update_fields=['current_revision', 'published_at'])
    return article


def test_homepage(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'blog/public/home.html' in [t.name for t in response.templates]


def test_article_detail_access(client, author):
    published = _make_article(author, status=Article.Status.PUBLISHED, slug='published-post')
    response = client.get(reverse('article_detail', kwargs={'slug': 'published-post'}))
    assert response.status_code == 200
    assert response.context['article'].pk == published.pk

    _make_article(author, status=Article.Status.DRAFT, slug='draft-post')
    assert client.get(reverse('article_detail', kwargs={'slug': 'draft-post'})).status_code == 404

    _make_article(author, status=Article.Status.IN_EDITORIAL_REVIEW, slug='review-post')
    assert client.get(reverse('article_detail', kwargs={'slug': 'review-post'})).status_code == 404


def test_markdown_sanitization(client, author):
    _make_article(
        author,
        status=Article.Status.PUBLISHED,
        slug='safe-post',
        body='Hello\n\n<script>alert(1)</script>',
    )
    response = client.get(reverse('article_detail', kwargs={'slug': 'safe-post'}))
    assert response.status_code == 200
    content = response.content.decode()
    assert '<script>alert(1)</script>' not in content
    assert 'alert(1)' in content  # text preserved, script neutralized


def test_draft_not_exposed(client, author):
    _make_article(author, status=Article.Status.DRAFT, slug='secret-draft')
    response = client.get(reverse('article_detail', kwargs={'slug': 'secret-draft'}))
    assert response.status_code == 404
