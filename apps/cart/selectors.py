from django.db.models import Prefetch

from .models import Cart, CartItem


class CartSelector:
    """Provides optimized read-only queries for shopping carts."""

    @staticmethod
    def get_cart_for_user(user):
        """
        Return the user's cart with its items loaded efficiently.
        """

        return (
            Cart.objects
            .filter(user=user)
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=CartItem.objects.select_related(
                        "product",
                        "variant",
                    ),
                )
            )
            .first()
        )

    @staticmethod
    def get_cart_item_for_user(user, item_id):
        """
        Return a specific cart item belonging to the authenticated user.
        """

        return (
            CartItem.objects
            .select_related(
                "cart",
                "product",
                "variant",
            )
            .filter(
                id=item_id,
                cart__user=user,
            )
            .first()
        )