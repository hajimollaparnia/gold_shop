from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serialize notifications for API responses."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "data",
            "created_at",
            "read_at",
        ]
        read_only_fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "data",
            "created_at",
            "read_at",
        ]