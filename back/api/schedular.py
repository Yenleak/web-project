import logging
from datetime import date, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_deadline_reminders():
    """Находит задачи с дедлайном завтра и отправляет напоминания."""
    from core.models import Task  # импорт внутри функции — безопасно

    tomorrow = date.today() + timedelta(days=1)

    tasks = Task.objects.filter(
        deadline=tomorrow,
        is_completed=False,
    ).select_related("owner")

    if not tasks.exists():
        logger.info("[Scheduler] Задач с дедлайном завтра не найдено.")
        return

    for task in tasks:
        try:
            send_mail(
                subject="⏰ Напоминание о дедлайне задачи",
                message=(
                    f"Здравствуйте, {task.owner.name}!\n\n"
                    f"Напоминаем, что дедлайн по задаче «{task.title}» истекает завтра!\n\n"
                    f"— Task Manager"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.owner.email],
                fail_silently=False,
            )
            logger.info(f"[Scheduler] Отправлено: {task.owner.email} → «{task.title}»")
        except Exception as e:
            logger.error(f"[Scheduler] Ошибка для задачи {task.id}: {e}")


def start():
    """Запуск планировщика — вызывается из CoreConfig.ready()"""
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        send_deadline_reminders,
        trigger="cron",
        hour=9,
        minute=0,
        id="send_deadline_reminders",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.add_job(
        DjangoJobExecution.objects.delete_old_job_executions,
        trigger="cron",
        day_of_week="mon",
        hour=0,
        minute=0,
        id="delete_old_job_executions",
        replace_existing=True,
        kwargs={"max_age": 604800},
    )

    try:
        logger.info("[Scheduler] Запуск планировщика...")
        scheduler.start()
    except Exception as e:
        logger.error(f"[Scheduler] Ошибка запуска: {e}")