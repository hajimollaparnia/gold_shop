from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .exceptions import (
    CouponNotFoundError,
    ExpiredCouponError,
    InactiveCouponError,
    InvalidCouponError,
    CouponUsageLimitError,
    UserCouponUsageLimitError,
    MinimumOrderAmountError,
)
from .models import Coupon, CouponUsage
from .selectors import CouponSelector


class CouponService:
    """Provides transactional business operations for coupons."""

    @staticmethod
    def calculate_discount(coupon, order_amount):
        """
        Calculate the discount amount for a valid coupon.

        The discount can be either a percentage or a fixed amount.
        """

        if coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
            discount = (
                order_amount * coupon.discount_value / Decimal("100")
            )

            return min(discount, order_amount)

        if coupon.discount_type == Coupon.DiscountType.FIXED:
            return min(coupon.discount_value, order_amount)

        raise InvalidCouponError("The coupon discount type is invalid.")

    @staticmethod
    def validate_coupon(user, code, order_amount):
        """Validate a coupon against the current user and order amount."""

        coupon = CouponSelector.get_by_code(code)

        if coupon is None:
            raise CouponNotFoundError(
                "The requested coupon does not exist."
            )

        now = timezone.now()

        if not coupon.is_active:
            raise InactiveCouponError(
                "The coupon is inactive."
            )

        if now < coupon.starts_at:
            raise InvalidCouponError(
                "The coupon is not active yet."
            )

        if now >= coupon.expires_at:
            raise ExpiredCouponError(
                "The coupon has expired."
            )

        if (
            coupon.usage_limit is not None
            and coupon.usage_count >= coupon.usage_limit
        ):
            raise CouponUsageLimitError(
                "The coupon usage limit has been reached."
            )

        if order_amount < coupon.minimum_order_amount:
            raise MinimumOrderAmountError(
                "The order amount does not meet the coupon minimum."
            )

        if coupon.per_user_limit is not None:
            user_usage_count = CouponSelector.get_usage_count_for_user(
                coupon=coupon,
                user=user,
            )

            if user_usage_count >= coupon.per_user_limit:
                raise UserCouponUsageLimitError(
                    "The user coupon usage limit has been reached."
                )

        return coupon

    @staticmethod
    @transaction.atomic
    def apply_coupon(user, code, order, order_amount):
        """
        Validate and record coupon usage for an order.

        The coupon row is locked during the transaction to prevent
        concurrent requests from exceeding its global usage limit.
        """

        coupon = (
            Coupon.objects
            .select_for_update()
            .filter(code=code.upper())
            .first()
        )

        if coupon is None:
            raise CouponNotFoundError(
                "The requested coupon does not exist."
            )

        coupon = CouponService.validate_coupon(
            user=user,
            code=coupon.code,
            order_amount=order_amount,
        )

        discount_amount = CouponService.calculate_discount(
            coupon=coupon,
            order_amount=order_amount,
        )

        CouponUsage.objects.create(
            coupon=coupon,
            user=user,
            order=order,
            discount_amount=discount_amount,
        )

        coupon.usage_count += 1
        coupon.save(
            update_fields=[
                "usage_count",
                "updated_at",
            ]
        )

        return coupon, discount_amount