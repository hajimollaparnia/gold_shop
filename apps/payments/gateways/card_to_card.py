from decimal import Decimal
from typing import Any

from .base import (
    PaymentGateway,
    PaymentInitializationResult,
    PaymentVerificationResult,
)


class CardToCardGateway(PaymentGateway):
    """
    Implements the card-to-card payment workflow.

    Card-to-card payments do not provide automatic provider-side
    verification. Therefore, initialization only exposes the merchant
    payment information, while verification is completed manually
    after the customer uploads a payment receipt.
    """

    def __init__(self, merchant_card_number: str) -> None:
        """
        Initialize the card-to-card gateway.

        Args:
            merchant_card_number: Merchant bank card number used
                for customer transfers.
        """
        self.merchant_card_number = merchant_card_number

    def initialize(
        self,
        *,
        amount: Decimal,
        payment_id: int,
    ) -> PaymentInitializationResult:
        """
        Prepare a card-to-card payment.

        No external provider request is made because the customer
        performs the transfer directly through their banking service.
        """

        return PaymentInitializationResult(
            success=True,
            message="Card-to-card payment initialized successfully.",
            raw_response={
                "payment_id": payment_id,
                "amount": str(amount),
                "merchant_card_number": self.merchant_card_number,
            },
        )

    def verify(
        self,
        *,
        payment_id: int,
        authority: str | None = None,
    ) -> PaymentVerificationResult:
        """
        Return a manual-verification response.

        Card-to-card payments cannot be verified automatically.
        The actual verification decision is made by the payment
        service after an administrator reviews the uploaded receipt.
        """

        return PaymentVerificationResult(
            success=False,
            message="Card-to-card payments require manual verification.",
            raw_response={
                "payment_id": payment_id,
                "verification_required": True,
            },
        )

    def refund(
        self,
        *,
        payment_id: int,
        amount: Decimal,
    ) -> PaymentVerificationResult:
        """
        Indicate that card-to-card refunds require manual processing.

        No automatic bank refund API is available for this gateway.
        """

        return PaymentVerificationResult(
            success=False,
            message="Card-to-card refunds require manual processing.",
            raw_response={
                "payment_id": payment_id,
                "amount": str(amount),
                "manual_processing_required": True,
            },
        )