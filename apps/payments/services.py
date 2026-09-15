from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, PaymentStatus as OrderPaymentStatus

from .exceptions import (
    InvalidOrderForPayment,
    InvalidPaymentState,
    InvalidRefundState,
    PaymentAlreadyCompleted,
    RefundAmountExceeded,
)
from .gateways.base import PaymentGateway
from .models import (
    Payment,
    PaymentLog,
    PaymentLogEvent,
    PaymentStatus,
    Refund,
    RefundStatus,
)


class PaymentService:
    """
    Provides business operations for payment processing.

    Payment business logic is intentionally kept outside views,
    serializers, and gateway implementations.
    """

    def __init__(self, gateway: PaymentGateway) -> None:
        """Initialize the service with a provider-independent gateway."""
        self.gateway = gateway

    @transaction.atomic
    def initialize_payment(self, order: Order) -> Payment:
        """
        Create and initialize a payment for an eligible order.

        The order is locked during validation to prevent concurrent
        payment initialization for the same order.
        """

        locked_order = (
            Order.objects.select_for_update()
            .select_related("user")
            .get(pk=order.pk)
        )

        if locked_order.status in {
            "cancelled",
            "delivered",
        }:
            raise InvalidOrderForPayment(
                "This order cannot be paid."
            )

        if locked_order.payment_status == OrderPaymentStatus.PAID:
            raise PaymentAlreadyCompleted(
                "This order has already been paid."
            )

        active_payment_exists = Payment.objects.filter(
            order=locked_order,
            status__in=[
                PaymentStatus.PENDING,
                PaymentStatus.PROCESSING,
            ],
        ).exists()

        if active_payment_exists:
            raise InvalidPaymentState(
                "This order already has an active payment."
            )

        payment = Payment.objects.create(
            order=locked_order,
            amount=locked_order.total_amount,
            currency=locked_order.currency,
        )

        PaymentLog.objects.create(
            payment=payment,
            event=PaymentLogEvent.CREATED,
            message="Payment created.",
        )

        self.gateway.initialize(
            amount=payment.amount,
            payment_id=payment.pk,
        )

        return payment

    @transaction.atomic
    def upload_receipt(
        self,
        *,
        payment_id: int,
        receipt_image,
    ) -> Payment:
        """
        Attach a customer payment receipt to a pending payment.

        Receipt submission does not mark the payment as successful.
        The payment remains pending until manually reviewed.
        """

        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .get(pk=payment_id)
        )

        if payment.status != PaymentStatus.PENDING:
            raise InvalidPaymentState(
                "A receipt can only be uploaded for a pending payment."
            )

        payment.receipt_image = receipt_image
        payment.save(
            update_fields=["receipt_image", "updated_at"],
        )

        PaymentLog.objects.create(
            payment=payment,
            event=PaymentLogEvent.RECEIPT_UPLOADED,
            message="Payment receipt uploaded.",
        )

        return payment

    @transaction.atomic
    def approve_payment(self, *, payment_id: int) -> Payment:
        """
        Manually approve a card-to-card payment.

        Payment and order state changes are committed atomically to
        prevent partially completed payment operations.
        """

        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .get(pk=payment_id)
        )

        if payment.status == PaymentStatus.SUCCESS:
            raise PaymentAlreadyCompleted(
                "This payment has already been approved."
            )

        if payment.status != PaymentStatus.PENDING:
            raise InvalidPaymentState(
                "Only pending payments can be approved."
            )

        if not payment.receipt_image:
            raise InvalidPaymentState(
                "Payment receipt is required before approval."
            )

        order = (
            Order.objects.select_for_update()
            .get(pk=payment.order_id)
        )

        if order.payment_status == OrderPaymentStatus.PAID:
            raise PaymentAlreadyCompleted(
                "The order has already been paid."
            )

        payment.status = PaymentStatus.SUCCESS
        payment.verified_at = timezone.now()
        payment.failure_reason = ""
        payment.save(
            update_fields=[
                "status",
                "verified_at",
                "failure_reason",
                "updated_at",
            ],
        )

        order.payment_status = OrderPaymentStatus.PAID
        order.save(
            update_fields=["payment_status", "updated_at"],
        )

        PaymentLog.objects.create(
            payment=payment,
            event=PaymentLogEvent.SUCCESS,
            message="Payment manually approved.",
        )

        return payment

    @transaction.atomic
    def reject_payment(
        self,
        *,
        payment_id: int,
        reason: str,
    ) -> Payment:
        """
        Manually reject a card-to-card payment.

        The rejection reason is persisted for auditability.
        """

        payment = Payment.objects.select_for_update().get(
            pk=payment_id,
        )

        if payment.status != PaymentStatus.PENDING:
            raise InvalidPaymentState(
                "Only pending payments can be rejected."
            )

        payment.status = PaymentStatus.FAILED
        payment.failure_reason = reason.strip()

        payment.save(
            update_fields=[
                "status",
                "failure_reason",
                "updated_at",
            ],
        )

        PaymentLog.objects.create(
            payment=payment,
            event=PaymentLogEvent.FAILED,
            message="Payment manually rejected.",
            metadata={"reason": reason.strip()},
        )

        return payment


class RefundService:
    """
    Provides business operations for payment refunds.

    Refund business logic is intentionally kept outside views,
    serializers, and gateway implementations.
    """

    def __init__(self, gateway: PaymentGateway) -> None:
        """Initialize the service with a provider-independent gateway."""
        self.gateway = gateway

    @transaction.atomic
    def create_refund(
        self,
        *,
        payment_id: int,
        amount: Decimal,
        reason: str = "",
    ) -> Refund:
        """
        Create a refund request for a successful payment.

        The payment is locked to prevent concurrent refund operations.
        The total amount of active and successful refunds cannot exceed
        the original payment amount.
        """

        payment = (
            Payment.objects.select_for_update()
            .get(pk=payment_id)
        )

        if payment.status != PaymentStatus.SUCCESS:
            raise InvalidRefundState(
                "Only successful payments can be refunded."
            )

        refunded_amount = sum(
            refund.amount
            for refund in payment.refunds.select_for_update().filter(
                status__in=[
                    RefundStatus.PENDING,
                    RefundStatus.PROCESSING,
                    RefundStatus.SUCCESS,
                ],
            )
        )

        if refunded_amount + amount > payment.amount:
            raise RefundAmountExceeded(
                "Refund amount exceeds the refundable payment amount."
            )

        refund = Refund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason.strip(),
        )

        PaymentLog.objects.create(
            payment=payment,
            event=PaymentLogEvent.REFUND_REQUESTED,
            message="Refund requested.",
            metadata={
                "refund_id": refund.pk,
                "amount": str(refund.amount),
                "reason": reason.strip(),
            },
        )

        return refund

    @transaction.atomic
    def process_refund(
        self,
        *,
        refund_id: int,
    ) -> Refund:
        """
        Process an existing refund through the configured gateway.

        Card-to-card gateways require manual processing, while future
        automatic gateways can complete the refund programmatically.
        """

        refund = (
            Refund.objects.select_for_update()
            .select_related("payment")
            .get(pk=refund_id)
        )

        if refund.status != RefundStatus.PENDING:
            raise InvalidRefundState(
                "Only pending refunds can be processed."
            )

        refund.status = RefundStatus.PROCESSING
        refund.save(
            update_fields=["status", "updated_at"],
        )

        PaymentLog.objects.create(
            payment=refund.payment,
            event=PaymentLogEvent.REFUND_REQUESTED,
            message="Refund processing started.",
            metadata={
                "refund_id": refund.pk,
                "amount": str(refund.amount),
            },
        )

        result = self.gateway.refund(
            payment_id=refund.payment_id,
            amount=refund.amount,
        )

        if not result.success:
            refund.status = RefundStatus.PENDING
            refund.save(
                update_fields=["status", "updated_at"],
            )

            PaymentLog.objects.create(
                payment=refund.payment,
                event=PaymentLogEvent.REFUND_REQUESTED,
                message=(
                    result.message
                    or "Manual refund processing required."
                ),
                metadata={
                    "refund_id": refund.pk,
                    "manual_processing_required": True,
                    "gateway_response": result.raw_response or {},
                },
            )

            return refund

        refund.status = RefundStatus.SUCCESS
        refund.processed_at = timezone.now()
        refund.save(
            update_fields=[
                "status",
                "processed_at",
                "updated_at",
            ],
        )

        PaymentLog.objects.create(
            payment=refund.payment,
            event=PaymentLogEvent.REFUND_COMPLETED,
            message=(
                result.message
                or "Refund completed successfully."
            ),
            metadata={
                "refund_id": refund.pk,
                "transaction_id": result.transaction_id,
                "gateway_response": result.raw_response or {},
            },
        )

        return refund