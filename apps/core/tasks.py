"""
Celery tasks for the core application.
"""

from celery import shared_task


@shared_task
def test_redis_task():
    """
    Verify that Celery can execute a task through Redis.
    """
    return "Gold Shop Celery is working"