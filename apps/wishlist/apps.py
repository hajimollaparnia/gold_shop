from django.apps import AppConfig


class WishlistConfig(AppConfig):
    """Application configuration for the wishlist domain."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.wishlist"