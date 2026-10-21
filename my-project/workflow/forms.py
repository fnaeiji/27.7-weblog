"""Editor review form (FR-012)."""

from django import forms
from django.utils.translation import gettext_lazy as _


class ReviewForm(forms.Form):
    """Editor review action form."""

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

    # Edit fields (used when action=edit)
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
