"""WorkflowEvent model (append-only audit log for status transitions)."""

from blog.models import Article, ArticleRevision
from django.conf import settings
from django.db import models


class WorkflowEvent(models.Model):
    """Append-only record of a status transition (FR-021)."""

    class Action(models.TextChoices):
        CREATE = 'CREATE', 'ایجاد'
        UPDATE_CONTENT = 'UPDATE_CONTENT', 'ویرایش محتوا'
        SUBMIT_FOR_REVIEW = 'SUBMIT_FOR_REVIEW', 'ارسال برای بررسی'
        REQUEST_CHANGES = 'REQUEST_CHANGES', 'درخواست تغییر'
        APPROVE_EDITORIAL = 'APPROVE_EDITORIAL', 'تأیید ویراستاری'
        REJECT_EDITORIAL = 'REJECT_EDITORIAL', 'رد ویراستاری'
        PUBLISH = 'PUBLISH', 'انتشار'
        UNPUBLISH = 'UNPUBLISH', 'لغو انتشار'
        ASSIGN_ROLE = 'ASSIGN_ROLE', 'انتساب نقش'
        DEACTIVATE_USER = 'DEACTIVATE_USER', 'غیرفعال‌سازی کاربر'

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='workflow_events')
    revision = models.ForeignKey(
        ArticleRevision,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_events',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='workflow_events'
    )
    action = models.CharField(max_length=40, choices=Action.choices)
    from_status = models.CharField(
        max_length=30, choices=Article.Status.choices, blank=True, default=''
    )
    to_status = models.CharField(
        max_length=30, choices=Article.Status.choices, blank=True, default=''
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article', 'created_at'], name='wfe_article_created_idx'),
            models.Index(fields=['actor'], name='wfe_actor_idx'),
        ]

    def __str__(self):
        return f'{self.action} ({self.from_status} → {self.to_status}) by {self.actor}'
