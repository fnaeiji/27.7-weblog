"""Article and revision models (US1)."""

from core.models import TimeStampedModel
from core.utils import markdown_to_safe_html
from django.conf import settings
from django.db import models

from .managers import ArticleManager


class Article(TimeStampedModel):
    """A blog post with a workflow status (FR-007, FR-019, FR-025)."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'پیش‌نویس'
        IN_EDITORIAL_REVIEW = 'IN_EDITORIAL_REVIEW', 'در بررسی ویراستار'
        CHANGES_REQUESTED = 'CHANGES_REQUESTED', 'تغییر درخواست شده'
        PENDING_ADMIN_APPROVAL = 'PENDING_ADMIN_APPROVAL', 'در انتظار تأیید مدیر'
        PUBLISHED = 'PUBLISHED', 'منتشرشده'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='articles'
    )
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    current_revision = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)

    objects = ArticleManager()

    class Meta:
        indexes = [
            models.Index(fields=['status'], name='blog_article_status_idx'),
            models.Index(fields=['author'], name='blog_article_author_idx'),
        ]

    def get_current_revision(self):
        """Return the revision matching ``current_revision`` (uses prefetch cache)."""
        if self.current_revision == 0:
            return None
        for revision in self.revisions.all():
            if revision.revision_number == self.current_revision:
                return revision
        return None

    def can_be_viewed_by(self, user) -> bool:
        """Published articles are public; others only for the owner/editor/admin."""
        if self.status == self.Status.PUBLISHED:
            return True
        if user is None or not getattr(user, 'is_authenticated', False):
            return False
        if getattr(user, 'is_admin', False) or getattr(user, 'is_editor', False):
            return True
        return self.author_id == user.id

    def is_editable(self) -> bool:
        return self.status in {self.Status.DRAFT, self.Status.CHANGES_REQUESTED}

    def is_in_review(self) -> bool:
        return self.status in {self.Status.IN_EDITORIAL_REVIEW, self.Status.PENDING_ADMIN_APPROVAL}


class ArticleRevision(TimeStampedModel):
    """Immutable content snapshot of an article (FR-009, FR-020, FR-024)."""

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='revisions')
    revision_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    excerpt = models.TextField(blank=True)
    body_markdown = models.TextField()
    tags = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='revisions'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['article', 'revision_number'], name='blog_revision_unique_number'
            ),
        ]
        indexes = [
            models.Index(fields=['slug'], name='blog_revision_slug_idx'),
            models.Index(fields=['created_by'], name='blog_revision_created_by_idx'),
        ]

    def get_sanitized_html(self) -> str:
        """Render the Markdown body to sanitized HTML (FR-023)."""
        return markdown_to_safe_html(self.body_markdown)

    def get_tags_list(self) -> list[str]:
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def has_content_changes(self, other: 'ArticleRevision') -> bool:
        """True when any content field differs (FR-009)."""
        return (
            self.title != other.title
            or self.slug != other.slug
            or self.excerpt != other.excerpt
            or self.body_markdown != other.body_markdown
            or self.tags != other.tags
        )
