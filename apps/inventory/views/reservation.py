from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventory.serializers.reservation import (
    ReservationOperationSerializer,
)
from apps.inventory.services.reservation_service import ReservationService


class ReservationReserveView(APIView):
    """
    Reserve available inventory stock.

    Reservation business rules are delegated to ReservationService.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = ReservationOperationSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        try:
            inventory_item = ReservationService.reserve(
                inventory_item_id=serializer.validated_data[
                    "inventory_item_id"
                ],
                quantity=serializer.validated_data["quantity"],
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "inventory_item_id": inventory_item.id,
                "quantity": inventory_item.quantity,
                "reserved_quantity": inventory_item.reserved_quantity,
                "available_quantity": inventory_item.available_quantity,
            },
            status=status.HTTP_200_OK,
        )


class ReservationReleaseView(APIView):
    """
    Release previously reserved inventory.

    Reservation business rules are delegated to ReservationService.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = ReservationOperationSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        try:
            inventory_item = ReservationService.release(
                inventory_item_id=serializer.validated_data[
                    "inventory_item_id"
                ],
                quantity=serializer.validated_data["quantity"],
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "inventory_item_id": inventory_item.id,
                "quantity": inventory_item.quantity,
                "reserved_quantity": inventory_item.reserved_quantity,
                "available_quantity": inventory_item.available_quantity,
            },
            status=status.HTTP_200_OK,
        )


class ReservationCommitView(APIView):
    """
    Commit a previously reserved inventory quantity.

    Committing decreases both physical stock and reserved stock.
    Stock movement creation remains delegated to the appropriate
    order/checkout integration layer.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = ReservationOperationSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        try:
            inventory_item = ReservationService.commit(
                inventory_item_id=serializer.validated_data[
                    "inventory_item_id"
                ],
                quantity=serializer.validated_data["quantity"],
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "inventory_item_id": inventory_item.id,
                "quantity": inventory_item.quantity,
                "reserved_quantity": inventory_item.reserved_quantity,
                "available_quantity": inventory_item.available_quantity,
            },
            status=status.HTTP_200_OK,
        )