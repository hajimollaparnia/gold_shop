import pytest

from apps.payments.exceptions import (
    InvalidPaymentState,
    PaymentAlreadyCompleted,
)
from apps.payments.gateways.card_to_card import CardToCardGateway
from apps.payments.models import Payment, PaymentStatus
from apps.payments.services import PaymentService


@pytest.fixture
def payment_service():
    """Return a payment service configured for card-to-card payments."""

    return PaymentService(
        gateway=CardToCardGateway(
            merchant_card_number="6037991234567890",
        ),
    )


@pytest.mark.django_db
def test_order_cannot_have_multiple_pending_payments(
    order,
    payment_service,
):
    """
    Ensure an order cannot have multiple active pending payments.

    This prevents duplicate payment attempts from being created
    concurrently for the same unpaid order.
    """

    first_payment = payment_service.initialize_payment(order)

    with pytest.raises(InvalidPaymentState):
        payment_service.initialize_payment(order)

    assert Payment.objects.filter(
        order=order,
        status=PaymentStatus.PENDING,
    ).count() == 1

    assert Payment.objects.filter(
        pk=first_payment.pk,
    ).exists()


@pytest.mark.django_db
def test_successful_payment_cannot_be_processed_again(
    order,
    payment_service,
):
    """
    Ensure a successful payment cannot be processed twice.
    """

    payment = payment_service.initialize_payment(order)

    from django.core.files.uploadedfile import SimpleUploadedFile

    receipt = SimpleUploadedFile(
        "receipt.jpg",
        (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01"
            b"\x00\x01\x00\x01\x00\x00\xff\xd9"
        ),
        content_type="image/jpeg",
    )

    payment_service.upload_receipt(
        payment_id=payment.pk,
        receipt_image=receipt,
    )

    payment_service.approve_payment(
        payment_id=payment.pk,
    )

    with pytest.raises(PaymentAlreadyCompleted):
        payment_service.approve_payment(
            payment_id=payment.pk,
        )


@pytest.mark.django_db
def test_failed_payment_can_create_new_payment_attempt(
    order,
    payment_service,
):
    """
    Ensure a failed payment does not permanently block
    a new payment attempt for the same order.
    """

    payment = payment_service.initialize_payment(order)

    payment_service.reject_payment(
        payment_id=payment.pk,
        reason="Invalid payment receipt.",
    )

    payment.refresh_from_db()

    assert payment.status == PaymentStatus.FAILED

    new_payment = payment_service.initialize_payment(order)

    assert new_payment.pk != payment.pk
    assert new_payment.status == PaymentStatus.PENDING

    assert Payment.objects.filter(
        order=order,
        status=PaymentStatus.FAILED,
    ).count() == 1

    assert Payment.objects.filter(
        order=order,
        status=PaymentStatus.PENDING,
    ).count() == 1