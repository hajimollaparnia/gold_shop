from datetime import datetime, timezone
from decimal import Decimal

import pytest

from apps.pricing.providers.base import MarketPriceData, PriceProvider


class TestMarketPriceData:
    """Test suite for normalized market price data."""

    def get_valid_data(self):
        return {
            "asset": "GOLD_18K",
            "buy_price": Decimal("69500000.00"),
            "sell_price": Decimal("70000000.00"),
            "currency": "IRR",
            "source": "manual",
            "timestamp": datetime.now(timezone.utc),
        }

    def test_market_price_data_creation(self):
        """MarketPriceData should be created with valid data."""
        data = MarketPriceData(**self.get_valid_data())

        assert data.asset == "GOLD_18K"
        assert data.buy_price == Decimal("69500000.00")
        assert data.sell_price == Decimal("70000000.00")
        assert data.currency == "IRR"
        assert data.source == "manual"

    def test_market_price_data_is_immutable(self):
        """MarketPriceData should be immutable."""
        data = MarketPriceData(**self.get_valid_data())

        with pytest.raises(AttributeError):
            data.buy_price = Decimal("80000000.00")

    def test_market_price_data_uses_decimal(self):
        """Financial values must use Decimal."""
        data = MarketPriceData(**self.get_valid_data())

        assert isinstance(data.buy_price, Decimal)
        assert isinstance(data.sell_price, Decimal)

    def test_market_price_data_has_timestamp(self):
        """Market price data must contain a timestamp."""
        data = MarketPriceData(**self.get_valid_data())

        assert isinstance(data.timestamp, datetime)

    def test_negative_buy_price_is_rejected(self):
        """Negative buy prices must be rejected."""
        data = self.get_valid_data()
        data["buy_price"] = Decimal("-1.00")

        with pytest.raises(ValueError, match="buy_price"):
            MarketPriceData(**data)

    def test_negative_sell_price_is_rejected(self):
        """Negative sell prices must be rejected."""
        data = self.get_valid_data()
        data["sell_price"] = Decimal("-1.00")

        with pytest.raises(ValueError, match="sell_price"):
            MarketPriceData(**data)

    def test_sell_price_cannot_be_lower_than_buy_price(self):
        """Sell price must not be lower than buy price."""
        data = self.get_valid_data()
        data["buy_price"] = Decimal("70000000.00")
        data["sell_price"] = Decimal("69000000.00")

        with pytest.raises(ValueError, match="sell_price"):
            MarketPriceData(**data)

    def test_empty_asset_is_rejected(self):
        """Asset must not be empty."""
        data = self.get_valid_data()
        data["asset"] = ""

        with pytest.raises(ValueError, match="asset"):
            MarketPriceData(**data)

    def test_empty_currency_is_rejected(self):
        """Currency must not be empty."""
        data = self.get_valid_data()
        data["currency"] = ""

        with pytest.raises(ValueError, match="currency"):
            MarketPriceData(**data)

    def test_empty_source_is_rejected(self):
        """Source must not be empty."""
        data = self.get_valid_data()
        data["source"] = ""

        with pytest.raises(ValueError, match="source"):
            MarketPriceData(**data)


class TestPriceProvider:
    """Test suite for the PriceProvider contract."""

    def test_provider_is_abstract(self):
        """PriceProvider must not be instantiated directly."""
        with pytest.raises(TypeError):
            PriceProvider()

    def test_fetch_prices_is_required(self):
        """Concrete providers must implement fetch_prices."""

        class IncompleteProvider(PriceProvider):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_concrete_provider_can_be_implemented(self):
        """A valid concrete provider should satisfy the contract."""

        class FakeProvider(PriceProvider):

            def fetch_prices(self):
                return [
                    MarketPriceData(
                        asset="GOLD_18K",
                        buy_price=Decimal("69500000.00"),
                        sell_price=Decimal("70000000.00"),
                        currency="IRR",
                        source="fake",
                        timestamp=datetime.now(timezone.utc),
                    )
                ]

        provider = FakeProvider()

        prices = provider.fetch_prices()

        assert len(prices) == 1
        assert isinstance(prices[0], MarketPriceData)
        assert prices[0].asset == "GOLD_18K"

    def test_provider_returns_normalized_data(self):
        """Provider output should use the normalized MarketPriceData contract."""

        class FakeProvider(PriceProvider):

            def fetch_prices(self):
                return [
                    MarketPriceData(
                        asset="SILVER",
                        buy_price=Decimal("1200000.00"),
                        sell_price=Decimal("1250000.00"),
                        currency="IRR",
                        source="fake",
                        timestamp=datetime.now(timezone.utc),
                    )
                ]

        provider = FakeProvider()
        result = provider.fetch_prices()

        assert isinstance(result, list)
        assert all(
            isinstance(item, MarketPriceData)
            for item in result
        )

