from django.db.models import QuerySet

from .models import Order


class OrderSelector:
    """
    Provides optimized read-only queries for orders.
    """

    @staticmethod
    def get_user_orders(user) -> QuerySet[Order]:
        """
        Return all orders belonging to a specific user.
        """

        return (
            Order.objects
            .filter(user=user)
            .prefetch_related("items")
            .order_by("-created_at")
        )

    @staticmethod
    def get_order_for_user(
        *,
        user,
        order_id: int,
    ) -> Order:
        """
        Return a single order belonging to the given user.
        """

        return (
            Order.objects
            .select_related("user")
            .prefetch_related(
                "items",
                "items__product",
                "items__variant",
                "items__price_snapshot",
            )
            .get(
                pk=order_id,
                user=user,
            )
        )