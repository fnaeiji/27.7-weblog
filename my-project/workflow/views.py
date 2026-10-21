"""Editor and Admin workflow views (US3, US4)."""

from blog.models import Article, ArticleRevision
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from workflow.forms import ReviewForm
from workflow.models import WorkflowEvent


class EditorRequiredMixin(LoginRequiredMixin):
    """Require Editor or Admin role."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role not in {'EDITOR', 'ADMIN'}:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class EditorQueueView(EditorRequiredMixin, ListView):
    """List IN_EDITORIAL_REVIEW articles ordered by update time (FR-011)."""

    template_name = 'workflow/editor/queue.html'
    context_object_name = 'articles'
    paginate_by = 20

    def get_queryset(self):
        return (
            Article.objects.by_status(Article.Status.IN_EDITORIAL_REVIEW)
            .select_related('author')
            .prefetch_related('revisions')
            .order_by('-updated_at')
        )


class EditorReviewView(EditorRequiredMixin, View):
    """Review article: request changes / approve / edit (FR-012, FR-013, FR-014)."""

    template_name = 'workflow/editor/review.html'

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if article.status != Article.Status.IN_EDITORIAL_REVIEW:
            messages.error(request, 'این مقاله در وضعیت بررسی ویراستار نیست.')
            return redirect('editor_queue')
        revision = article.get_current_revision()
        form = ReviewForm(initial={'action': 'request_changes'})
        return render(
            request,
            self.template_name,
            {
                'article': article,
                'revision': revision,
                'form': form,
                'content_html': revision.get_sanitized_html(),
            },
        )

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if article.status != Article.Status.IN_EDITORIAL_REVIEW:
            messages.error(request, 'این مقاله در وضعیت بررسی ویراستار نیست.')
            return redirect('editor_queue')

        form = ReviewForm(request.POST)
        if not form.is_valid():
            revision = article.get_current_revision()
            return render(
                request,
                self.template_name,
                {
                    'article': article,
                    'revision': revision,
                    'form': form,
                    'content_html': revision.get_sanitized_html(),
                },
            )

        action = form.cleaned_data['action']
        note = form.cleaned_data.get('note', '').strip()

        if action == 'request_changes':
            article.status = Article.Status.CHANGES_REQUESTED
            article.save(update_fields=['status'])
            article.workflow_events.create(
                revision=article.get_current_revision(),
                actor=request.user,
                action=WorkflowEvent.Action.REQUEST_CHANGES,
                from_status=Article.Status.IN_EDITORIAL_REVIEW,
                to_status=Article.Status.CHANGES_REQUESTED,
                note=note,
            )
            messages.success(request, 'تغییرات درخواست شد و مقاله به نویسنده برگردانده شد.')

        elif action == 'approve':
            article.status = Article.Status.PENDING_ADMIN_APPROVAL
            article.save(update_fields=['status'])
            article.workflow_events.create(
                revision=article.get_current_revision(),
                actor=request.user,
                action=WorkflowEvent.Action.APPROVE_EDITORIAL,
                from_status=Article.Status.IN_EDITORIAL_REVIEW,
                to_status=Article.Status.PENDING_ADMIN_APPROVAL,
                note=note,
            )
            messages.success(request, 'مقاله تأیید و برای مدیر ارسال شد.')

        elif action == 'edit':
            # Create new revision and revert to DRAFT
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
            article.status = Article.Status.DRAFT
            article.save(update_fields=['current_revision', 'status'])
            article.workflow_events.create(
                revision=new_rev,
                actor=request.user,
                action=WorkflowEvent.Action.UPDATE_CONTENT,
                from_status=Article.Status.IN_EDITORIAL_REVIEW,
                to_status=Article.Status.DRAFT,
                note=note,
            )
            messages.success(request, 'مقاله ویرایش شد و به پیش‌نویس برگردانده شد.')

        return redirect('editor_queue')


class AdminRequiredMixin(LoginRequiredMixin):
    """Require Admin role."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role != 'ADMIN':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
