from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """
        Метод ready() вызывается Django один раз при полной инициализации.
        Здесь безопасно запускать планировщик — все модели уже загружены.
        """
        import os
        # Защита от двойного запуска в режиме разработки (Django reloader
        # запускает процесс дважды — основной + watchdog)
        if os.environ.get("RUN_MAIN") != "true":
            return

        from .schedular import start
        start()
