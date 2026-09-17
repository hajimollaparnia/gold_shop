import pytest

from apps.cart.models import Cart, CartItem


@pytest.mark.django_db
def test_cart_can_be_created(user):
    cart = Cart.objects.create(user=user)

    assert cart.pk is not None
    assert cart.user == user


@pytest.mark.django_db
def test_user_can_have_only_one_cart(user):
    Cart.objects.create(user=user)

    with pytest.raises(Exception):
        Cart.objects.create(user=user)


@pytest.mark.django_db
def test_cart_item_can_be_created(cart, product):
    item = CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2,
    )

    assert item.pk is not None
    assert item.quantity == 2


@pytest.mark.django_db
def test_cart_item_belongs_to_cart(cart, product):
    item = CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2,
    )

    assert item.cart == cart


@pytest.mark.django_db
def test_cart_item_quantity_must_be_positive(cart, product):
    item = CartItem(
        cart=cart,
        product=product,
        quantity=0,
    )

    with pytest.raises(Exception):
        item.full_clean()