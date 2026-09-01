from datetime import datetime
from decimal import Decimal

from .base import MarketPriceData, PriceProvider

class ManualPriceProvider(PriceProvider):
    """
    Price provider for manually supplied market prices.

    This provider does not communicate with an external API.
    It is useful for:
    - Admin-managed market prices
    - Local development
    - Testing
    - Fallback pricing
    """

    def __init__(
        self,
        prices: list[MarketPriceData] | None = None,
    ) -> None:
        self._prices = prices or []

    def fetch_prices(self) -> list[MarketPriceData]:
        """
        Return manually configured market prices.
        """
        return list(self._prices)

    @classmethod
    def from_values(
        cls,
        *,
        asset: str,
        buy_price: Decimal,
        sell_price: Decimal,
        currency: str,
        source: str = "manual",
        timestamp: datetime | None = None,
    ) -> "ManualPriceProvider":
        """
        Build a ManualPriceProvider from a single price record.
        """
        price = MarketPriceData(
            asset=asset,
            buy_price=buy_price,
            sell_price=sell_price,
            currency=currency,
            source=source,
            timestamp=timestamp or datetime.now(),
        )

        return cls([price])