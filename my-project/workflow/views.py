"""Editor and Admin workflow views (US3, US4)."""

from accounts.models import User
from blog.models import Article, ArticleRevision
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from workflow.forms import AdminActionForm, ReviewForm, UserManagementForm
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


class AdminDashboardView(AdminRequiredMixin, View):
    """Admin dashboard with stats, pending/published articles, and users (FR-015)."""

    template_name = 'workflow/admin/dashboard.html'

    def get(self, request):
        pending = Article.objects.by_status(Article.Status.PENDING_ADMIN_APPROVAL).select_related(
            'author'
        )
        published = Article.objects.by_status(Article.Status.PUBLISHED).select_related('author')

        users = User.objects.filter(is_active=True).order_by('username')

        context = {
            'pending_count': pending.count(),
            'published_count': published.count(),
            'active_users': users.count(),
            'pending_articles': pending[:10],
            'published_articles': published[:10],
            'users': users[:20],
        }
        return render(request, self.template_name, context)


class AdminPendingView(AdminRequiredMixin, View):
    """Pending approval list with publish/reject actions (FR-015, FR-016, FR-017)."""

    template_name = 'workflow/admin/pending_list.html'

    def get(self, request):
        articles = (
            Article.objects.by_status(Article.Status.PENDING_ADMIN_APPROVAL)
            .select_related('author')
            .prefetch_related('revisions', 'workflow_events')
            .order_by('-updated_at')
        )
        return render(request, self.template_name, {'articles': articles})

    def post(self, request):
        form = AdminActionForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'فرم نامعتبر است.')
            return redirect('admin_pending')

        article = get_object_or_404(Article, pk=form.cleaned_data['article_id'])
        action = form.cleaned_data['action']
        note = form.cleaned_data.get('note', '').strip()

        if action == 'publish':
            revision_id = form.cleaned_data.get('revision_id')
            if article.current_revision != revision_id:
                messages.error(request, 'نسخه مقاله با نسخه تأییدشده مطابقت ندارد. انتشار رد شد.')
                return redirect('admin_pending')
            article.status = Article.Status.PUBLISHED
            article.published_at = article.updated_at
            article.save(update_fields=['status', 'published_at'])
            article.workflow_events.create(
                revision=article.get_current_revision(),
                actor=request.user,
                action=WorkflowEvent.Action.PUBLISH,
                from_status=Article.Status.PENDING_ADMIN_APPROVAL,
                to_status=Article.Status.PUBLISHED,
                note=note,
            )
            messages.success(request, 'مقاله با موفقیت منتشر شد.')

        elif action == 'reject':
            article.status = Article.Status.CHANGES_REQUESTED
            article.save(update_fields=['status'])
            article.workflow_events.create(
                revision=article.get_current_revision(),
                actor=request.user,
                action=WorkflowEvent.Action.REJECT_EDITORIAL,
                from_status=Article.Status.PENDING_ADMIN_APPROVAL,
                to_status=Article.Status.CHANGES_REQUESTED,
                note=note,
            )
            messages.success(request, 'مقاله رد و به نویسنده برگردانده شد.')

        return redirect('admin_pending')


class AdminPublishedView(AdminRequiredMixin, View):
    """Published articles list with unpublish action (FR-018)."""

    template_name = 'workflow/admin/published_list.html'

    def get(self, request):
        articles = (
            Article.objects.by_status(Article.Status.PUBLISHED)
            .select_related('author')
            .prefetch_related('revisions')
            .order_by('-published_at')
        )
        return render(request, self.template_name, {'articles': articles})

    def post(self, request):
        form = AdminActionForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'فرم نامعتبر است.')
            return redirect('admin_published')

        article = get_object_or_404(Article, pk=form.cleaned_data['article_id'])
        note = form.cleaned_data.get('note', '').strip()

        if form.cleaned_data['action'] == 'unpublish':
            article.status = Article.Status.DRAFT
            article.published_at = None
            article.save(update_fields=['status', 'published_at'])
            article.workflow_events.create(
                revision=article.get_current_revision(),
                actor=request.user,
                action=WorkflowEvent.Action.UNPUBLISH,
                from_status=Article.Status.PUBLISHED,
                to_status=Article.Status.DRAFT,
                note=note,
            )
            messages.success(request, 'مقاله لغو انتشار یافت و به پیش‌نویس برگردانده شد.')

        return redirect('admin_published')


class AdminUserManagementView(AdminRequiredMixin, View):
    """User management: list, create, edit, deactivate (FR-004, FR-005, SC-011)."""

    template_name = 'workflow/admin/user_management.html'

    def get(self, request):
        users = User.objects.all().order_by('-is_active', 'username')
        form = UserManagementForm()
        return render(request, self.template_name, {'users': users, 'form': form})

    def post(self, request):
        if 'create_user' in request.POST:
            form = UserManagementForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(request.POST.get('password', 'defaultpass123'))
                user.save()
                user.workflow_events.create(
                    actor=request.user,
                    action=WorkflowEvent.Action.ASSIGN_ROLE,
                    note=f'Created with role {user.get_role_display()}',
                )
                messages.success(request, f'کاربر {user.username} ایجاد شد.')
            else:
                messages.error(request, 'خطا در ایجاد کاربر.')
            return redirect('admin_users')

        if 'edit_user' in request.POST:
            user = get_object_or_404(User, pk=request.POST.get('user_id'))
            form = UserManagementForm(request.POST, instance=user, current_user=request.user)
            if form.is_valid():
                form.save()
                user.workflow_events.create(
                    actor=request.user,
                    action=WorkflowEvent.Action.ASSIGN_ROLE,
                    note=f'Updated role to {user.get_role_display()}, active={user.is_active}',
                )
                messages.success(request, f'کاربر {user.username} به‌روزرسانی شد.')
            else:
                messages.error(request, 'خطا در به‌روزرسانی کاربر.')
            return redirect('admin_users')

        if 'deactivate_user' in request.POST:
            user = get_object_or_404(User, pk=request.POST.get('user_id'))
            if user == request.user:
                messages.error(request, 'نمی‌توانید خودتان را غیرفعال کنید.')
            else:
                form = UserManagementForm(
                    {'username': user.username, 'role': user.role, 'is_active': False},
                    instance=user,
                    current_user=request.user,
                )
                if form.is_valid():
                    form.save()
                    user.workflow_events.create(
                        actor=request.user,
                        action=WorkflowEvent.Action.DEACTIVATE_USER,
                        note=f'Deactivated by {request.user.username}',
                    )
                    messages.success(request, f'کاربر {user.username} غیرفعال شد.')
                else:
                    messages.error(request, 'نمی‌توان آخرین مدیر فعال را غیرفعال کرد.')
            return redirect('admin_users')

        return redirect('admin_users')
