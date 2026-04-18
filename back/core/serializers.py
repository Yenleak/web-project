# core/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Workspace, Task, Subtask

User = get_user_model()


# ─────────────────────────────────────────────
# Пользователь
# ─────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ["id", "name", "email", "password"]

    def create(self, validated_data):
        # Используем наш кастомный менеджер, чтобы пароль хэшировался
        return User.objects.create_user(**validated_data)


class UserShortSerializer(serializers.ModelSerializer):
    """Лёгкое представление пользователя для вложенных объектов."""
    class Meta:
        model  = User
        fields = ["id", "name", "email"]


# ─────────────────────────────────────────────
# Подзадача
# ─────────────────────────────────────────────
class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Subtask
        fields = ["id", "title", "is_completed", "task"]
        # task не включаем — он берётся из контекста родительской Task


# ─────────────────────────────────────────────
# Задача
# ─────────────────────────────────────────────
class TaskSerializer(serializers.ModelSerializer):
    # Вложенные подзадачи (read-only список)
    subtasks = SubtaskSerializer(many=True, read_only=True)
    # owner выводим как имя, а не PK
    owner    = UserShortSerializer(read_only=True)

    class Meta:
        model  = Task
        fields = [
            "id", "title", "description", "deadline",
            "priority", "is_completed", "completed_at",
            "owner", "workspace", "subtasks", "created_at",
        ]
        read_only_fields = ["completed_at", "created_at", "owner"]


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Отдельный сериализатор для создания/обновления задачи.
    owner выставляется во view через perform_create, а не через запрос.
    """
    class Meta:
        model  = Task
        fields = [
            "id", "title", "description", "deadline",
            "priority", "is_completed", "workspace",
        ]


# ─────────────────────────────────────────────
# Workspace
# ─────────────────────────────────────────────
class WorkspaceSerializer(serializers.ModelSerializer):
    creator = UserShortSerializer(read_only=True)
    members = UserShortSerializer(many=True, read_only=True)
    # Поле для записи: принимает список ID пользователей
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        source="members"        # маппим на поле members модели
    )

    class Meta:
        model  = Workspace
        fields = ["id", "name", "creator", "members", "member_ids", "deadline"]

    def create(self, validated_data):
        # Извлекаем members отдельно, так как M2M нельзя передать в create()
        members = validated_data.pop("members", [])
        workspace = Workspace.objects.create(**validated_data)
        workspace.members.set(members)
        return workspace


class AddMembersSerializer(serializers.Serializer):
    """Для эндпоинта добавления участников в воркспейс."""
    user_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )


# ─────────────────────────────────────────────
# Статистика
# ─────────────────────────────────────────────
class StatisticsSerializer(serializers.Serializer):
    total_tasks         = serializers.IntegerField()
    completed_on_time   = serializers.IntegerField()
    completed_overdue   = serializers.IntegerField()
    pending             = serializers.IntegerField()
    completion_rate_pct = serializers.FloatField()