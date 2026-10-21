"""Public blog views (US1)."""

from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import ListView

from .models import Article, ArticleRevision


class HomeView(ListView):
    """Paginated list of published articles (FR-026)."""

    template_name = 'blog/public/home.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return (
            Article.objects.published()
            .select_related('author')
            .prefetch_related('revisions')
            .order_by('-published_at')
        )


class ArticleDetailView(View):
    """Slug lookup, status check, and sanitized rendering (FR-023, FR-025)."""

    template_name = 'blog/public/article_detail.html'

    def get(self, request, slug):
        revision = get_object_or_404(ArticleRevision, slug=slug)
        article = revision.article
        if article.status != Article.Status.PUBLISHED:
            raise Http404
        return render(
            request,
            self.template_name,
            {
                'article': article,
                'revision': revision,
                'content_html': revision.get_sanitized_html(),
            },
        )
