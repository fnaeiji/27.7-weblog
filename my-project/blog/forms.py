"""Article forms with validation (FR-008, FR-024)."""

from core.utils import slugify
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ArticleRevision


class ArticleForm(forms.ModelForm):
    """Create/edit article revision form."""

    class Meta:
        model = ArticleRevision
        fields = ['title', 'slug', 'excerpt', 'body_markdown', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'required': True}),
            'slug': forms.TextInput(),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'body_markdown': forms.Textarea(attrs={'rows': 15, 'required': True}),
            'tags': forms.TextInput(),
        }
        labels = {
            'title': _('عنوان'),
            'slug': _('اسلاگ (نامک)'),
            'excerpt': _('خلاصه'),
            'body_markdown': _('متن (مارک‌داون)'),
            'tags': _('برچسب‌ها (با کاما جدا شده)'),
        }
        help_texts = {
            'slug': _('اختیاری؛ در صورت خالی ماندن از عنوان تولید می‌شود.'),
        }

    def __init__(self, *args, article=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._article = article

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '').strip()
        if not slug:
            slug = slugify(self.cleaned_data['title'])
        # For edit: allow same slug for same article's revisions
        # For create: enforce global uniqueness
        article = self._article or (
            self.instance.article if self.instance and self.instance.pk else None
        )
        qs = ArticleRevision.objects.filter(slug=slug)
        if article:
            # Editing existing article: allow same slug for this article's revisions
            qs = qs.filter(article=article)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_('این اسلاگ قبلاً استفاده شده است.'))
        return slug

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('title'):
            self.add_error('title', _('عنوان الزامی است.'))
        if not cleaned_data.get('body_markdown'):
            self.add_error('body_markdown', _('متن مقاله الزامی است.'))
        return cleaned_data
