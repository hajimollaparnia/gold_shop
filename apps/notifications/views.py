from drf_spectacular.utils import OpenApiResponse, extend_schema

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

    @extend_schema(
        tags=["Notifications"],
        summary="List user notifications",
        responses={
            200: NotificationSerializer(many=True),
        },
    )
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

    @extend_schema(
        tags=["Notifications"],
        summary="Mark notification as read",
        request=None,
        responses={
            200: NotificationSerializer,
            404: OpenApiResponse(
                description="Notification not found.",
            ),
        },
    )
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

    @extend_schema(
        tags=["Notifications"],
        summary="Mark all notifications as read",
        request=None,
        responses={
            200: OpenApiResponse(
                description="All notifications have been marked as read.",
            ),
        },
    )
    def post(self, request):
        NotificationService.mark_all_as_read(request.user)

        return Response(
            {"detail": "All notifications have been marked as read."},
            status=status.HTTP_200_OK,
        )


class UnreadNotificationListAPIView(APIView):
    """Return unread notifications for the authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Notifications"],
        summary="List unread notifications",
        responses={
            200: NotificationSerializer(many=True),
        },
    )
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