from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Application configuration for the notifications domain."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"