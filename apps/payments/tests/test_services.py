import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.payments.exceptions import (
    InvalidPaymentState,
    PaymentAlreadyCompleted,
)
from apps.payments.gateways.card_to_card import CardToCardGateway
from apps.payments.models import PaymentLog, PaymentLogEvent, PaymentStatus
from apps.payments.services import PaymentService


@pytest.fixture
def payment_service():
    """
    Return a payment service configured for card-to-card payments.
    """

    return PaymentService(
        gateway=CardToCardGateway(
            merchant_card_number="6037991234567890",
        ),
    )


@pytest.mark.django_db
def test_initialize_payment(order, payment_service):
    """
    Ensure a pending payment is created for an eligible order.
    """

    payment = payment_service.initialize_payment(order)

    assert payment.pk is not None
    assert payment.order == order
    assert payment.amount == order.total_amount
    assert payment.status == PaymentStatus.PENDING

    assert PaymentLog.objects.filter(
        payment=payment,
        event=PaymentLogEvent.CREATED,
    ).exists()


@pytest.mark.django_db
def test_upload_receipt(order, payment_service):
    """
    Ensure a receipt can be uploaded to a pending payment.
    """

    payment = payment_service.initialize_payment(order)

    receipt = SimpleUploadedFile(
        "receipt.jpg",
        b"fake-image-content",
        content_type="image/jpeg",
    )

    updated_payment = payment_service.upload_receipt(
        payment_id=payment.pk,
        receipt_image=receipt,
    )

    updated_payment.refresh_from_db()

    assert updated_payment.receipt_image.name
    assert updated_payment.status == PaymentStatus.PENDING

    assert PaymentLog.objects.filter(
        payment=payment,
        event=PaymentLogEvent.RECEIPT_UPLOADED,
    ).exists()


@pytest.mark.django_db
def test_payment_can_be_approved_after_receipt_upload(
    order,
    payment_service,
):
    """
    Ensure an uploaded receipt can be manually approved.
    """

    payment = payment_service.initialize_payment(order)

    receipt = SimpleUploadedFile(
        "receipt.jpg",
        b"fake-image-content",
        content_type="image/jpeg",
    )

    payment_service.upload_receipt(
        payment_id=payment.pk,
        receipt_image=receipt,
    )

    approved_payment = payment_service.approve_payment(
        payment_id=payment.pk,
    )

    approved_payment.refresh_from_db()
    order.refresh_from_db()

    assert approved_payment.status == PaymentStatus.SUCCESS
    assert approved_payment.verified_at is not None
    assert order.payment_status == "paid"

    assert PaymentLog.objects.filter(
        payment=approved_payment,
        event=PaymentLogEvent.SUCCESS,
    ).exists()


@pytest.mark.django_db
def test_payment_cannot_be_approved_without_receipt(
    order,
    payment_service,
):
    """
    Ensure approval is blocked when no receipt exists.
    """

    payment = payment_service.initialize_payment(order)

    with pytest.raises(InvalidPaymentState):
        payment_service.approve_payment(
            payment_id=payment.pk,
        )


@pytest.mark.django_db
def test_successful_payment_cannot_be_approved_twice(
    order,
    payment_service,
):
    """
    Ensure an already successful payment cannot be approved twice.
    """

    payment = payment_service.initialize_payment(order)

    receipt = SimpleUploadedFile(
        "receipt.jpg",
        b"fake-image-content",
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
def test_payment_can_be_rejected(
    order,
    payment_service,
):
    """
    Ensure a pending payment can be manually rejected.
    """

    payment = payment_service.initialize_payment(order)

    rejected_payment = payment_service.reject_payment(
        payment_id=payment.pk,
        reason="Receipt amount does not match the order.",
    )

    rejected_payment.refresh_from_db()

    assert rejected_payment.status == PaymentStatus.FAILED
    assert (
        rejected_payment.failure_reason
        == "Receipt amount does not match the order."
    )

    assert PaymentLog.objects.filter(
        payment=rejected_payment,
        event=PaymentLogEvent.FAILED,
    ).exists()