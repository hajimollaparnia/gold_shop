class PaymentError(Exception):
    """Base exception for all payment-related errors."""


class InvalidPaymentState(PaymentError):
    """Raised when a payment operation is invalid for its current state."""


class PaymentAlreadyCompleted(PaymentError):
    """Raised when attempting to process an already successful payment."""


class PaymentVerificationFailed(PaymentError):
    """Raised when payment verification fails."""


class DuplicatePaymentCallback(PaymentError):
    """Raised when an already-processed payment callback is received."""


class InvalidPaymentAmount(PaymentError):
    """Raised when the payment amount is invalid."""


class InvalidOrderForPayment(PaymentError):
    """Raised when an order cannot be paid."""


class PaymentGatewayError(PaymentError):
    """Raised when a payment gateway operation fails."""


class RefundError(PaymentError):
    """Base exception for refund-related failures."""


class InvalidRefundState(RefundError):
    """Raised when a refund operation is invalid for its current state."""


class RefundAmountExceeded(RefundError):
    """Raised when the refund amount exceeds the refundable amount."""