"""Workflow URL configuration (US3, US4, US6)."""

from django.urls import path

from . import views

urlpatterns = [
    path('editor/queue/', views.EditorQueueView.as_view(), name='editor_queue'),
    path('editor/article/<int:pk>/review/', views.EditorReviewView.as_view(), name='editor_review'),
    path(
        'editor/article/<int:pk>/history/',
        views.EditorArticleRevisionHistoryView.as_view(),
        name='editor_article_history',
    ),
    path(
        'editor/article/<int:pk>/workflow-history/',
        views.EditorArticleWorkflowHistoryView.as_view(),
        name='editor_article_workflow_history',
    ),
    path('manager/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('manager/pending/', views.AdminPendingView.as_view(), name='admin_pending'),
    path('manager/published/', views.AdminPublishedView.as_view(), name='admin_published'),
    path('manager/users/', views.AdminUserManagementView.as_view(), name='admin_users'),
    path(
        'manager/article/<int:pk>/history/',
        views.AdminArticleRevisionHistoryView.as_view(),
        name='admin_article_history',
    ),
    path(
        'manager/article/<int:pk>/workflow-history/',
        views.AdminArticleWorkflowHistoryView.as_view(),
        name='admin_article_workflow_history',
    ),
]
