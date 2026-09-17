from django.apps import AppConfig


class CartConfig(AppConfig):
    """Application configuration for the shopping cart domain."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cart"