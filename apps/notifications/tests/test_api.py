import pytest
from rest_framework.test import APIClient

from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


@pytest.fixture
def api_client():
    """Return a DRF API client."""

    return APIClient()


@pytest.mark.django_db
def test_get_notifications(api_client, user):
    NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Test",
        message="Test notification.",
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/v1/notifications/",
    )

    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_get_unread_notifications(api_client, user):
    NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Unread",
        message="Unread notification.",
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/v1/notifications/unread/",
    )

    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_mark_notification_as_read(api_client, user):
    notification = NotificationService.create_notification(
        user=user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Test",
        message="Test notification.",
    )

    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/v1/notifications/{notification.id}/read/",
    )

    assert response.status_code == 200
    assert response.data["is_read"] is True
    assert response.data["read_at"] is not None


@pytest.mark.django_db
def test_mark_nonexistent_notification_returns_404(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/notifications/999999/read/",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_mark_all_notifications_as_read(
    api_client,
    user,
):
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

    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/notifications/read-all/",
    )

    assert response.status_code == 200

    assert Notification.objects.filter(
        user=user,
        is_read=False,
    ).count() == 0


@pytest.mark.django_db
def test_notifications_require_authentication(api_client):
    response = api_client.get(
        "/api/v1/notifications/",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_read_another_users_notification(
    api_client,
    user,
    second_user,
):
    notification = NotificationService.create_notification(
        user=second_user,
        notification_type=Notification.NotificationType.SYSTEM,
        title="Private",
        message="Private notification.",
    )

    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/v1/notifications/{notification.id}/read/",
    )

    assert response.status_code == 404