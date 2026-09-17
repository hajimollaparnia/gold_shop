from django.db.models import Prefetch

from .models import Wishlist, WishlistItem


class WishlistSelector:
    """Provides optimized read-only queries for wishlists."""

    @staticmethod
    def get_wishlist_for_user(user):
        """Return the user's wishlist with its items loaded efficiently."""

        return (
            Wishlist.objects
            .filter(user=user)
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=WishlistItem.objects.select_related(
                        "product",
                        "variant",
                    ),
                )
            )
            .first()
        )

    @staticmethod
    def get_item_for_user(user, item_id):
        """Return a specific wishlist item owned by the authenticated user."""

        return (
            WishlistItem.objects
            .select_related(
                "wishlist",
                "product",
                "variant",
            )
            .filter(
                id=item_id,
                wishlist__user=user,
            )
            .first()
        )