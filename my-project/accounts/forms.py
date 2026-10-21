"""Authentication forms."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    """Username/password login form; CSRF is enforced by middleware (FR-001)."""

    username = forms.CharField(label=_('نام کاربری'), max_length=100)
    password = forms.CharField(label=_('رمز عبور'), strip=False, widget=forms.PasswordInput)

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': _('نام کاربری یا رمز عبور نادرست است.'),
    }
