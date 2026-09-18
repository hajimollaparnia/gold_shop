from celery import shared_task


@shared_task
def test_redis_task():
    """
    Verify that Celery can execute a task through Redis.
    """
    return "Gold Shop Celery is working"


@shared_task
def beat_test_task():
    """
    Test task executed automatically by Celery Beat.
    """
    print("Gold Shop Celery Beat is working")
    return "Beat task executed successfully"
