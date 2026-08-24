from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """
    Application configuration for the product catalog.

    Defines the default primary key type and the Python import path
    used by Django to register and initialize the catalog application.
    """

    # Use BigAutoField as the default primary key for new catalog models.
    default_auto_field = "django.db.models.BigAutoField"

    # Python import path of the catalog application.
    name = "apps.catalog"
