class CouponError(Exception):
    """Base exception for coupon-related business errors."""


class CouponNotFoundError(CouponError):
    """Raised when the requested coupon does not exist."""


class InvalidCouponError(CouponError):
    """Raised when a coupon cannot be applied."""


class ExpiredCouponError(CouponError):
    """Raised when a coupon has expired."""


class InactiveCouponError(CouponError):
    """Raised when a coupon is inactive."""


class CouponUsageLimitError(CouponError):
    """Raised when a coupon has reached its usage limit."""


class UserCouponUsageLimitError(CouponError):
    """Raised when a user has reached the coupon usage limit."""


class MinimumOrderAmountError(CouponError):
    """Raised when the order amount is below the coupon minimum."""


class InvalidCouponDiscountError(CouponError):
    """Raised when a coupon discount configuration is invalid."""