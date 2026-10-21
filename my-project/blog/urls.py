"""Blog URL configuration (US1 + US2)."""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('posts/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('author/dashboard/', views.AuthorDashboardView.as_view(), name='author_dashboard'),
    path('author/article/new/', views.ArticleCreateView.as_view(), name='author_article_create'),
    path(
        'author/article/<int:pk>/edit/', views.ArticleEditView.as_view(), name='author_article_edit'
    ),
    path(
        'author/article/<int:pk>/submit/',
        views.ArticleSubmitView.as_view(),
        name='author_article_submit',
    ),
]
