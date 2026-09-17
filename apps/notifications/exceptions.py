class NotificationError(Exception):
    """Base exception for notification-related business errors."""


class NotificationNotFoundError(NotificationError):
    """Raised when a requested notification does not exist."""