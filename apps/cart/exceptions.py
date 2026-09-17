class CartError(Exception):
    """Base exception for cart-related business errors."""


class CartItemNotFoundError(CartError):
    """Raised when a requested cart item does not exist."""


class ProductNotFoundError(CartError):
    """Raised when the requested product does not exist."""


class ProductVariantNotFoundError(CartError):
    """Raised when the requested product variant does not exist."""


class InvalidCartQuantityError(CartError):
    """Raised when a cart quantity is invalid."""