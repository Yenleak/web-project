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


# AUTH  (Function-Based Views #1, #2) yeanleak

@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """
    FBV #1 — Регистрация нового пользователя.
    Возвращает JWT-токены сразу после создания аккаунта.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
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
    """
    FBV #2 — Логаут: инвалидируем refresh-токен,
    добавляя его в чёрный список SimpleJWT.
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        # требует 'rest_framework_simplejwt.token_blacklist' в INSTALLED_APPS
        token.blacklist()
        return Response({"detail": "Успешный выход."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"detail": "Неверный токен."}, status=status.HTTP_400_BAD_REQUEST)


# TASKS  (Class-Based View — generics) sanzhar

class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /tasks/  — список задач текущего пользователя
    POST /tasks/  — создать задачу (owner = request.user автоматически)
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Для чтения — подробный сериализатор с вложенными объектами
        if self.request.method == "GET":
            return TaskSerializer
        return TaskCreateSerializer

    def get_queryset(self):
        # Пользователь видит только свои задачи
        queryset = Task.objects.filter(owner=self.request.user)

        # 2. Проверяем, прислал ли фронтенд ID воркспейса в ссылке (например, /tasks/?workspace=3)
        workspace_id = self.request.query_params.get('workspace')

        # 3. Если ID есть, фильтруем задачи именно по этому воркспейсу
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        else:
            queryset = Task.objects.filter(
                assigned_to=self.request.user, workspace__isnull=True)

        return queryset.select_related("assigned_to", "workspace").prefetch_related("subtasks")

    def perform_create(self, serializer):
        assigned_to = serializer.validated_data.get('assigned_to')

        # если задача никому не дана(не указано) значит это задача самого пользователя
        if not assigned_to:
            serializer.save(owner=self.request.user,
                            assigned_to=self.request.user)
        else:
            serializer.save(owner=self.request.user)


class SubtaskListCreateView(generics.ListCreateAPIView):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]


class SubtaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /tasks/<pk>/  — получить задачу
    PUT    /tasks/<pk>/  — полное обновление
    PATCH  /tasks/<pk>/  — частичное обновление
    DELETE /tasks/<pk>/  — удалить задачу
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskSerializer
        return TaskCreateSerializer

    def get_queryset(self):
        # Запрещаем редактировать чужие задачи
        return Task.objects.filter(owner=self.request.user)


# TASKS — FBV-эндпоинты для быстрых действий

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def toggle_task_status(request, pk):
    """
    FBV #3 — Быстрое переключение статуса задачи (выполнена / не выполнена).
    PATCH /tasks/<pk>/toggle/
    Не требует тела запроса — просто инвертирует is_completed.
    """
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
    """
    FBV #4 — Быстрое переключение статуса подзадачи.
    PATCH /subtasks/<pk>/toggle/
    """
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


# WORKSPACES  (APIView — CBV #1)

class WorkspaceView(APIView):
    """
    CBV #1 на основе APIView.
    GET  /workspaces/  — воркспейсы, где пользователь является участником или создателем
    POST /workspaces/  — создать новый воркспейс
    """
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
    """
    CBV — Добавление участников в воркспейс.
    POST /workspaces/<pk>/add-members/
    Тело: { "user_ids": [1, 2, 3] }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            # Добавлять участников может только создатель воркспейса
            workspace = Workspace.objects.get(pk=pk)
        except Workspace.DoesNotExist:
            return Response(
                {"detail": "Воркспейс не найден или нет прав."},
                status=status.HTTP_404_NOT_FOUND
            )

        email = request.data.get('email')

        if not email:
            return Response({"error": "Email обязателен для приглашения."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Ищем пользователя по этому email в базе
        try:
            user = User.objects.get(email=email)

            # 3. Добавляем пользователя в воркспейс
            # ВНИМАНИЕ: Замени 'members' на то название, которое используется у тебя в модели Workspace (например, users, participants и т.д.)
            workspace.members.add(user)

            return Response({"message": "Пользователь успешно добавлен!"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Если такого email нет в базе, возвращаем понятную ошибку
            return Response({"error": "Пользователь с таким email не найден."}, status=status.HTTP_404_NOT_FOUND)


# STATISTICS  (APIView — CBV #2)

class UserStatisticsView(APIView):
    """
    CBV #2 на основе APIView.
    GET /statistics/
    Возвращает статистику по задачам текущего пользователя:
    - выполнено в срок
    - выполнено с просрочкой
    - в ожидании
    - процент выполнения
    """
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

        completion_rate = round(
            (completed_on_time + completed_overdue) / total * 100, 1) if total else 0.0

        data = {
            "total_tasks":         total,
            "completed_on_time":   completed_on_time,
            "completed_overdue":   completed_overdue,
            "pending":             pending,
            "completion_rate_pct": completion_rate,
        }

        serializer = StatisticsSerializer(data)
        return Response(serializer.data)


# ── Вспомогательные функции для ORM-фильтров статистики ──────────────────────

from django.db.models import F  # noqa — импорт ниже для читаемости


def models_deadline_lte():
    """Возвращает выражение: completed_at.date <= deadline."""
    # Используется как фильтр: completed_at__date__lte=F('deadline')
    return F("deadline")


def _task_deadline_field():
    """Возвращает выражение для сравнения completed_at > deadline."""
    return F("deadline")
