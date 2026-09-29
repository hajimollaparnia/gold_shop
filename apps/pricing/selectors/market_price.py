from apps.pricing.models import MarketPrice


def get_active_gold_price() -> MarketPrice | None:
    """
    Return the currently active 18K gold market price.
    """
    return (
        MarketPrice.objects
        .filter(
            asset="gold",
            purity=18,
            is_active=True,
        )
        .first()
    )