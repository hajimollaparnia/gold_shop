import pytest
from django.contrib.auth import get_user_model

from apps.catalog.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.pricing.models import PriceSnapshot


User = get_user_model()


@pytest.mark.django_db
def test_order_can_be_created():
    """
    Ensure a valid order can be persisted successfully.
    """

    user = User.objects.create_user(
        phone_number="09123456789",
    )

    order = Order.objects.create(
        user=user,
        customer_name="Test User",
        customer_phone="09123456789",
        shipping_address="Test Address",
    )

    assert order.pk is not None
    assert order.status == "pending"
    assert order.payment_status == "pending"


@pytest.mark.django_db
def test_order_item_belongs_to_order():
    """
    Ensure an order item is correctly associated with its order.
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

    order = Order.objects.create(
        user=user,
        customer_name="Test User",
        customer_phone="09123456789",
        shipping_address="Test Address",
    )

    item = OrderItem.objects.create(
        order=order,
        product=product,
        product_name_snapshot=product.name,
        sku_snapshot=product.sku,
        weight_snapshot=product.weight,
        purity_snapshot=product.purity,
        quantity=1,
        unit_price=snapshot.final_price,
        total_price=snapshot.final_price,
        price_snapshot=snapshot,
    )

    assert item.pk is not None
    assert item.order == order
    assert order.items.count() == 1