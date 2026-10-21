"""Workflow URL configuration (US3, US4)."""

from django.urls import path

from . import views

urlpatterns = [
    path('editor/queue/', views.EditorQueueView.as_view(), name='editor_queue'),
    path('editor/article/<int:pk>/review/', views.EditorReviewView.as_view(), name='editor_review'),
    path('manager/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('manager/pending/', views.AdminPendingView.as_view(), name='admin_pending'),
    path('manager/published/', views.AdminPublishedView.as_view(), name='admin_published'),
    path('manager/users/', views.AdminUserManagementView.as_view(), name='admin_users'),
]
