from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path("auth/register/", views.register_view,       name="register"),   # FBV
    path("auth/login/",    TokenObtainPairView.as_view(),
         name="login"),   # SimpleJWT
    path("auth/refresh/",  TokenRefreshView.as_view(),    name="token-refresh"),
    path("auth/logout/",   views.logout_view,          name="logout"),     # FBV

    # ── Tasks (CRUD) ───────────────────────────────────────────────────────
    path("tasks/",         views.TaskListCreateView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(),     name="task-detail"),
    path("subtasks/", views.SubtaskListCreateView.as_view(), name="subtask-list"),

    # ── Tasks quick actions (FBV) ──────────────────────────────────────────
    path("tasks/<int:pk>/toggle/",    views.toggle_task_status,
         name="task-toggle"),    # FBV #3
    path("subtasks/<int:pk>/toggle/", views.toggle_subtask_status,
         name="subtask-toggle"),  # FBV #4
    path("subtasks/<int:pk>/", views.SubtaskDetailView.as_view(),
         name="subtask-detail"),

    # ── Workspaces (APIView CBV) ───────────────────────────────────────────
    path("workspaces/",                       views.WorkspaceView.as_view(),
         name="workspace-list"),   # CBV #1
    path("workspaces/<int:pk>/add-members/",
         views.WorkspaceAddMembersView.as_view(), name="workspace-add-members"),

    # ── Statistics (APIView CBV) ───────────────────────────────────────────
    path("statistics/", views.UserStatisticsView.as_view(),
         name="statistics"),  # CBV #2
]
