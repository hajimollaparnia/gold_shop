from django.db.models import QuerySet

from .models import Payment


def get_payment_by_id(
    *,
    payment_id: int,
) -> Payment:
    """Return a payment with its related order."""

    return Payment.objects.select_related(
        "order",
        "order__user",
    ).get(pk=payment_id)


def get_user_payments(
    *,
    user,
) -> QuerySet[Payment]:
    """Return payments belonging to the given user's orders."""

    return (
        Payment.objects
        .filter(order__user=user)
        .select_related("order")
        .prefetch_related("logs", "refunds")
    )


def get_order_payments(
    *,
    order_id: int,
) -> QuerySet[Payment]:
    """Return all payment attempts associated with an order."""

    return (
        Payment.objects
        .filter(order_id=order_id)
        .order_by("-created_at")
    )