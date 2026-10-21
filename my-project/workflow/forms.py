"""Workflow forms: editor review and admin actions."""

from accounts.models import User
from django import forms
from django.utils.translation import gettext_lazy as _


class ReviewForm(forms.Form):
    """Editor review action form (FR-012)."""

    ACTION_CHOICES = [
        ('request_changes', _('درخواست تغییر')),
        ('approve', _('تأیید و ارسال به مدیر')),
        ('edit', _('ویرایش')),
    ]

    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.HiddenInput())
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label=_('یادداشت'),
        help_text=_('الزامی برای درخواست تغییر.'),
    )

    title = forms.CharField(required=False, label=_('عنوان'))
    slug = forms.CharField(required=False, label=_('اسلاگ'))
    excerpt = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), required=False, label=_('خلاصه')
    )
    body_markdown = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15}), required=False, label=_('متن (مارک‌داون)')
    )
    tags = forms.CharField(required=False, label=_('برچسب‌ها'))

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        if action == 'request_changes' and not cleaned_data.get('note', '').strip():
            self.add_error('note', _('یادداشت برای درخواست تغییر الزامی است.'))
        if action == 'edit':
            if not cleaned_data.get('title', '').strip():
                self.add_error('title', _('عنوان الزامی است.'))
            if not cleaned_data.get('body_markdown', '').strip():
                self.add_error('body_markdown', _('متن مقاله الزامی است.'))
        return cleaned_data


class AdminActionForm(forms.Form):
    """Admin actions on pending/published articles (FR-017, FR-018)."""

    ACTION_CHOICES = [
        ('publish', _('انتشار')),
        ('reject', _('رد')),
        ('unpublish', _('لغو انتشار')),
    ]

    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.HiddenInput())
    article_id = forms.IntegerField(widget=forms.HiddenInput())
    revision_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label=_('یادداشت'),
        help_text=_('الزامی برای رد و لغو انتشار.'),
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        if action in {'reject', 'unpublish'} and not cleaned_data.get('note', '').strip():
            self.add_error('note', _('یادداشت برای این عملیات الزامی است.'))
        return cleaned_data


class UserManagementForm(forms.ModelForm):
    """Create/edit user with role assignment (FR-004, FR-005)."""

    class Meta:
        model = User
        fields = ['username', 'role', 'is_active']
        labels = {
            'username': _('نام کاربری'),
            'role': _('نقش'),
            'is_active': _('فعال'),
        }
        help_texts = {
            'is_active': _('غیرفعال کردن کاربر به جای حذف، برای حفظ تاریخچه.'),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active')
        if (
            self.instance
            and self.instance.pk
            and not is_active
            and self.instance.role == User.Role.ADMIN
            and self.instance.is_active
        ):
            active_admins = User.objects.filter(role=User.Role.ADMIN, is_active=True).count()
            if active_admins <= 1:
                raise forms.ValidationError(_('آخرین مدیر فعال قابل غیرفعال‌سازی نیست.'))
        return is_active

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if (
            self.instance
            and self.instance.pk
            and self.instance.role == User.Role.ADMIN
            and role != User.Role.ADMIN
            and self.instance.is_active
        ):
            active_admins = User.objects.filter(role=User.Role.ADMIN, is_active=True).count()
            if active_admins <= 1:
                raise forms.ValidationError(_('آخرین مدیر فعال قابل تغییر نقش نیست.'))
        return role
