class WishlistError(Exception):
    """Base exception for wishlist-related business errors."""


class WishlistItemNotFoundError(WishlistError):
    """Raised when a requested wishlist item does not exist."""


class ProductNotFoundError(WishlistError):
    """Raised when the requested product does not exist."""


class ProductVariantNotFoundError(WishlistError):
    """Raised when the requested product variant does not exist."""


class WishlistItemAlreadyExistsError(WishlistError):
    """Raised when an item already exists in the wishlist."""