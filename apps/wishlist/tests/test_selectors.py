import pytest

from apps.wishlist.models import Wishlist, WishlistItem
from apps.wishlist.selectors import WishlistSelector
from apps.wishlist.services import WishlistService


@pytest.mark.django_db
def test_get_wishlist_for_user(
    user,
    product,
):
    wishlist = WishlistService.get_or_create_wishlist(user)

    WishlistItem.objects.create(
        wishlist=wishlist,
        product=product,
    )

    result = WishlistSelector.get_wishlist_for_user(user)

    assert result is not None
    assert result.pk == wishlist.pk
    assert result.items.count() == 1


@pytest.mark.django_db
def test_get_wishlist_for_user_returns_none_when_missing(user):
    result = WishlistSelector.get_wishlist_for_user(user)

    assert result is None


@pytest.mark.django_db
def test_get_item_for_user(
    user,
    product,
):
    wishlist = Wishlist.objects.create(user=user)

    item = WishlistItem.objects.create(
        wishlist=wishlist,
        product=product,
    )

    result = WishlistSelector.get_item_for_user(
        user=user,
        item_id=item.id,
    )

    assert result is not None
    assert result.pk == item.pk


@pytest.mark.django_db
def test_get_item_for_user_respects_ownership(
    user,
    second_user,
    product,
):
    wishlist = Wishlist.objects.create(user=second_user)

    item = WishlistItem.objects.create(
        wishlist=wishlist,
        product=product,
    )

    result = WishlistSelector.get_item_for_user(
        user=user,
        item_id=item.id,
    )

    assert result is None