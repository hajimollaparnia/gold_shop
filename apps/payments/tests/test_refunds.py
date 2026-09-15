from decimal import Decimal

import pytest

from apps.payments.exceptions import (
    InvalidRefundState,
    RefundAmountExceeded,
)
from apps.payments.gateways.card_to_card import CardToCardGateway
from apps.payments.models import (
    Payment,
    PaymentLog,
    PaymentLogEvent,
    PaymentStatus,
    RefundStatus,
)
from apps.payments.services import RefundService


@pytest.fixture
def refund_service():
    """Return a refund service configured for card-to-card payments."""

    return RefundService(
        gateway=CardToCardGateway(
            merchant_card_number="6037991234567890",
        ),
    )


@pytest.fixture
def successful_payment(order):
    """Create a successful payment eligible for refund."""

    return Payment.objects.create(
        order=order,
        amount=Decimal("15000000"),
        currency=order.currency,
        status=PaymentStatus.SUCCESS,
    )


@pytest.mark.django_db
def test_create_refund_for_successful_payment(
    successful_payment,
    refund_service,
):
    """Ensure a refund request can be created for a successful payment."""

    refund = refund_service.create_refund(
        payment_id=successful_payment.pk,
        amount=Decimal("5000000"),
        reason="Customer refund request.",
    )

    assert refund.pk is not None
    assert refund.payment == successful_payment
    assert refund.amount == Decimal("5000000")
    assert refund.status == RefundStatus.PENDING
    assert refund.reason == "Customer refund request."

    assert PaymentLog.objects.filter(
        payment=successful_payment,
        event=PaymentLogEvent.REFUND_REQUESTED,
    ).exists()


@pytest.mark.django_db
def test_refund_requires_successful_payment(
    order,
    refund_service,
):
    """Ensure only successful payments can be refunded."""

    payment = Payment.objects.create(
        order=order,
        amount=Decimal("15000000"),
        currency=order.currency,
        status=PaymentStatus.FAILED,
    )

    with pytest.raises(InvalidRefundState):
        refund_service.create_refund(
            payment_id=payment.pk,
            amount=Decimal("5000000"),
        )


@pytest.mark.django_db
def test_refund_amount_cannot_exceed_payment_amount(
    successful_payment,
    refund_service,
):
    """Ensure a refund cannot exceed the original payment amount."""

    with pytest.raises(RefundAmountExceeded):
        refund_service.create_refund(
            payment_id=successful_payment.pk,
            amount=Decimal("15000001"),
        )


@pytest.mark.django_db
def test_multiple_refunds_cannot_exceed_payment_amount(
    successful_payment,
    refund_service,
):
    """Ensure cumulative refunds cannot exceed the payment amount."""

    refund_service.create_refund(
        payment_id=successful_payment.pk,
        amount=Decimal("10000000"),
    )

    with pytest.raises(RefundAmountExceeded):
        refund_service.create_refund(
            payment_id=successful_payment.pk,
            amount=Decimal("5000001"),
        )


@pytest.mark.django_db
def test_card_to_card_refund_requires_manual_processing(
    successful_payment,
    refund_service,
):
    """
    Ensure card-to-card refunds remain pending because they
    require manual processing.
    """

    refund = refund_service.create_refund(
        payment_id=successful_payment.pk,
        amount=Decimal("5000000"),
        reason="Manual refund request.",
    )

    processed_refund = refund_service.process_refund(
        refund_id=refund.pk,
    )

    processed_refund.refresh_from_db()

    assert processed_refund.status == RefundStatus.PENDING
    assert processed_refund.processed_at is None

    assert PaymentLog.objects.filter(
        payment=successful_payment,
        event=PaymentLogEvent.REFUND_REQUESTED,
    ).count() >= 2


@pytest.mark.django_db
def test_refund_cannot_be_processed_twice(
    successful_payment,
    refund_service,
):
    """
    Ensure a refund that is no longer pending cannot be processed again.
    """

    refund = refund_service.create_refund(
        payment_id=successful_payment.pk,
        amount=Decimal("5000000"),
    )

    refund.status = RefundStatus.SUCCESS
    refund.save(
        update_fields=["status", "updated_at"],
    )

    with pytest.raises(InvalidRefundState):
        refund_service.process_refund(
            refund_id=refund.pk,
        )


@pytest.mark.django_db
def test_refund_processing_keeps_audit_log(
    successful_payment,
    refund_service,
):
    """Ensure refund processing creates an auditable payment log."""

    refund = refund_service.create_refund(
        payment_id=successful_payment.pk,
        amount=Decimal("3000000"),
    )

    refund_service.process_refund(
        refund_id=refund.pk,
    )

    logs = PaymentLog.objects.filter(
        payment=successful_payment,
        event=PaymentLogEvent.REFUND_REQUESTED,
    )

    assert logs.count() >= 2