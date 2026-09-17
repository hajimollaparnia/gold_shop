import pytest

from apps.notifications.models import Notification


@pytest.mark.django_db
def test_notification_can_be_created(user):
    notification = Notification.objects.create(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="System Notification",
        message="Welcome to Gold Shop.",
    )

    assert notification.user == user
    assert notification.title == "System Notification"
    assert notification.is_read is False
    assert notification.read_at is None
    assert notification.data == {}


@pytest.mark.django_db
def test_notification_default_data_is_empty(user):
    notification = Notification.objects.create(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Test",
        message="Test message",
    )

    assert notification.data == {}


@pytest.mark.django_db
def test_notification_can_store_structured_data(user):
    notification = Notification.objects.create(
        user=user,
        notification_type=Notification.NotificationType.ORDER_CREATED,
        title="Order Created",
        message="Your order has been created.",
        data={
            "order_id": 123,
            "status": "pending",
        },
    )

    assert notification.data["order_id"] == 123
    assert notification.data["status"] == "pending"