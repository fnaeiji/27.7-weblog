"""Workflow URL configuration (US3, US4)."""

from django.urls import path

from . import views

urlpatterns = [
    path('editor/queue/', views.EditorQueueView.as_view(), name='editor_queue'),
    path('editor/article/<int:pk>/review/', views.EditorReviewView.as_view(), name='editor_review'),
]
