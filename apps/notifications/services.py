from django.utils import timezone

from .exceptions import NotificationNotFoundError
from .models import Notification


class NotificationService:
    """Provides business operations for user notifications."""

    @staticmethod
    def create_notification(
        user,
        notification_type,
        title,
        message,
        data=None,
    ):
        """Create and persist a notification for a user."""

        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {},
        )

    @staticmethod
    def mark_as_read(user, notification_id):
        """Mark a user's notification as read."""

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=user,
            )
        except Notification.DoesNotExist as exc:
            raise NotificationNotFoundError(
                "The requested notification does not exist."
            ) from exc

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()

            notification.save(
                update_fields=[
                    "is_read",
                    "read_at",
                ],
            )

        return notification

    @staticmethod
    def mark_all_as_read(user):
        """Mark all unread notifications belonging to a user as read."""

        now = timezone.now()

        Notification.objects.filter(
            user=user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=now,
        )