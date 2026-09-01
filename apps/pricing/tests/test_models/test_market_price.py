from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.pricing.models import (
    Currency,
    MarketAsset,
    MarketPrice,
    PriceProvider,
)


@pytest.mark.django_db
class TestMarketPriceModel:
    """Test suite for the MarketPrice model."""

    def get_valid_market_price_data(self):
        """Return valid data for creating a MarketPrice instance."""
        return {
            "asset": MarketAsset.GOLD,
            "purity": 18,
            "buy_price": Decimal("69000000.00"),
            "sell_price": Decimal("70000000.00"),
            "currency": Currency.IRR,
            "provider": PriceProvider.MANUAL,
            "source": "Admin",
            "effective_at": timezone.now(),
        }

    def test_create_market_price(self):
        """A valid market price should be created successfully."""
        market_price = MarketPrice.objects.create(
            **self.get_valid_market_price_data()
        )

        assert market_price.pk is not None
        assert market_price.asset == MarketAsset.GOLD
        assert market_price.purity == 18
        assert market_price.buy_price == Decimal("69000000.00")
        assert market_price.sell_price == Decimal("70000000.00")
        assert market_price.currency == Currency.IRR
        assert market_price.provider == PriceProvider.MANUAL
        assert market_price.source == "Admin"

    def test_default_values(self):
        """Default model values should be applied correctly."""
        data = self.get_valid_market_price_data()

        data.pop("currency")
        data.pop("provider")
        data.pop("source")

        market_price = MarketPrice.objects.create(**data)

        assert market_price.currency == Currency.IRR
        assert market_price.provider == PriceProvider.MANUAL
        assert market_price.source == ""
        assert market_price.is_active is True

    def test_market_price_is_active_by_default(self):
        """New market prices should be active by default."""
        market_price = MarketPrice.objects.create(
            **self.get_valid_market_price_data()
        )

        assert market_price.is_active is True

    def test_market_price_can_be_deactivated(self):
        """A market price should be able to be deactivated."""
        data = self.get_valid_market_price_data()
        data["is_active"] = False

        market_price = MarketPrice.objects.create(**data)

        assert market_price.is_active is False

    def test_string_representation_for_gold_with_purity(self):
        """Gold prices should include purity in their string representation."""
        market_price = MarketPrice.objects.create(
            **self.get_valid_market_price_data()
        )

        assert str(market_price) == "Gold 18K - 70000000.00 IRR"

    def test_string_representation_without_purity(self):
        """Assets without purity should still have a valid string representation."""
        data = self.get_valid_market_price_data()
        data["asset"] = MarketAsset.COIN
        data["purity"] = None

        market_price = MarketPrice.objects.create(**data)

        assert str(market_price) == "Coin - 70000000.00 IRR"

    def test_market_price_ordering_by_effective_at(self):
        """Newest effective prices should appear first."""
        older_price = MarketPrice.objects.create(
            **{
                **self.get_valid_market_price_data(),
                "effective_at": timezone.now() - timedelta(hours=1),
                "sell_price": Decimal("68000000.00"),
            }
        )

        newer_price = MarketPrice.objects.create(
            **{
                **self.get_valid_market_price_data(),
                "effective_at": timezone.now(),
                "sell_price": Decimal("70000000.00"),
            }
        )

        prices = list(MarketPrice.objects.all())

        assert prices[0] == newer_price
        assert prices[1] == older_price

    def test_created_at_is_set_automatically(self):
        """created_at should be populated automatically."""
        market_price = MarketPrice.objects.create(
            **self.get_valid_market_price_data()
        )

        assert market_price.created_at is not None

    def test_updated_at_is_set_automatically(self):
        """updated_at should be populated automatically."""
        market_price = MarketPrice.objects.create(
            **self.get_valid_market_price_data()
        )

        assert market_price.updated_at is not None

    def test_negative_buy_price_fails_validation(self):
        """Negative buy prices should fail model validation."""
        data = self.get_valid_market_price_data()
        data["buy_price"] = Decimal("-1.00")

        market_price = MarketPrice(**data)

        with pytest.raises(ValidationError):
            market_price.full_clean()

    def test_negative_sell_price_fails_validation(self):
        """Negative sell prices should fail model validation."""
        data = self.get_valid_market_price_data()
        data["sell_price"] = Decimal("-1.00")

        market_price = MarketPrice(**data)

        with pytest.raises(ValidationError):
            market_price.full_clean()

    def test_zero_buy_price_is_allowed(self):
        """Zero buy price is technically valid at the model level."""
        data = self.get_valid_market_price_data()
        data["buy_price"] = Decimal("0.00")

        market_price = MarketPrice(**data)

        market_price.full_clean()

    def test_zero_sell_price_is_allowed(self):
        """Zero sell price is technically valid at the model level."""
        data = self.get_valid_market_price_data()
        data["sell_price"] = Decimal("0.00")

        market_price = MarketPrice(**data)

        market_price.full_clean()

    def test_purity_must_be_positive_when_provided(self):
        """Provided purity values must be greater than zero."""
        data = self.get_valid_market_price_data()
        data["purity"] = 0

        market_price = MarketPrice(**data)

        with pytest.raises(ValidationError):
            market_price.full_clean()

    def test_purity_can_be_null(self):
        """Purity may be null for assets where it is not applicable."""
        data = self.get_valid_market_price_data()
        data["asset"] = MarketAsset.COIN
        data["purity"] = None

        market_price = MarketPrice(**data)

        market_price.full_clean()

    def test_source_is_optional(self):
        """Source should be optional."""
        data = self.get_valid_market_price_data()
        data["source"] = ""

        market_price = MarketPrice.objects.create(**data)

        assert market_price.source == ""

    def test_provider_is_stored_correctly(self):
        """Provider information should be stored correctly."""
        data = self.get_valid_market_price_data()
        data["provider"] = PriceProvider.EXTERNAL_API

        market_price = MarketPrice.objects.create(**data)

        assert market_price.provider == PriceProvider.EXTERNAL_API

    def test_effective_at_is_stored_correctly(self):
        """The effective timestamp should be stored without modification."""
        effective_at = timezone.now()

        data = self.get_valid_market_price_data()
        data["effective_at"] = effective_at

        market_price = MarketPrice.objects.create(**data)

        assert market_price.effective_at == effective_at

    def test_decimal_precision_is_preserved(self):
        """Financial values must remain Decimal values."""
        market_price = MarketPrice.objects.create(
            **self.get_valid_market_price_data()
        )

        assert isinstance(market_price.buy_price, Decimal)
        assert isinstance(market_price.sell_price, Decimal)

    def test_market_price_can_be_inactive(self):
        """Inactive historical market prices should be supported."""
        data = self.get_valid_market_price_data()
        data["is_active"] = False

        market_price = MarketPrice.objects.create(**data)

        assert market_price.is_active is False

    def test_database_rejects_negative_buy_price(self):
        """Database constraints should reject negative buy prices."""
        data = self.get_valid_market_price_data()
        data["buy_price"] = Decimal("-1.00")

        with pytest.raises(IntegrityError):
            MarketPrice.objects.create(**data)

    def test_database_rejects_negative_sell_price(self):
        """Database constraints should reject negative sell prices."""
        data = self.get_valid_market_price_data()
        data["sell_price"] = Decimal("-1.00")

        with pytest.raises(IntegrityError):
            MarketPrice.objects.create(**data)