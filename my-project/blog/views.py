"""Blog views: public + author + history (US1 + US2 + US6)."""

from core.views import ArticleOwnerOrEditorMixin, AuthorRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from .forms import ArticleForm
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
        if article.current_revision != revision.revision_number:
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


class AuthorDashboardView(AuthorRequiredMixin, ListView):
    """List the current author's articles with status and revision count (FR-007)."""

    template_name = 'blog/author/dashboard.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return (
            Article.objects.by_author(self.request.user)
            .select_related('author')
            .prefetch_related('revisions')
            .order_by('-updated_at')
        )


class ArticleCreateView(AuthorRequiredMixin, View):
    """Create a new article draft with revision 1 (FR-007, FR-009)."""

    template_name = 'blog/author/article_form.html'

    def get(self, request):
        form = ArticleForm()
        return render(request, self.template_name, {'form': form, 'action': 'create'})

    def post(self, request):
        form = ArticleForm(request.POST, article=None)
        if form.is_valid():
            article = Article.objects.create(author=request.user, status=Article.Status.DRAFT)
            revision = form.save(commit=False)
            revision.article = article
            revision.revision_number = 1
            revision.created_by = request.user
            revision.save()
            article.current_revision = 1
            article.save(update_fields=['current_revision'])
            messages.success(request, 'پیش‌نویس با موفقیت ایجاد شد.')
            return redirect('author_dashboard')
        return render(request, self.template_name, {'form': form, 'action': 'create'})


class ArticleEditView(AuthorRequiredMixin, ArticleOwnerOrEditorMixin, View):
    """Edit an article; create new revision only when content changes (FR-009)."""

    template_name = 'blog/author/article_form.html'
    model = Article

    def get_queryset(self):
        return super().get_queryset()

    def get(self, request, pk):
        article = get_object_or_404(self.get_queryset(), pk=pk)
        if not article.is_editable():
            raise PermissionDenied
        revision = article.get_current_revision()
        form = ArticleForm(instance=revision)
        return render(
            request, self.template_name, {'form': form, 'article': article, 'action': 'edit'}
        )

    def post(self, request, pk):
        article = get_object_or_404(self.get_queryset(), pk=pk)
        if not article.is_editable():
            raise PermissionDenied
        current_rev = article.get_current_revision()
        original_values = {
            'title': current_rev.title,
            'slug': current_rev.slug,
            'excerpt': current_rev.excerpt,
            'body_markdown': current_rev.body_markdown,
            'tags': current_rev.tags,
        }
        form = ArticleForm(request.POST, instance=current_rev)
        if form.is_valid():
            submitted_rev = ArticleRevision(
                title=form.cleaned_data['title'],
                slug=form.cleaned_data['slug'],
                excerpt=form.cleaned_data['excerpt'],
                body_markdown=form.cleaned_data['body_markdown'],
                tags=form.cleaned_data['tags'],
            )
            original_rev = ArticleRevision(**original_values)
            if original_rev.has_content_changes(submitted_rev):
                new_rev = ArticleRevision(
                    article=article,
                    revision_number=article.current_revision + 1,
                    title=form.cleaned_data['title'],
                    slug=form.cleaned_data['slug'],
                    excerpt=form.cleaned_data['excerpt'],
                    body_markdown=form.cleaned_data['body_markdown'],
                    tags=form.cleaned_data['tags'],
                    created_by=request.user,
                )
                new_rev.save()
                article.current_revision = new_rev.revision_number
                article.save(update_fields=['current_revision'])
                messages.success(request, 'ویرایش ذخیره شد و نسخه جدید ایجاد گردید.')
            else:
                messages.info(request, 'تغییری در محتوا اعمال نشد.')
            return redirect('author_dashboard')
        return render(
            request, self.template_name, {'form': form, 'article': article, 'action': 'edit'}
        )


class ArticleSubmitView(AuthorRequiredMixin, ArticleOwnerOrEditorMixin, View):
    """Submit a DRAFT or CHANGES_REQUESTED article for editorial review (FR-010)."""

    model = Article

    def get_queryset(self):
        return super().get_queryset()

    def post(self, request, pk):
        article = get_object_or_404(self.get_queryset(), pk=pk)
        if article.status not in {Article.Status.DRAFT, Article.Status.CHANGES_REQUESTED}:
            messages.error(request, 'فقط پیش‌نویس یا تغییر‌طلبی قابل ارسال برای بررسی است.')
            return redirect('author_dashboard')
        article.status = Article.Status.IN_EDITORIAL_REVIEW
        article.save(update_fields=['status'])
        article.workflow_events.create(
            revision=article.get_current_revision(),
            actor=request.user,
            action='SUBMIT_FOR_REVIEW',
            from_status=Article.Status.DRAFT
            if article.status == Article.Status.IN_EDITORIAL_REVIEW
            else Article.Status.CHANGES_REQUESTED,
            to_status=Article.Status.IN_EDITORIAL_REVIEW,
        )
        messages.success(request, 'مقاله برای بررسی ویراستاری ارسال شد.')
        return redirect('author_dashboard')


class ArticleRevisionHistoryView(AuthorRequiredMixin, ArticleOwnerOrEditorMixin, View):
    """View revision history for an article (FR-020)."""

    template_name = 'blog/author/history.html'
    model = Article

    def get_queryset(self):
        return super().get_queryset()

    def get(self, request, pk):
        article = get_object_or_404(self.get_queryset(), pk=pk)
        revisions = article.revisions.order_by('-revision_number')
        return render(
            request,
            self.template_name,
            {'article': article, 'revisions': revisions},
        )


class ArticleWorkflowHistoryView(AuthorRequiredMixin, ArticleOwnerOrEditorMixin, View):
    """View workflow event history for an article (FR-021)."""

    template_name = 'blog/author/workflow_history.html'
    model = Article

    def get_queryset(self):
        return super().get_queryset()

    def get(self, request, pk):
        article = get_object_or_404(self.get_queryset(), pk=pk)
        events = article.workflow_events.select_related('actor', 'revision').order_by('created_at')
        return render(
            request,
            self.template_name,
            {'article': article, 'events': events},
        )
