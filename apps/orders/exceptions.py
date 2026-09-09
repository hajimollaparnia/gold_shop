class OrderError(Exception):
    """
    Base exception for order-related business errors.
    """


class OrderCreationError(OrderError):
    """
    Raised when an order cannot be created.
    """


class InvalidOrderItemError(OrderCreationError):
    """
    Raised when an order item contains invalid data.
    """


class InsufficientStockError(OrderCreationError):
    """
    Raised when the requested quantity is not available.
    """