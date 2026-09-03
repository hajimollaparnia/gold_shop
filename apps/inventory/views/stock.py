from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventory.serializers.stock import StockOperationSerializer
from apps.inventory.services.stock_service import StockService


class StockIncreaseView(APIView):
    """
    Increase inventory stock.

    Stock validation and business rules are delegated to StockService.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = StockOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            inventory_item = StockService.increase_stock(
                inventory_item_id=serializer.validated_data[
                    "inventory_item_id"
                ],
                quantity=serializer.validated_data["quantity"],
                reference=serializer.validated_data.get("reference", ""),
                note=serializer.validated_data.get("note", ""),
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


class StockDecreaseView(APIView):
    """
    Decrease inventory stock.

    Stock validation and business rules are delegated to StockService.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = StockOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            inventory_item = StockService.decrease_stock(
                inventory_item_id=serializer.validated_data[
                    "inventory_item_id"
                ],
                quantity=serializer.validated_data["quantity"],
                reference=serializer.validated_data.get("reference", ""),
                note=serializer.validated_data.get("note", ""),
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


class StockAdjustView(APIView):
    """
    Adjust inventory stock.

    Positive values increase stock and negative values decrease stock.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = StockOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            inventory_item = StockService.adjust_stock(
                inventory_item_id=serializer.validated_data[
                    "inventory_item_id"
                ],
                quantity=serializer.validated_data["quantity"],
                reference=serializer.validated_data.get("reference", ""),
                note=serializer.validated_data.get("note", ""),
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