from django.db import transaction

from apps.pricing.models import MarketPrice, PriceProvider
from apps.pricing.providers.base import PriceProvider as PriceProviderContract


class MarketPriceSyncService:
    """
    Synchronizes external market prices with the database.

    Historical market prices are never overwritten or deleted.
    The previous active price is deactivated and a new record is created.
    """

    def __init__(self, provider: PriceProviderContract) -> None:
        self.provider = provider

    @transaction.atomic
    def sync(self) -> list[MarketPrice]:
        """
        Fetch prices from the provider and persist them.

        Returns:
            Newly created MarketPrice records.
        """

        prices = self.provider.fetch_prices()

        if not prices:
            return []

        created_prices: list[MarketPrice] = []

        for price_data in prices:
            MarketPrice.objects.filter(
                asset=price_data.asset,
                purity=price_data.purity,
                is_active=True,
            ).update(is_active=False)

            market_price = MarketPrice.objects.create(
                asset=price_data.asset,
                purity=price_data.purity,
                buy_price=price_data.buy_price,
                sell_price=price_data.sell_price,
                currency=price_data.currency,
                provider=PriceProvider.EXTERNAL_API,
                source=price_data.source,
                is_active=True,
                effective_at=price_data.timestamp,
            )

            created_prices.append(market_price)

        return created_prices