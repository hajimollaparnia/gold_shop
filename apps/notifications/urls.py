from django.urls import path

from .views import (
    NotificationListAPIView,
    NotificationMarkAllAsReadAPIView,
    NotificationMarkAsReadAPIView,
    UnreadNotificationListAPIView,
)


app_name = "notifications"

urlpatterns = [
    path(
        "",
        NotificationListAPIView.as_view(),
        name="list",
    ),
    path(
        "unread/",
        UnreadNotificationListAPIView.as_view(),
        name="unread",
    ),
    path(
        "<int:notification_id>/read/",
        NotificationMarkAsReadAPIView.as_view(),
        name="mark-read",
    ),
    path(
        "read-all/",
        NotificationMarkAllAsReadAPIView.as_view(),
        name="mark-all-read",
    ),
]