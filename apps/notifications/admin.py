from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Administrative interface for system-generated notifications."""

    list_display = (
        "id",
        "user",
        "notification_type",
        "title",
        "is_read",
        "created_at",
        "read_at",
    )

    list_filter = (
        "notification_type",
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__phone_number",
        "title",
        "message",
    )

    readonly_fields = (
        "user",
        "notification_type",
        "title",
        "message",
        "data",
        "created_at",
        "read_at",
    )

    list_select_related = (
        "user",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    def has_add_permission(self, request):
        """Prevent manual creation of system notifications."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of notification history."""
        return False