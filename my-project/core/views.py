"""Shared view mixins for authorization and revision binding."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class AuthorRequiredMixin(LoginRequiredMixin):
    """Require an authenticated user with an editorial role (FR-003/FR-004)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role not in {'AUTHOR', 'EDITOR', 'ADMIN'}:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ArticleOwnerOrEditorMixin:
    """Authors see only their own articles; Editors/Admins see all (FR-003)."""

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if getattr(user, 'is_admin', False) or getattr(user, 'is_editor', False):
            return queryset
        return queryset.filter(author=user)


class RevisionBoundActionMixin:
    """Ensure an action applies only to the article's current revision (FR-022)."""

    @staticmethod
    def check_revision_match(article, revision_id: int) -> bool:
        return article.current_revision == revision_id
