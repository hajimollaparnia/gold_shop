from decimal import Decimal

import pytest

from apps.payments.models import (
    Payment,
    PaymentGateway,
    PaymentLog,
    PaymentLogEvent,
    PaymentStatus,
    Refund,
    RefundStatus,
)


@pytest.mark.django_db
def test_payment_creation(order):
    """
    Ensure a payment can be created successfully.
    """

    payment = Payment.objects.create(
        order=order,
        amount=Decimal("15000000"),
        currency="IRR",
        gateway=PaymentGateway.CARD_TO_CARD,
    )

    assert payment.pk is not None
    assert payment.status == PaymentStatus.PENDING
    assert payment.gateway == PaymentGateway.CARD_TO_CARD
    assert payment.amount == Decimal("15000000")


@pytest.mark.django_db
def test_payment_log_creation(order):
    """
    Ensure payment events are stored in the audit log.
    """

    payment = Payment.objects.create(
        order=order,
        amount=Decimal("15000000"),
    )

    log = PaymentLog.objects.create(
        payment=payment,
        event=PaymentLogEvent.CREATED,
        message="Payment created.",
    )

    assert log.pk is not None
    assert log.payment == payment
    assert log.event == PaymentLogEvent.CREATED


@pytest.mark.django_db
def test_refund_creation(order):
    """
    Ensure a refund can be created for a successful payment.
    """

    payment = Payment.objects.create(
        order=order,
        amount=Decimal("15000000"),
        status=PaymentStatus.SUCCESS,
    )

    refund = Refund.objects.create(
        payment=payment,
        amount=Decimal("5000000"),
    )

    assert refund.pk is not None
    assert refund.payment == payment
    assert refund.status == RefundStatus.PENDING