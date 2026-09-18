"""
Celery application configuration for the Gold Shop project.

Celery uses Redis as the message broker and result backend.
"""

import os

from celery import Celery


# Set the default Django settings module for the 'celery' command.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("gold_shop")

# Load Celery configuration from Django settings using the CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks.py files inside installed Django apps.
app.autodiscover_tasks()