from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Application configuration for the accounts application.

    Defines the default primary key type and the Python import path
    used by Django to register and initialize the application.
    """

    # Use BigAutoField as the default primary key for new models.
    default_auto_field = "django.db.models.BigAutoField"

    # Python import path of the accounts application.
    name = "apps.accounts"