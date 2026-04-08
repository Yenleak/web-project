from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    profile_view,
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    TaskListCreateAPIView,
    TaskDetailAPIView,
    CommentListCreateAPIView,
)

urlpatterns = [
    path('register/', register_view),
    path('login/', login_view),
    path('logout/', logout_view),
    path('profile/', profile_view),

    path('categories/', CategoryListCreateAPIView.as_view()),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view()),

    path('tasks/', TaskListCreateAPIView.as_view()),
    path('tasks/<int:pk>/', TaskDetailAPIView.as_view()),

    path('comments/', CommentListCreateAPIView.as_view()),
]