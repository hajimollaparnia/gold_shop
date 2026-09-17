from decimal import Decimal
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.coupons.exceptions import (
    CouponNotFoundError,
    ExpiredCouponError,
    InactiveCouponError,
    CouponUsageLimitError,
    UserCouponUsageLimitError,
    MinimumOrderAmountError,
)
from apps.coupons.models import Coupon
from apps.coupons.services import CouponService


@pytest.mark.django_db
def test_percentage_coupon_discount(percentage_coupon, user):
    coupon = CouponService.validate_coupon(
        user=user,
        code="GOLD20",
        order_amount=Decimal("2000000"),
    )

    discount = CouponService.calculate_discount(
        coupon=coupon,
        order_amount=Decimal("2000000"),
    )

    assert discount == Decimal("400000")


@pytest.mark.django_db
def test_fixed_coupon_discount(fixed_coupon, user):
    coupon = CouponService.validate_coupon(
        user=user,
        code="GOLD500",
        order_amount=Decimal("2000000"),
    )

    discount = CouponService.calculate_discount(
        coupon=coupon,
        order_amount=Decimal("2000000"),
    )

    assert discount == Decimal("500000")


@pytest.mark.django_db
def test_fixed_discount_cannot_exceed_order_amount(fixed_coupon, user):
    fixed_coupon.discount_value = Decimal("5000000")
    fixed_coupon.save()

    coupon = CouponService.validate_coupon(
        user=user,
        code="GOLD500",
        order_amount=Decimal("1000000"),
    )

    discount = CouponService.calculate_discount(
        coupon=coupon,
        order_amount=Decimal("1000000"),
    )

    assert discount == Decimal("1000000")


@pytest.mark.django_db
def test_unknown_coupon_raises_error(user):
    with pytest.raises(CouponNotFoundError):
        CouponService.validate_coupon(
            user=user,
            code="UNKNOWN",
            order_amount=Decimal("2000000"),
        )


@pytest.mark.django_db
def test_inactive_coupon_raises_error(percentage_coupon, user):
    percentage_coupon.is_active = False
    percentage_coupon.save()

    with pytest.raises(InactiveCouponError):
        CouponService.validate_coupon(
            user=user,
            code=percentage_coupon.code,
            order_amount=Decimal("2000000"),
        )


@pytest.mark.django_db
def test_expired_coupon_raises_error(percentage_coupon, user):
    percentage_coupon.expires_at = timezone.now() - timedelta(minutes=1)
    percentage_coupon.save()

    with pytest.raises(ExpiredCouponError):
        CouponService.validate_coupon(
            user=user,
            code=percentage_coupon.code,
            order_amount=Decimal("2000000"),
        )


@pytest.mark.django_db
def test_minimum_order_amount_is_enforced(percentage_coupon, user):
    with pytest.raises(MinimumOrderAmountError):
        CouponService.validate_coupon(
            user=user,
            code=percentage_coupon.code,
            order_amount=Decimal("500000"),
        )


@pytest.mark.django_db
def test_global_usage_limit_is_enforced(percentage_coupon, user):
    percentage_coupon.usage_limit = 1
    percentage_coupon.usage_count = 1
    percentage_coupon.save()

    with pytest.raises(CouponUsageLimitError):
        CouponService.validate_coupon(
            user=user,
            code=percentage_coupon.code,
            order_amount=Decimal("2000000"),
        )


@pytest.mark.django_db
def test_per_user_usage_limit_is_enforced(
    percentage_coupon,
    user,
    order,
):
    percentage_coupon.per_user_limit = 1
    percentage_coupon.save()

    CouponService.apply_coupon(
        user=user,
        code=percentage_coupon.code,
        order=order,
        order_amount=Decimal("2000000"),
    )

    with pytest.raises(UserCouponUsageLimitError):
        CouponService.validate_coupon(
            user=user,
            code=percentage_coupon.code,
            order_amount=Decimal("2000000"),
        )


@pytest.mark.django_db
def test_apply_coupon_records_usage(
    percentage_coupon,
    user,
    order,
):
    coupon, discount = CouponService.apply_coupon(
        user=user,
        code=percentage_coupon.code,
        order=order,
        order_amount=Decimal("2000000"),
    )

    assert coupon == percentage_coupon
    assert discount == Decimal("400000")
    assert coupon.usage_count == 1