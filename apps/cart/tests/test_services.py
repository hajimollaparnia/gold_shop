import pytest

from apps.accounts.models import User
from apps.catalog.models import Product, ProductVariant

from apps.cart.exceptions import (
    CartItemNotFoundError,
    InvalidCartQuantityError,
    ProductNotFoundError,
    ProductVariantNotFoundError,
)
from apps.cart.models import Cart, CartItem
from apps.cart.services import CartService


@pytest.mark.django_db
def test_get_or_create_cart(user):
    cart = CartService.get_or_create_cart(user)

    assert cart.user == user
    assert Cart.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_add_item(user, product):
    item = CartService.add_item(
        user=user,
        product_id=product.id,
        quantity=2,
    )

    assert item.quantity == 2
    assert item.product == product


@pytest.mark.django_db
def test_add_same_item_increases_quantity(user, product):
    CartService.add_item(
        user=user,
        product_id=product.id,
        quantity=2,
    )

    item = CartService.add_item(
        user=user,
        product_id=product.id,
        quantity=3,
    )

    assert item.quantity == 5


@pytest.mark.django_db
def test_add_variant_item(user, product, variant):
    item = CartService.add_item(
        user=user,
        product_id=product.id,
        variant_id=variant.id,
        quantity=2,
    )

    assert item.variant == variant


@pytest.mark.django_db
def test_add_invalid_variant_for_product(user, product):
    other_product = Product.objects.create(
        category=product.category,
        name="Gold Necklace",
        sku="NECKLACE-001",
        weight=10,
        purity=750,
    )

    variant = ProductVariant.objects.create(
        product=other_product,
        sku="NECKLACE-001-18K",
        weight=10,
    )

    with pytest.raises(ProductVariantNotFoundError):
        CartService.add_item(
            user=user,
            product_id=product.id,
            variant_id=variant.id,
            quantity=1,
        )


@pytest.mark.django_db
def test_add_nonexistent_product(user):
    with pytest.raises(ProductNotFoundError):
        CartService.add_item(
            user=user,
            product_id=999999,
            quantity=1,
        )


@pytest.mark.django_db
def test_add_invalid_quantity(user, product):
    with pytest.raises(InvalidCartQuantityError):
        CartService.add_item(
            user=user,
            product_id=product.id,
            quantity=0,
        )


@pytest.mark.django_db
def test_update_item(user, product):
    item = CartService.add_item(
        user=user,
        product_id=product.id,
        quantity=2,
    )

    updated = CartService.update_item(
        user=user,
        item_id=item.id,
        quantity=5,
    )

    assert updated.quantity == 5


@pytest.mark.django_db
def test_update_nonexistent_item(user):
    with pytest.raises(CartItemNotFoundError):
        CartService.update_item(
            user=user,
            item_id=999999,
            quantity=2,
        )


@pytest.mark.django_db
def test_user_cannot_update_another_users_cart_item(user, product):
    another_user = User.objects.create_user(
        phone_number="09120000002",
        password="TestPassword123!",
    )

    item = CartService.add_item(
        user=another_user,
        product_id=product.id,
        quantity=2,
    )

    with pytest.raises(CartItemNotFoundError):
        CartService.update_item(
            user=user,
            item_id=item.id,
            quantity=5,
        )

    item.refresh_from_db()

    assert item.quantity == 2


@pytest.mark.django_db
def test_remove_item(user, product):
    item = CartService.add_item(
        user=user,
        product_id=product.id,
        quantity=2,
    )

    CartService.remove_item(
        user=user,
        item_id=item.id,
    )

    assert not CartItem.objects.filter(id=item.id).exists()


@pytest.mark.django_db
def test_user_cannot_remove_another_users_cart_item(user, product):
    another_user = User.objects.create_user(
        phone_number="09120000003",
        password="TestPassword123!",
    )

    item = CartService.add_item(
        user=another_user,
        product_id=product.id,
        quantity=2,
    )

    with pytest.raises(CartItemNotFoundError):
        CartService.remove_item(
            user=user,
            item_id=item.id,
        )

    assert CartItem.objects.filter(id=item.id).exists()


@pytest.mark.django_db
def test_clear_cart(user, product):
    CartService.add_item(
        user=user,
        product_id=product.id,
        quantity=2,
    )

    CartService.clear_cart(user)

    cart = Cart.objects.get(user=user)

    assert cart.items.count() == 0