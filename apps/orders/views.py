from django.http import Http404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .exceptions import InvalidOrderItemError
from .models import Order
from .selectors import OrderSelector
from .serializers import (
    CreateOrderSerializer,
    OrderSerializer,
)
from .services import OrderService


class OrderListView(generics.ListAPIView):
    """
    Return the authenticated user's orders.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderSelector.get_user_orders(
            self.request.user,
        )


class OrderCreateView(generics.CreateAPIView):
    """
    Create a new order for the authenticated user.

    The serializer validates the request data and the service
    handles the actual order business logic.
    """

    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Validate input and create the order through OrderService.
        """

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            order = OrderService.create_order(
                user=request.user,
                customer_name=validated_data["customer_name"],
                customer_phone=validated_data["customer_phone"],
                shipping_address=validated_data["shipping_address"],
                items=[
                    {
                        "product": item["product"],
                        "variant": item.get("variant"),
                        "price_snapshot_id": item[
                            "price_snapshot"
                        ].pk,
                        "quantity": item["quantity"],
                    }
                    for item in validated_data["items"]
                ],
                shipping_cost=validated_data.get(
                    "shipping_cost",
                    0,
                ),
                discount=validated_data.get(
                    "discount",
                    0,
                ),
                tax=validated_data.get(
                    "tax",
                    0,
                ),
            )

        except InvalidOrderItemError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = OrderSerializer(
            order,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(generics.RetrieveAPIView):
    """
    Return a single order belonging to the authenticated user.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return OrderSelector.get_order_for_user(
                user=self.request.user,
                order_id=self.kwargs["pk"],
            )
        except Order.DoesNotExist:
            raise Http404("Order not found.")

class OrderCancelView(generics.GenericAPIView):
    """
    Cancel an authenticated user's order.

    The actual cancellation logic is handled by OrderService.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Cancel the requested order and release its inventory reservation.
        """

        try:
            order = OrderSelector.get_order_for_user(
                user=request.user,
                order_id=kwargs["pk"],
            )
        except Order.DoesNotExist:
            raise Http404("Order not found.")

        try:
            order = OrderService.cancel_order(
                order=order,
            )
        except InvalidOrderItemError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK,
        )