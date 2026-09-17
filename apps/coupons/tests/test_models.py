import pytest
from django.db import IntegrityError

from apps.coupons.models import Coupon, CouponUsage


@pytest.mark.django_db
def test_coupon_can_be_created(percentage_coupon):
    assert percentage_coupon.code == "GOLD20"
    assert percentage_coupon.discount_type == Coupon.DiscountType.PERCENTAGE
    assert percentage_coupon.discount_value == 20


@pytest.mark.django_db
def test_coupon_code_must_be_unique(percentage_coupon):
    with pytest.raises(IntegrityError):
        Coupon.objects.create(
            code="GOLD20",
            discount_type=Coupon.DiscountType.FIXED,
            discount_value=100_000,
            starts_at=percentage_coupon.starts_at,
            expires_at=percentage_coupon.expires_at,
        )


@pytest.mark.django_db
def test_coupon_usage_can_be_created(percentage_coupon, user, order):
    usage = CouponUsage.objects.create(
        coupon=percentage_coupon,
        user=user,
        order=order,
        discount_amount=200_000,
    )

    assert usage.coupon == percentage_coupon
    assert usage.user == user
    assert usage.order == order
    assert usage.discount_amount == 200_000