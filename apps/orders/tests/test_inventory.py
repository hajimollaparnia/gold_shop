from decimal import Decimal

import pytest

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.inventory.models import InventoryItem, StockMovement
from apps.orders.models import OrderStatus
from apps.orders.services import OrderService
from apps.pricing.models import PriceSnapshot


@pytest.fixture
def order_data():
    """Create common catalog, user, inventory and pricing test data."""

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

    inventory = InventoryItem.objects.create(
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

    return {
        "user": user,
        "product": product,
        "inventory": inventory,
        "snapshot": snapshot,
    }


def create_order(data, quantity=2):
    """Create a test order using the common test data."""

    return OrderService.create_order(
        user=data["user"],
        customer_name="Test User",
        customer_phone="09123456789",
        shipping_address="Test Address",
        items=[
            {
                "product": data["product"],
                "variant": None,
                "price_snapshot_id": data["snapshot"].pk,
                "quantity": quantity,
            }
        ],
        shipping_cost=Decimal("500000"),
        discount=Decimal("100000"),
        tax=Decimal("1000000"),
    )


@pytest.mark.django_db
def test_cancel_order_releases_inventory(order_data):
    """
    Cancelling an order must release its reserved inventory.
    """

    order = create_order(order_data, quantity=2)

    inventory = InventoryItem.objects.get(
        pk=order_data["inventory"].pk,
    )

    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 2

    OrderService.cancel_order(order=order)

    order.refresh_from_db()
    inventory.refresh_from_db()

    assert order.status == OrderStatus.CANCELLED
    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 0
    assert inventory.available_quantity == 10


@pytest.mark.django_db
def test_complete_order_commits_inventory(order_data):
    """
    Completing an order must convert its reservation into a
    physical stock deduction.
    """

    order = create_order(order_data, quantity=2)

    inventory = InventoryItem.objects.get(
        pk=order_data["inventory"].pk,
    )

    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 2

    OrderService.complete_order(order=order)

    order.refresh_from_db()
    inventory.refresh_from_db()

    assert order.status == OrderStatus.DELIVERED
    assert inventory.quantity == 8
    assert inventory.reserved_quantity == 0
    assert inventory.available_quantity == 8

    movement = StockMovement.objects.get(
        inventory_item=inventory,
        movement_type=StockMovement.MovementType.OUT,
    )

    assert movement.quantity == 2
    assert movement.reference == f"ORDER-{order.pk}"


@pytest.mark.django_db
def test_order_cannot_exceed_available_inventory(order_data):
    """
    An order exceeding available inventory must fail.
    """

    with pytest.raises(Exception):
        create_order(order_data, quantity=11)

    inventory = InventoryItem.objects.get(
        pk=order_data["inventory"].pk,
    )

    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 0


@pytest.mark.django_db
def test_cancelled_order_cannot_be_completed(order_data):
    """
    A cancelled order must never be completed.
    """

    order = create_order(order_data, quantity=2)

    OrderService.cancel_order(order=order)

    with pytest.raises(Exception):
        OrderService.complete_order(order=order)

    order.refresh_from_db()
    inventory = InventoryItem.objects.get(
        pk=order_data["inventory"].pk,
    )

    assert order.status == OrderStatus.CANCELLED
    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 0


@pytest.mark.django_db
def test_delivered_order_cannot_be_cancelled(order_data):
    """
    A delivered order must never release inventory again.
    """

    order = create_order(order_data, quantity=2)

    OrderService.complete_order(order=order)

    with pytest.raises(Exception):
        OrderService.cancel_order(order=order)

    order.refresh_from_db()
    inventory = InventoryItem.objects.get(
        pk=order_data["inventory"].pk,
    )

    assert order.status == OrderStatus.DELIVERED
    assert inventory.quantity == 8
    assert inventory.reserved_quantity == 0