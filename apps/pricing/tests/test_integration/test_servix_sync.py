from decimal import Decimal

import pytest
from django.conf import settings

from apps.pricing.models import MarketPrice, PriceProvider
from apps.pricing.providers.external import ServixPriceProvider
from apps.pricing.services.market_price_sync import MarketPriceSyncService


@pytest.mark.integration
@pytest.mark.django_db
def test_servix_sync_creates_market_price():
    if not settings.SERVIX_API_KEY:
        pytest.skip("SERVIX_API_KEY is not configured.")

    provider = ServixPriceProvider(
        api_key=settings.SERVIX_API_KEY,
    )

    service = MarketPriceSyncService(provider)

    created_prices = service.sync()

    assert created_prices

    price = created_prices[0]

    assert price.asset == "gold"
    assert price.purity == 18
    assert price.provider == PriceProvider.EXTERNAL_API
    assert price.source == "servix:GOLD_18_RLS"
    assert price.is_active is True

    assert price.buy_price > Decimal("0")
    assert price.sell_price > Decimal("0")

    assert MarketPrice.objects.filter(
        asset="gold",
        purity=18,
        is_active=True,
    ).count() == 1