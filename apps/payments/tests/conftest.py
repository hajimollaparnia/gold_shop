import pytest
from django.contrib.auth import get_user_model

from apps.orders.models import Order
from decimal import Decimal

User = get_user_model()


@pytest.fixture
def order(db):
    """
    Create a valid order shared across payment tests.

    The order must have a positive total amount because
    Payment.amount requires a value greater than zero.
    """

    user = User.objects.create_user(
        phone_number="09123456789",
    )

    return Order.objects.create(
        user=user,
        customer_name="Test User",
        customer_phone="09123456789",
        shipping_address="Test Address",
        subtotal="15000000",
        total_amount=Decimal("15000000"),
    )