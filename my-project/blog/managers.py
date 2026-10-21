"""Custom article manager and querysets (FR-011, FR-015)."""

from django.db import models


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status='PUBLISHED')

    def by_author(self, user):
        return self.filter(author=user)

    def by_status(self, status):
        return self.filter(status=status)


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def by_author(self, user):
        return self.get_queryset().by_author(user)

    def by_status(self, status):
        return self.get_queryset().by_status(status)
