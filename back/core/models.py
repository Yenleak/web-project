from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


# ─────────────────────────────────────────────
# Менеджер для кастомной модели пользователя yeanleak
# ─────────────────────────────────────────────
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)  # хэширует пароль
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# ─────────────────────────────────────────────
# Модель 1: Кастомный пользователь
# Авторизация по email вместо username
# ─────────────────────────────────────────────
class CustomUser(AbstractBaseUser, PermissionsMixin):
    name  = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    objects = CustomUserManager()

    # Используем email как логин
    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


# ─────────────────────────────────────────────
# Модель 2: Рабочее пространство (Workspace) sanzhar
# ─────────────────────────────────────────────
class Workspace(models.Model):
    name     = models.CharField(max_length=255)
    creator  = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_workspaces"   # user.created_workspaces.all()
    )
    members  = models.ManyToManyField(
        CustomUser,
        related_name="workspaces",          # user.workspaces.all()
        blank=True
    )
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
# Модель 3: Задача (Task)
# ─────────────────────────────────────────────
class Task(models.Model):
    PRIORITY_CHOICES = [
        ("low",    "Низкий"),
        ("medium", "Средний"),
        ("high",   "Высокий"),
    ]

    title        = models.CharField(max_length=255)
    description  = models.CharField(max_length=200, blank=True)  # max 200 символов
    deadline     = models.DateField(null=True, blank=True)
    priority     = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)   # заполняется автоматически

    owner     = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="tasks"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматически фиксируем время завершения задачи
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
        super().save(*args, **kwargs)
 

# ─────────────────────────────────────────────
# Модель 4: Подзадача (Subtask)
# ─────────────────────────────────────────────
class Subtask(models.Model):
    title        = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    task         = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="subtasks"             # task.subtasks.all()
    )

    def __str__(self):
        return f"[{'✓' if self.is_completed else '✗'}] {self.title}"