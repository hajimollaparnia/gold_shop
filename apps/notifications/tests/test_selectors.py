import pytest

from apps.notifications.models import Notification
from apps.notifications.selectors import NotificationSelector
from apps.notifications.services import NotificationService


@pytest.mark.django_db
def test_get_user_notifications(user):
    NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="First",
        message="First notification.",
    )

    NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Second",
        message="Second notification.",
    )

    notifications = NotificationSelector.get_user_notifications(user)

    assert notifications.count() == 2


@pytest.mark.django_db
def test_get_user_notifications_respects_ownership(
    user,
    second_user,
):
    NotificationService.create_notification(
        user=second_user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Other",
        message="Other notification.",
    )

    notifications = NotificationSelector.get_user_notifications(user)

    assert notifications.count() == 0


@pytest.mark.django_db
def test_get_unread_notifications(user):
    unread = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Unread",
        message="Unread notification.",
    )

    read = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Read",
        message="Read notification.",
    )

    NotificationService.mark_as_read(
        user=user,
        notification_id=read.id,
    )

    notifications = NotificationSelector.get_unread_notifications(user)

    assert notifications.count() == 1
    assert notifications.first().id == unread.id


@pytest.mark.django_db
def test_get_notification_for_user(user):
    notification = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Test",
        message="Test notification.",
    )

    result = NotificationSelector.get_notification_for_user(
        user=user,
        notification_id=notification.id,
    )

    assert result is not None
    assert result.id == notification.id


@pytest.mark.django_db
def test_get_notification_for_user_respects_ownership(
    user,
    second_user,
):
    notification = NotificationService.create_notification(
        user=second_user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Private",
        message="Private notification.",
    )

    result = NotificationSelector.get_notification_for_user(
        user=user,
        notification_id=notification.id,
    )

    assert result is None