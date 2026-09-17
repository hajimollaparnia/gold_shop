from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import NotificationNotFoundError
from .selectors import NotificationSelector
from .serializers import NotificationSerializer
from .services import NotificationService


class NotificationListAPIView(APIView):
    """Return notifications belonging to the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = NotificationSelector.get_user_notifications(
            request.user,
        )

        return Response(
            NotificationSerializer(
                notifications,
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )


class NotificationMarkAsReadAPIView(APIView):
    """Mark a user's notification as read."""

    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = NotificationService.mark_as_read(
                user=request.user,
                notification_id=notification_id,
            )

        except NotificationNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )


class NotificationMarkAllAsReadAPIView(APIView):
    """Mark all notifications belonging to the user as read."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        NotificationService.mark_all_as_read(request.user)

        return Response(
            {"detail": "All notifications have been marked as read."},
            status=status.HTTP_200_OK,
        )


class UnreadNotificationListAPIView(APIView):
    """Return unread notifications for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = NotificationSelector.get_unread_notifications(
            request.user,
        )

        return Response(
            NotificationSerializer(
                notifications,
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )