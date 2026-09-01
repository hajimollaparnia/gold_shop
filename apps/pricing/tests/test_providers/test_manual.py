from datetime import datetime, timezone
from decimal import Decimal

from apps.pricing.providers.base import MarketPriceData
from apps.pricing.providers.manual import ManualPriceProvider


class TestManualPriceProvider:
    """Test suite for ManualPriceProvider."""

    def test_empty_provider_returns_empty_list(self):
        provider = ManualPriceProvider()

        assert provider.fetch_prices() == []

    def test_provider_returns_configured_prices(self):
        timestamp = datetime.now(timezone.utc)

        price = MarketPriceData(
            asset="GOLD_18K",
            buy_price=Decimal("69500000.00"),
            sell_price=Decimal("70000000.00"),
            currency="IRR",
            source="manual",
            timestamp=timestamp,
        )

        provider = ManualPriceProvider([price])

        result = provider.fetch_prices()

        assert result == [price]

    def test_provider_does_not_expose_internal_list(self):
        price = MarketPriceData(
            asset="GOLD_18K",
            buy_price=Decimal("69500000.00"),
            sell_price=Decimal("70000000.00"),
            currency="IRR",
            source="manual",
            timestamp=datetime.now(timezone.utc),
        )

        provider = ManualPriceProvider([price])

        result = provider.fetch_prices()
        result.clear()

        assert provider.fetch_prices() == [price]

    def test_from_values_creates_provider(self):
        provider = ManualPriceProvider.from_values(
            asset="GOLD_18K",
            buy_price=Decimal("69500000.00"),
            sell_price=Decimal("70000000.00"),
            currency="IRR",
        )

        result = provider.fetch_prices()

        assert len(result) == 1
        assert result[0].asset == "GOLD_18K"
        assert result[0].buy_price == Decimal("69500000.00")
        assert result[0].sell_price == Decimal("70000000.00")
        assert result[0].currency == "IRR"
        assert result[0].source == "manual"

    def test_from_values_preserves_timestamp(self):
        timestamp = datetime.now(timezone.utc)

        provider = ManualPriceProvider.from_values(
            asset="GOLD_18K",
            buy_price=Decimal("69500000.00"),
            sell_price=Decimal("70000000.00"),
            currency="IRR",
            timestamp=timestamp,
        )

        result = provider.fetch_prices()

        assert result[0].timestamp == timestamp