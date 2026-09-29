from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

import pytest

from apps.pricing.models import MarketPrice, PriceProvider
from apps.pricing.providers.base import MarketPriceData
from apps.pricing.services.market_price_sync import MarketPriceSyncService


@pytest.mark.django_db
def test_sync_creates_new_market_price():
    provider = Mock()

    provider.fetch_prices.return_value = [
        MarketPriceData(
            asset="gold",
            purity=18,
            buy_price=Decimal("100000000"),
            sell_price=Decimal("101000000"),
            currency="IRR",
            source="test:provider",
            timestamp=datetime(
                2026,
                9,
                27,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )
    ]

    service = MarketPriceSyncService(provider)

    created_prices = service.sync()

    assert len(created_prices) == 1

    price = created_prices[0]

    assert price.asset == "gold"
    assert price.purity == 18
    assert price.buy_price == Decimal("100000000")
    assert price.sell_price == Decimal("101000000")
    assert price.currency == "IRR"
    assert price.provider == PriceProvider.EXTERNAL_API
    assert price.source == "test:provider"
    assert price.is_active is True

    assert MarketPrice.objects.count() == 1


@pytest.mark.django_db
def test_sync_deactivates_previous_active_price():
    old_price = MarketPrice.objects.create(
        asset="gold",
        purity=18,
        buy_price=Decimal("90000000"),
        sell_price=Decimal("91000000"),
        currency="IRR",
        provider=PriceProvider.MANUAL,
        source="test:old",
        is_active=True,
        effective_at=datetime(
            2026,
            9,
            27,
            9,
            0,
            tzinfo=timezone.utc,
        ),
    )

    provider = Mock()

    provider.fetch_prices.return_value = [
        MarketPriceData(
            asset="gold",
            purity=18,
            buy_price=Decimal("100000000"),
            sell_price=Decimal("101000000"),
            currency="IRR",
            source="test:new",
            timestamp=datetime(
                2026,
                9,
                27,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )
    ]

    service = MarketPriceSyncService(provider)
    created_prices = service.sync()

    old_price.refresh_from_db()

    assert old_price.is_active is False
    assert created_prices[0].is_active is True

    assert MarketPrice.objects.filter(
        asset="gold",
        purity=18,
        is_active=True,
    ).count() == 1

    assert MarketPrice.objects.count() == 2


@pytest.mark.django_db
def test_sync_preserves_historical_prices():
    first_provider = Mock()

    first_provider.fetch_prices.return_value = [
        MarketPriceData(
            asset="gold",
            purity=18,
            buy_price=Decimal("90000000"),
            sell_price=Decimal("91000000"),
            currency="IRR",
            source="test:first",
            timestamp=datetime(
                2026,
                9,
                27,
                9,
                0,
                tzinfo=timezone.utc,
            ),
        )
    ]

    service = MarketPriceSyncService(first_provider)
    service.sync()

    second_provider = Mock()

    second_provider.fetch_prices.return_value = [
        MarketPriceData(
            asset="gold",
            purity=18,
            buy_price=Decimal("100000000"),
            sell_price=Decimal("101000000"),
            currency="IRR",
            source="test:second",
            timestamp=datetime(
                2026,
                9,
                27,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )
    ]

    service = MarketPriceSyncService(second_provider)
    service.sync()

    prices = MarketPrice.objects.order_by("effective_at")

    assert prices.count() == 2

    assert prices[0].buy_price == Decimal("90000000")
    assert prices[0].is_active is False

    assert prices[1].buy_price == Decimal("100000000")
    assert prices[1].is_active is True


@pytest.mark.django_db
def test_sync_returns_empty_list_when_provider_returns_no_prices():
    provider = Mock()
    provider.fetch_prices.return_value = []

    service = MarketPriceSyncService(provider)

    result = service.sync()

    assert result == []
    assert MarketPrice.objects.count() == 0