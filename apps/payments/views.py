from django.shortcuts import get_object_or_404

from drf_spectacular.utils import OpenApiResponse, extend_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order

from .gateways.card_to_card import CardToCardGateway
from .models import Payment
from .serializers import PaymentSerializer, ReceiptUploadSerializer
from .services import PaymentService


class PaymentInitializeAPIView(APIView):
    """Initialize a card-to-card payment for an order."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Payments"],
        summary="Initialize payment",
        description=(
            "Create a new card-to-card payment for an authenticated "
            "user's order."
        ),
        request=None,
        responses={
            201: PaymentSerializer,
            400: OpenApiResponse(
                description="The order cannot be paid.",
            ),
            404: OpenApiResponse(
                description="Order not found.",
            ),
        },
    )
    def post(self, request, order_id: int):
        """Create a payment for the requested order."""

        order = get_object_or_404(
            Order,
            pk=order_id,
            user=request.user,
        )

        gateway = CardToCardGateway(
            merchant_card_number="",
        )

        payment = PaymentService(
            gateway=gateway,
        ).initialize_payment(order)

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentReceiptUploadAPIView(APIView):
    """Accept a payment receipt uploaded by the customer."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Payments"],
        summary="Upload payment receipt",
        description=(
            "Upload a receipt image for an authenticated user's "
            "pending payment."
        ),
        request=ReceiptUploadSerializer,
        responses={
            200: PaymentSerializer,
            400: OpenApiResponse(
                description="Invalid receipt or payment state.",
            ),
            404: OpenApiResponse(
                description="Payment not found.",
            ),
        },
    )
    def post(self, request, payment_id: int):
        """Upload the receipt associated with a payment."""

        serializer = ReceiptUploadSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        payment = get_object_or_404(
            Payment,
            pk=payment_id,
            order__user=request.user,
        )

        gateway = CardToCardGateway(
            merchant_card_number="",
        )

        payment = PaymentService(
            gateway=gateway,
        ).upload_receipt(
            payment_id=payment.pk,
            receipt_image=serializer.validated_data["receipt_image"],
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )