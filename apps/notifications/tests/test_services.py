import pytest

from apps.notifications.exceptions import NotificationNotFoundError
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


@pytest.mark.django_db
def test_create_notification(user):
    notification = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Welcome",
        message="Welcome to Gold Shop.",
    )

    assert notification.user == user
    assert notification.title == "Welcome"
    assert notification.is_read is False


@pytest.mark.django_db
def test_create_notification_with_data(user):
    notification = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.ORDER_CREATED,
        title="Order Created",
        message="Your order has been created.",
        data={"order_id": 10},
    )

    assert notification.data == {"order_id": 10}


@pytest.mark.django_db
def test_mark_as_read(user):
    notification = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Test",
        message="Test message.",
    )

    result = NotificationService.mark_as_read(
        user=user,
        notification_id=notification.id,
    )

    result.refresh_from_db()

    assert result.is_read is True
    assert result.read_at is not None


@pytest.mark.django_db
def test_mark_as_read_is_idempotent(user):
    notification = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Test",
        message="Test message.",
    )

    first_result = NotificationService.mark_as_read(
        user=user,
        notification_id=notification.id,
    )

    first_read_at = first_result.read_at

    second_result = NotificationService.mark_as_read(
        user=user,
        notification_id=notification.id,
    )

    assert second_result.is_read is True
    assert second_result.read_at == first_read_at


@pytest.mark.django_db
def test_mark_nonexistent_notification_raises_error(user):
    with pytest.raises(NotificationNotFoundError):
        NotificationService.mark_as_read(
            user=user,
            notification_id=999999,
        )


@pytest.mark.django_db
def test_user_cannot_mark_another_users_notification_as_read(
    user,
    second_user,
):
    notification = NotificationService.create_notification(
        user=second_user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Private",
        message="Private notification.",
    )

    with pytest.raises(NotificationNotFoundError):
        NotificationService.mark_as_read(
            user=user,
            notification_id=notification.id,
        )


@pytest.mark.django_db
def test_mark_all_as_read(user):
    first = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="First",
        message="First notification.",
    )

    second = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Second",
        message="Second notification.",
    )

    NotificationService.mark_all_as_read(user)

    first.refresh_from_db()
    second.refresh_from_db()

    assert first.is_read is True
    assert second.is_read is True
    assert first.read_at is not None
    assert second.read_at is not None


@pytest.mark.django_db
def test_mark_all_as_read_does_not_affect_other_users(
    user,
    second_user,
):
    user_notification = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="User",
        message="User notification.",
    )

    other_notification = NotificationService.create_notification(
        user=second_user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Other",
        message="Other notification.",
    )

    NotificationService.mark_all_as_read(user)

    user_notification.refresh_from_db()
    other_notification.refresh_from_db()

    assert user_notification.is_read is True
    assert other_notification.is_read is False