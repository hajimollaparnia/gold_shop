from django.db import transaction

from apps.catalog.models import Product, ProductVariant

from .exceptions import (
    ProductNotFoundError,
    ProductVariantNotFoundError,
    WishlistItemAlreadyExistsError,
    WishlistItemNotFoundError,
)
from .models import Wishlist, WishlistItem


class WishlistService:
    """Provides transactional business operations for wishlists."""

    @staticmethod
    @transaction.atomic
    def get_or_create_wishlist(user):
        """Return the user's existing wishlist or create a new one."""

        wishlist, _ = Wishlist.objects.get_or_create(user=user)
        return wishlist

    @staticmethod
    @transaction.atomic
    def add_item(user, product_id, variant_id=None):
        """Add a product or variant to the user's wishlist."""

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist as exc:
            raise ProductNotFoundError(
                "The requested product does not exist."
            ) from exc

        variant = None

        if variant_id is not None:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                )
            except ProductVariant.DoesNotExist as exc:
                raise ProductVariantNotFoundError(
                    "The requested product variant does not exist."
                ) from exc

        wishlist = WishlistService.get_or_create_wishlist(user)

        if WishlistItem.objects.filter(
            wishlist=wishlist,
            product=product,
            variant=variant,
        ).exists():
            raise WishlistItemAlreadyExistsError(
                "The item is already in the wishlist."
            )

        return WishlistItem.objects.create(
            wishlist=wishlist,
            product=product,
            variant=variant,
        )

    @staticmethod
    @transaction.atomic
    def remove_item(user, item_id):
        """Remove a wishlist item owned by the authenticated user."""

        try:
            item = WishlistItem.objects.get(
                id=item_id,
                wishlist__user=user,
            )
        except WishlistItem.DoesNotExist as exc:
            raise WishlistItemNotFoundError(
                "The requested wishlist item does not exist."
            ) from exc

        item.delete()

    @staticmethod
    @transaction.atomic
    def clear_wishlist(user):
        """Remove all items from the user's wishlist."""

        wishlist = Wishlist.objects.filter(user=user).first()

        if wishlist:
            wishlist.items.all().delete()

    @staticmethod
    def get_wishlist(user):
        """Return the user's wishlist."""

        return (
            Wishlist.objects
            .filter(user=user)
            .prefetch_related(
                "items__product",
                "items__variant",
            )
            .first()
        )