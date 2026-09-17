class ReviewError(Exception):
    """Base exception for review-related business errors."""


class ReviewAlreadyExistsError(ReviewError):
    """Raised when a user already reviewed a product."""


class ReviewNotFoundError(ReviewError):
    """Raised when a requested review does not exist."""


class ProductNotFoundError(ReviewError):
    """Raised when the requested product does not exist."""


class ProductVariantNotFoundError(ReviewError):
    """Raised when the requested variant does not belong to the product."""