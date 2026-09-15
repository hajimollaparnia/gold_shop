from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class PaymentInitializationResult:
    """
    Represents the normalized result of a payment initialization request.

    Gateway implementations return this provider-independent structure
    so that the payment service does not depend on a specific gateway.
    """

    success: bool
    redirect_url: str | None = None
    authority: str | None = None
    message: str | None = None
    raw_response: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class PaymentVerificationResult:
    """
    Represents the normalized result of a payment verification request.

    The result contains only information required by the payment
    service and remains independent of the underlying provider.
    """

    success: bool
    transaction_id: str | None = None
    message: str | None = None
    raw_response: dict[str, Any] | None = None


class PaymentGateway(ABC):
    """
    Defines the contract that every payment gateway must implement.

    Business logic must depend on this abstraction rather than on
    a concrete payment provider such as ZarinPal.
    """

    @abstractmethod
    def initialize(
        self,
        *,
        amount: Decimal,
        payment_id: int,
    ) -> PaymentInitializationResult:
        """
        Initialize a payment with the selected gateway.

        Args:
            amount: Payment amount in the order currency.
            payment_id: Internal Payment primary key.

        Returns:
            A normalized gateway-independent initialization result.
        """
        raise NotImplementedError

    @abstractmethod
    def verify(
        self,
        *,
        payment_id: int,
        authority: str | None = None,
    ) -> PaymentVerificationResult:
        """
        Verify a payment with the selected gateway.

        Args:
            payment_id: Internal Payment primary key.
            authority: Provider-specific payment authority when available.

        Returns:
            A normalized gateway-independent verification result.
        """
        raise NotImplementedError

    @abstractmethod
    def refund(
        self,
        *,
        payment_id: int,
        amount: Decimal,
    ) -> PaymentVerificationResult:
        """
        Request a refund through the selected gateway.

        Args:
            payment_id: Internal Payment primary key.
            amount: Amount to refund.

        Returns:
            A normalized gateway-independent refund result.
        """
        raise NotImplementedError