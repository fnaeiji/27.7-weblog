"""Django admin registration for blog models."""

from django.contrib import admin

from .models import Article, ArticleRevision


class ArticleRevisionInline(admin.TabularInline):
    model = ArticleRevision
    extra = 0
    readonly_fields = ('revision_number', 'title', 'slug', 'excerpt', 'created_by', 'created_at')
    fields = ('revision_number', 'title', 'slug', 'excerpt', 'created_by', 'created_at')
    can_delete = False
    ordering = ('-revision_number',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_title',
        'author',
        'status',
        'current_revision',
        'published_at',
        'updated_at',
    )
    list_filter = ('status', 'author')
    search_fields = ('revisions__title', 'revisions__slug', 'author__username')
    readonly_fields = ('current_revision', 'published_at', 'created_at', 'updated_at')
    inlines = [ArticleRevisionInline]
    ordering = ('-updated_at',)

    def get_title(self, obj):
        rev = obj.get_current_revision()
        return rev.title if rev else '-'

    get_title.short_description = 'Title'


@admin.register(ArticleRevision)
class ArticleRevisionAdmin(admin.ModelAdmin):
    list_display = ('article', 'revision_number', 'title', 'slug', 'created_by', 'created_at')
    list_filter = ('created_by',)
    search_fields = ('title', 'slug', 'body_markdown')
    readonly_fields = (
        'article',
        'revision_number',
        'title',
        'slug',
        'excerpt',
        'body_markdown',
        'tags',
        'created_by',
        'created_at',
    )
    ordering = ('-created_at',)
