from .models import Notification


class NotificationSelector:
    """Provides optimized read-only notification queries."""

    @staticmethod
    def get_user_notifications(user):
        """Return all notifications belonging to a user."""

        return (
            Notification.objects
            .filter(user=user)
            .order_by("-created_at")
        )

    @staticmethod
    def get_unread_notifications(user):
        """Return unread notifications belonging to a user."""

        return (
            Notification.objects
            .filter(
                user=user,
                is_read=False,
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_notification_for_user(
        user,
        notification_id,
    ):
        """Return a specific notification owned by the user."""

        return (
            Notification.objects
            .filter(
                id=notification_id,
                user=user,
            )
            .first()
        )