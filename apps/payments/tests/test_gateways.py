from decimal import Decimal

from apps.payments.gateways.card_to_card import CardToCardGateway


def test_card_to_card_initialize():
    """Card-to-card initialization should succeed without an external API."""

    gateway = CardToCardGateway(
        merchant_card_number="6037991234567890",
    )

    result = gateway.initialize(
        amount=Decimal("15000000"),
        payment_id=1,
    )

    assert result.success is True
    assert result.raw_response["payment_id"] == 1
    assert result.raw_response["amount"] == "15000000"
    assert (
        result.raw_response["merchant_card_number"]
        == "6037991234567890"
    )


def test_card_to_card_requires_manual_verification():
    """Card-to-card verification must remain manual."""

    gateway = CardToCardGateway(
        merchant_card_number="6037991234567890",
    )

    result = gateway.verify(payment_id=1)

    assert result.success is False
    assert result.raw_response["verification_required"] is True


def test_card_to_card_refund_requires_manual_processing():
    """Card-to-card refunds must be handled manually."""

    gateway = CardToCardGateway(
        merchant_card_number="6037991234567890",
    )

    result = gateway.refund(
        payment_id=1,
        amount=Decimal("5000000"),
    )

    assert result.success is False
    assert result.raw_response["manual_processing_required"] is True