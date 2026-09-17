from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.coupons.models import Coupon
from apps.orders.models import Order


@pytest.fixture
def user(db):
    """Create a user for coupon tests."""

    return User.objects.create_user(
        phone_number="09120000001",
        password="TestPassword123!",
    )


@pytest.fixture
def second_user(db):
    """Create a second user for usage-limit tests."""

    return User.objects.create_user(
        phone_number="09120000002",
        password="TestPassword123!",
    )


@pytest.fixture
def percentage_coupon(db):
    """Create a valid percentage-based coupon."""

    now = timezone.now()

    return Coupon.objects.create(
        code="GOLD20",
        discount_type=Coupon.DiscountType.PERCENTAGE,
        discount_value=20,
        minimum_order_amount=1_000_000,
        starts_at=now - timedelta(hours=1),
        expires_at=now + timedelta(days=7),
    )


@pytest.fixture
def fixed_coupon(db):
    """Create a valid fixed-value coupon."""

    now = timezone.now()

    return Coupon.objects.create(
        code="GOLD500",
        discount_type=Coupon.DiscountType.FIXED,
        discount_value=500_000,
        minimum_order_amount=1_000_000,
        starts_at=now - timedelta(hours=1),
        expires_at=now + timedelta(days=7),
    )


@pytest.fixture
def order(db, user):
    """Create a minimal pending order for coupon usage tests."""

    return Order.objects.create(
        user=user,
    )