"""Django admin registration for workflow models."""

from django.contrib import admin

from .models import WorkflowEvent


@admin.register(WorkflowEvent)
class WorkflowEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'article',
        'revision',
        'actor',
        'action',
        'from_status',
        'to_status',
        'created_at',
    )
    list_filter = ('action', 'from_status', 'to_status', 'actor')
    search_fields = ('article__revisions__title', 'actor__username', 'note')
    readonly_fields = (
        'article',
        'revision',
        'actor',
        'action',
        'from_status',
        'to_status',
        'note',
        'created_at',
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
