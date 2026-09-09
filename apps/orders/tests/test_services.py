from decimal import Decimal

import pytest

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.inventory.models import InventoryItem
from apps.orders.models import Order
from apps.orders.services import OrderService
from apps.pricing.models import PriceSnapshot


@pytest.mark.django_db
def test_create_order():
    """
    Ensure OrderService creates the order, reserves inventory,
    and calculates totals correctly.
    """

    user = User.objects.create_user(
        phone_number="09123456789",
    )

    category = Category.objects.create(
        name="Gold",
        slug="gold",
    )

    product = Product.objects.create(
        category=category,
        name="Gold Ring",
        slug="gold-ring",
        sku="GOLD-001",
        weight="2.500",
        purity=750,
    )

    # Create the inventory record required by the order service.
    inventory_item = InventoryItem.objects.create(
        product=product,
        quantity=10,
    )

    snapshot = PriceSnapshot.objects.create(
        market_price="5000000",
        weight="2.5000",
        purity=750,
        gold_value="12500000",
        making_charge="1000000",
        profit="500000",
        tax="1000000",
        other_charges="0",
        discount="0",
        subtotal="15000000",
        final_price="15000000",
    )

    order = OrderService.create_order(
        user=user,
        customer_name="Test User",
        customer_phone="09123456789",
        shipping_address="Test Address",
        items=[
            {
                "product": product,
                "variant": None,
                "price_snapshot_id": snapshot.pk,
                "quantity": 2,
            }
        ],
        shipping_cost=Decimal("500000"),
        discount=Decimal("100000"),
        tax=Decimal("1000000"),
    )

    # Subtotal = 15,000,000 × 2
    assert order.subtotal == Decimal("30000000")

    # Total = subtotal - discount + shipping + tax
    assert order.total_amount == Decimal("31400000")

    # Physical stock must remain unchanged after reservation.
    inventory_item.refresh_from_db()

    assert inventory_item.quantity == 10

    # Two units must be reserved for this order.
    assert inventory_item.reserved_quantity == 2

    # Available stock = 10 - 2
    assert inventory_item.available_quantity == 8

    assert order.items.count() == 1