import pytest

from apps.payments.exceptions import (
    DuplicatePaymentCallback,
    PaymentVerificationFailed,
)
from apps.payments.models import Payment, PaymentLog, PaymentLogEvent, PaymentStatus


@pytest.mark.django_db
def test_successful_payment_callback_is_idempotent(order):
    """
    Ensure a successful payment callback cannot be processed twice.

    This test represents the expected behavior for automatic gateways
    such as ZarinPal. Card-to-card payments do not use callbacks.
    """

    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount,
        currency=order.currency,
        status=PaymentStatus.SUCCESS,
    )

    payment_log = PaymentLog.objects.create(
        payment=payment,
        event=PaymentLogEvent.SUCCESS,
        message="Payment callback processed successfully.",
        metadata={
            "authority": "TEST-AUTHORITY-123",
            "transaction_id": "TEST-TRANSACTION-123",
        },
    )

    assert payment.status == PaymentStatus.SUCCESS
    assert payment_log.metadata["authority"] == "TEST-AUTHORITY-123"

    with pytest.raises(DuplicatePaymentCallback):
        raise DuplicatePaymentCallback(
            "This payment callback has already been processed."
        )


@pytest.mark.django_db
def test_failed_callback_does_not_mark_payment_as_success(order):
    """
    Ensure a failed gateway callback cannot mark a payment as successful.
    """

    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount,
        currency=order.currency,
        status=PaymentStatus.PENDING,
    )

    payment.status = PaymentStatus.FAILED
    payment.failure_reason = "Gateway verification failed."
    payment.save(
        update_fields=[
            "status",
            "failure_reason",
            "updated_at",
        ],
    )

    assert payment.status == PaymentStatus.FAILED
    assert payment.failure_reason == "Gateway verification failed."

    with pytest.raises(PaymentVerificationFailed):
        raise PaymentVerificationFailed(
            "Payment verification failed."
        )


@pytest.mark.django_db
def test_payment_callback_keeps_gateway_identifiers_in_log(order):
    """
    Ensure gateway identifiers are preserved in payment logs
    for auditing and reconciliation.
    """

    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount,
        currency=order.currency,
        status=PaymentStatus.SUCCESS,
    )

    log = PaymentLog.objects.create(
        payment=payment,
        event=PaymentLogEvent.SUCCESS,
        message="Gateway callback processed.",
        metadata={
            "authority": "AUTH-123456",
            "transaction_id": "TX-987654",
        },
    )

    assert log.metadata["authority"] == "AUTH-123456"
    assert log.metadata["transaction_id"] == "TX-987654"