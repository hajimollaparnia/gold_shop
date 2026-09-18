from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.catalog.models import Category, Product, ProductVariant
from apps.inventory.models import InventoryItem
from apps.orders.models import Order, OrderStatus
from apps.orders.services import OrderService
from apps.pricing.models import PriceSnapshot


@pytest.fixture
def api_client():
    """
    Return a DRF API client.
    """

    return APIClient()


@pytest.fixture
def order_api_data():
    """
    Create the common data required for API tests.
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


@pytest.mark.django_db
def test_create_order_api(
    api_client,
    order_api_data,
):
    """
    Ensure authenticated users can create an order
    through the API.
    """

    data = order_api_data

    api_client.force_authenticate(
        user=data["user"],
    )

    response = api_client.post(
        "/api/orders/create/",
        {
            "customer_name": "Test User",
            "customer_phone": "09123456789",
            "shipping_address": "Test Address",
            "shipping_cost": "500000",
            "discount": "100000",
            "tax": "1000000",
            "items": [
                {
                    "product": data["product"].pk,
                    "variant": None,
                    "price_snapshot_id": data["snapshot"].pk,
                    "quantity": 2,
                }
            ],
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["status"] == OrderStatus.PENDING
    assert response.data["customer_name"] == "Test User"

    assert Decimal(
        response.data["subtotal"]
    ) == Decimal("30000000")

    assert Decimal(
        response.data["total_amount"]
    ) == Decimal("31400000")

    assert len(response.data["items"]) == 1

    inventory = InventoryItem.objects.get(
        pk=data["inventory"].pk,
    )

    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 2
    assert inventory.available_quantity == 8

    assert Order.objects.filter(
        user=data["user"],
    ).count() == 1


@pytest.mark.django_db
def test_create_order_api_allows_guest_customer(
    api_client,
    order_api_data,
):
    """
    Ensure unauthenticated guest customers can create orders.

    Guest orders are initially created without a user account.
    """

    data = order_api_data

    response = api_client.post(
        "/api/orders/create/",
        {
            "customer_name": "Guest User",
            "customer_phone": "09111222333",
            "shipping_address": "Guest Address",
            "shipping_cost": "500000",
            "discount": "100000",
            "tax": "1000000",
            "items": [
                {
                    "product": data["product"].pk,
                    "variant": None,
                    "price_snapshot_id": data["snapshot"].pk,
                    "quantity": 2,
                }
            ],
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["status"] == OrderStatus.PENDING
    assert response.data["customer_name"] == "Guest User"

    order = Order.objects.get(
        pk=response.data["id"],
    )

    assert order.user is None
    assert order.customer_phone == "09111222333"

    inventory = InventoryItem.objects.get(
        pk=data["inventory"].pk,
    )

    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 2
    assert inventory.available_quantity == 8


@pytest.mark.django_db
def test_create_order_api_rejects_insufficient_inventory(
    api_client,
    order_api_data,
):
    """
    Ensure an order cannot reserve more stock than available.
    """

    data = order_api_data

    api_client.force_authenticate(
        user=data["user"],
    )

    response = api_client.post(
        "/api/orders/create/",
        {
            "customer_name": "Test User",
            "customer_phone": "09123456789",
            "shipping_address": "Test Address",
            "items": [
                {
                    "product": data["product"].pk,
                    "variant": None,
                    "price_snapshot_id": data["snapshot"].pk,
                    "quantity": 11,
                }
            ],
        },
        format="json",
    )

    assert response.status_code == 400
    assert "detail" in response.data

    assert Order.objects.count() == 0

    inventory = InventoryItem.objects.get(
        pk=data["inventory"].pk,
    )

    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 0


@pytest.mark.django_db
def test_create_order_api_rejects_invalid_variant(
    api_client,
    order_api_data,
):
    """
    Ensure a variant belonging to another product
    cannot be used for an order item.
    """

    data = order_api_data

    another_product = Product.objects.create(
        category=data["product"].category,
        name="Another Ring",
        slug="another-ring",
        sku="GOLD-002",
        weight="3.000",
        purity=750,
    )

    variant = ProductVariant.objects.create(
        product=another_product,
        sku="VARIANT-001",
        weight="3.000",
    )

    api_client.force_authenticate(
        user=data["user"],
    )

    response = api_client.post(
        "/api/orders/create/",
        {
            "customer_name": "Test User",
            "customer_phone": "09123456789",
            "shipping_address": "Test Address",
            "items": [
                {
                    "product": data["product"].pk,
                    "variant": variant.pk,
                    "price_snapshot_id": data["snapshot"].pk,
                    "quantity": 1,
                }
            ],
        },
        format="json",
    )

    assert response.status_code == 400

    assert "items" in response.data
    assert 0 in response.data["items"]
    assert "variant" in response.data["items"][0]


@pytest.mark.django_db
def test_cancel_order_api(
    api_client,
    order_api_data,
):
    """
    Ensure an authenticated user can cancel their order.

    Cancellation must release the reserved inventory.
    """

    data = order_api_data

    api_client.force_authenticate(
        user=data["user"],
    )

    create_response = api_client.post(
        "/api/orders/create/",
        {
            "customer_name": "Test User",
            "customer_phone": "09123456789",
            "shipping_address": "Test Address",
            "items": [
                {
                    "product": data["product"].pk,
                    "variant": None,
                    "price_snapshot_id": data["snapshot"].pk,
                    "quantity": 2,
                }
            ],
        },
        format="json",
    )

    assert create_response.status_code == 201

    order_id = create_response.data["id"]

    inventory = InventoryItem.objects.get(
        pk=data["inventory"].pk,
    )

    assert inventory.reserved_quantity == 2

    response = api_client.post(
        f"/api/orders/{order_id}/cancel/",
    )

    assert response.status_code == 200
    assert response.data["status"] == OrderStatus.CANCELLED

    inventory.refresh_from_db()

    assert inventory.quantity == 10
    assert inventory.reserved_quantity == 0
    assert inventory.available_quantity == 10


@pytest.mark.django_db
def test_cancel_order_api_cannot_cancel_delivered_order(
    api_client,
    order_api_data,
):
    """
    A delivered order cannot be cancelled.
    """

    data = order_api_data

    api_client.force_authenticate(
        user=data["user"],
    )

    create_response = api_client.post(
        "/api/orders/create/",
        {
            "customer_name": "Test User",
            "customer_phone": "09123456789",
            "shipping_address": "Test Address",
            "items": [
                {
                    "product": data["product"].pk,
                    "variant": None,
                    "price_snapshot_id": data["snapshot"].pk,
                    "quantity": 2,
                }
            ],
        },
        format="json",
    )

    assert create_response.status_code == 201

    order_id = create_response.data["id"]

    order = Order.objects.get(
        pk=order_id,
    )

    OrderService.complete_order(
        order=order,
    )

    response = api_client.post(
        f"/api/orders/{order_id}/cancel/",
    )

    assert response.status_code == 400
    assert "detail" in response.data

    order.refresh_from_db()

    assert order.status == OrderStatus.DELIVERED


@pytest.mark.django_db
def test_cancel_order_api_cannot_cancel_another_users_order(
    api_client,
    order_api_data,
):
    """
    A user must not be able to cancel another user's order.
    """

    data = order_api_data

    api_client.force_authenticate(
        user=data["user"],
    )

    create_response = api_client.post(
        "/api/orders/create/",
        {
            "customer_name": "Test User",
            "customer_phone": "09123456789",
            "shipping_address": "Test Address",
            "items": [
                {
                    "product": data["product"].pk,
                    "variant": None,
                    "price_snapshot_id": data["snapshot"].pk,
                    "quantity": 2,
                }
            ],
        },
        format="json",
    )

    assert create_response.status_code == 201

    order_id = create_response.data["id"]

    another_user = User.objects.create_user(
        phone_number="09987654321",
    )

    api_client.force_authenticate(
        user=another_user,
    )

    response = api_client.post(
        f"/api/orders/{order_id}/cancel/",
    )

    assert response.status_code == 404

    order = Order.objects.get(
        pk=order_id,
    )

    assert order.status == OrderStatus.PENDING

    inventory = InventoryItem.objects.get(
        pk=data["inventory"].pk,
    )

    assert inventory.reserved_quantity == 2