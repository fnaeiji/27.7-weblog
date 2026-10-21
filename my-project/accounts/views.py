"""Authentication views: login and logout with role-based redirect (FR-001)."""

from django.contrib.auth import views as auth_views

from .forms import LoginForm


def get_role_redirect_url(user) -> str:
    """Return the landing URL for the user's role (spec US5, scenario 3)."""
    if user.role == user.Role.ADMIN:
        return '/manager/dashboard/'
    if user.role == user.Role.EDITOR:
        return '/editor/queue/'
    return '/author/dashboard/'


class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm

    def get_success_url(self) -> str:
        return get_role_redirect_url(self.request.user)


class LogoutView(auth_views.LogoutView):
    next_page = '/login/'
