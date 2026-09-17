import pytest
from django.db import IntegrityError

from apps.wishlist.models import Wishlist, WishlistItem


@pytest.mark.django_db
def test_wishlist_can_be_created(user):
    wishlist = Wishlist.objects.create(user=user)

    assert wishlist.user == user


@pytest.mark.django_db
def test_user_can_have_only_one_wishlist(user):
    Wishlist.objects.create(user=user)

    with pytest.raises(IntegrityError):
        Wishlist.objects.create(user=user)


@pytest.mark.django_db
def test_wishlist_item_can_be_created(user, product):
    wishlist = Wishlist.objects.create(user=user)

    item = WishlistItem.objects.create(
        wishlist=wishlist,
        product=product,
    )

    assert item.wishlist == wishlist
    assert item.product == product
    assert item.variant is None


@pytest.mark.django_db
def test_wishlist_item_can_reference_variant(
    user,
    product,
    variant,
):
    wishlist = Wishlist.objects.create(user=user)

    item = WishlistItem.objects.create(
        wishlist=wishlist,
        product=product,
        variant=variant,
    )

    assert item.variant == variant


@pytest.mark.django_db
def test_duplicate_wishlist_item_is_rejected(
    user,
    product,
):
    wishlist = Wishlist.objects.create(user=user)

    WishlistItem.objects.create(
        wishlist=wishlist,
        product=product,
    )

    with pytest.raises(IntegrityError):
        WishlistItem.objects.create(
            wishlist=wishlist,
            product=product,
        )