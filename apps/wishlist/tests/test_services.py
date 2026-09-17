import pytest

from apps.wishlist.exceptions import (
    ProductNotFoundError,
    ProductVariantNotFoundError,
    WishlistItemAlreadyExistsError,
    WishlistItemNotFoundError,
)
from apps.wishlist.models import Wishlist, WishlistItem
from apps.wishlist.services import WishlistService


@pytest.mark.django_db
def test_get_or_create_wishlist(user):
    wishlist = WishlistService.get_or_create_wishlist(user)

    assert wishlist.user == user

    same_wishlist = WishlistService.get_or_create_wishlist(user)

    assert same_wishlist.pk == wishlist.pk


@pytest.mark.django_db
def test_add_product_to_wishlist(user, product):
    item = WishlistService.add_item(
        user=user,
        product_id=product.id,
    )

    assert item.product == product
    assert item.variant is None
    assert item.wishlist.user == user


@pytest.mark.django_db
def test_add_variant_to_wishlist(
    user,
    product,
    variant,
):
    item = WishlistService.add_item(
        user=user,
        product_id=product.id,
        variant_id=variant.id,
    )

    assert item.product == product
    assert item.variant == variant


@pytest.mark.django_db
def test_add_nonexistent_product_raises_error(user):
    with pytest.raises(ProductNotFoundError):
        WishlistService.add_item(
            user=user,
            product_id=999999,
        )


@pytest.mark.django_db
def test_add_nonexistent_variant_raises_error(
    user,
    product,
):
    with pytest.raises(ProductVariantNotFoundError):
        WishlistService.add_item(
            user=user,
            product_id=product.id,
            variant_id=999999,
        )


@pytest.mark.django_db
def test_variant_must_belong_to_product(
    user,
    product,
    category,
):
    another_product = product.__class__.objects.create(
        category=category,
        name="Another Gold Ring",
        sku="WISH-RING-002",
        weight=6,
        purity=750,
    )

    from apps.catalog.models import ProductVariant

    another_variant = ProductVariant.objects.create(
        product=another_product,
        sku="WISH-RING-002-18K",
        weight=6,
    )

    with pytest.raises(ProductVariantNotFoundError):
        WishlistService.add_item(
            user=user,
            product_id=product.id,
            variant_id=another_variant.id,
        )


@pytest.mark.django_db
def test_duplicate_item_raises_error(
    user,
    product,
):
    WishlistService.add_item(
        user=user,
        product_id=product.id,
    )

    with pytest.raises(WishlistItemAlreadyExistsError):
        WishlistService.add_item(
            user=user,
            product_id=product.id,
        )


@pytest.mark.django_db
def test_same_product_with_different_variants_is_allowed(
    user,
    product,
    variant,
):
    first_item = WishlistService.add_item(
        user=user,
        product_id=product.id,
    )

    second_item = WishlistService.add_item(
        user=user,
        product_id=product.id,
        variant_id=variant.id,
    )

    assert first_item.pk != second_item.pk
    assert WishlistItem.objects.filter(
        wishlist__user=user,
    ).count() == 2


@pytest.mark.django_db
def test_remove_item(user, product):
    item = WishlistService.add_item(
        user=user,
        product_id=product.id,
    )

    WishlistService.remove_item(
        user=user,
        item_id=item.id,
    )

    assert not WishlistItem.objects.filter(
        id=item.id,
    ).exists()


@pytest.mark.django_db
def test_remove_nonexistent_item_raises_error(user):
    with pytest.raises(WishlistItemNotFoundError):
        WishlistService.remove_item(
            user=user,
            item_id=999999,
        )


@pytest.mark.django_db
def test_user_cannot_remove_another_users_item(
    user,
    second_user,
    product,
):
    item = WishlistService.add_item(
        user=second_user,
        product_id=product.id,
    )

    with pytest.raises(WishlistItemNotFoundError):
        WishlistService.remove_item(
            user=user,
            item_id=item.id,
        )


@pytest.mark.django_db
def test_clear_wishlist(user, product, variant):
    WishlistService.add_item(
        user=user,
        product_id=product.id,
    )

    WishlistService.add_item(
        user=user,
        product_id=product.id,
        variant_id=variant.id,
    )

    WishlistService.clear_wishlist(user)

    assert WishlistItem.objects.filter(
        wishlist__user=user,
    ).count() == 0