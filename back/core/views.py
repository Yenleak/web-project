# core/views.py

from django.utils import timezone
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from django.contrib.auth import get_user_model

from .models import Task, Workspace, Subtask
from .serializers import (
    RegisterSerializer, TaskSerializer, TaskCreateSerializer,
    WorkspaceSerializer, AddMembersSerializer, StatisticsSerializer, SubtaskSerializer,
)

User = get_user_model()


# ══════════════════════════════════════════════
# AUTH  (Function-Based Views #1, #2) yeanleak
# ══════════════════════════════════════════════

@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):

    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user    = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user":    serializer.data,
            "refresh": str(refresh),
            "access":  str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):

    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()           # требует 'rest_framework_simplejwt.token_blacklist' в INSTALLED_APPS
        return Response({"detail": "Успешный выход."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"detail": "Неверный токен."}, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════
# TASKS  (Class-Based View — generics) sanzhar
# ══════════════════════════════════════════════

class TaskListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Для чтения — подробный сериализатор с вложенными объектами
        if self.request.method == "GET":
            return TaskSerializer
        return TaskCreateSerializer

    def get_queryset(self):
        # Пользователь видит только свои задачи
        return Task.objects.filter(owner=self.request.user).select_related(
            "owner", "workspace"
        ).prefetch_related("subtasks")

    def perform_create(self, serializer):
        # Привязываем задачу к авторизованному пользователю
        serializer.save(owner=self.request.user)

class SubtaskListCreateView(generics.ListCreateAPIView):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskSerializer
        return TaskCreateSerializer

    def get_queryset(self):
        # Запрещаем редактировать чужие задачи
        return Task.objects.filter(owner=self.request.user)


# ══════════════════════════════════════════════
# TASKS — FBV-эндпоинты для быстрых действий
# ══════════════════════════════════════════════

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def toggle_task_status(request, pk):

    try:
        task = Task.objects.get(pk=pk, owner=request.user)
    except Task.DoesNotExist:
        return Response({"detail": "Задача не найдена."}, status=status.HTTP_404_NOT_FOUND)

    task.is_completed = not task.is_completed
    task.save()  # сигнал в model.save() выставит completed_at

    return Response({
        "id":           task.id,
        "is_completed": task.is_completed,
        "completed_at": task.completed_at,
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def toggle_subtask_status(request, pk):

    try:
        # Проверяем, что подзадача принадлежит задаче текущего пользователя
        subtask = Subtask.objects.select_related("task__owner").get(
            pk=pk, task__owner=request.user
        )
    except Subtask.DoesNotExist:
        return Response({"detail": "Подзадача не найдена."}, status=status.HTTP_404_NOT_FOUND)

    subtask.is_completed = not subtask.is_completed
    subtask.save()

    return Response({
        "id":           subtask.id,
        "is_completed": subtask.is_completed,
    })


# ══════════════════════════════════════════════
# WORKSPACES  (APIView — CBV #1)
# ══════════════════════════════════════════════

class WorkspaceView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspaces = Workspace.objects.filter(
            members=request.user
        ).union(
            Workspace.objects.filter(creator=request.user)
        )
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WorkspaceSerializer(data=request.data)
        if serializer.is_valid():
            # Создатель — текущий пользователь
            workspace = serializer.save(creator=request.user)
            # Создатель автоматически добавляется в участники
            workspace.members.add(request.user)
            return Response(
                WorkspaceSerializer(workspace).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceAddMembersView(APIView):

    permission_classes = [IsAuthenticated]
 
    def post(self, request, pk):
        try:
            # Добавлять участников может только создатель воркспейса
            workspace = Workspace.objects.get(pk=pk, creator=request.user)
        except Workspace.DoesNotExist:
            return Response(
                {"detail": "Воркспейс не найден или нет прав."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AddMembersSerializer(data=request.data)
        if serializer.is_valid():
            users = serializer.validated_data["user_ids"]
            workspace.members.add(*users)   # add() принимает *args
            return Response(
                WorkspaceSerializer(workspace).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════
# STATISTICS  (APIView — CBV #2)
# ══════════════════════════════════════════════

class UserStatisticsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_tasks = Task.objects.filter(owner=request.user)

        total = user_tasks.count()

        # Выполнено В СРОК: задача закрыта, и дедлайн либо не указан,
        # либо completed_at <= дедлайн (конец дня)
        completed_on_time = user_tasks.filter(
            is_completed=True
        ).filter(
            # completed_at <= deadline (date → datetime конвертация через __date)
            completed_at__date__lte=models_deadline_lte()
        ).count()

        # Выполнено С ПРОСРОЧКОЙ: закрыта, но позже дедлайна
        completed_overdue = user_tasks.filter(
            is_completed=True,
            deadline__isnull=False,
            completed_at__date__gt=_task_deadline_field()
        ).count()

        pending = user_tasks.filter(is_completed=False).count()

        completion_rate = round((completed_on_time + completed_overdue) / total * 100, 1) if total else 0.0

        data = {
            "total_tasks":         total,
            "completed_on_time":   completed_on_time,
            "completed_overdue":   completed_overdue,
            "pending":             pending,
            "completion_rate_pct": completion_rate,
        }

        serializer = StatisticsSerializer(data)
        return Response(serializer.data)



from django.db.models import F  # noqa — импорт ниже для читаемости

def models_deadline_lte():
    """Возвращает выражение: completed_at.date <= deadline."""
    # Используется как фильтр: completed_at__date__lte=F('deadline')
    return F("deadline")

def _task_deadline_field():
    """Возвращает выражение для сравнения completed_at > deadline."""
    return F("deadline")