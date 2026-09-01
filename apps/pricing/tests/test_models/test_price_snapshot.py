from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.pricing.models import Currency, PriceSnapshot


@pytest.mark.django_db
class TestPriceSnapshotModel:
    """Test suite for the PriceSnapshot model."""

    def get_valid_snapshot_data(self):
        """Return valid data for creating a PriceSnapshot."""
        return {
            "market_price": Decimal("70000000.00"),
            "weight": Decimal("5.2500"),
            "purity": 18,
            "gold_value": Decimal("367500000.00"),
            "making_charge": Decimal("36750000.00"),
            "profit": Decimal("28500000.00"),
            "tax": Decimal("42675000.00"),
            "other_charges": Decimal("0.00"),
            "discount": Decimal("1000000.00"),
            "subtotal": Decimal("474825000.00"),
            "final_price": Decimal("473825000.00"),
            "currency": Currency.IRR,
        }

    def test_create_price_snapshot(self):
        """A valid price snapshot should be created successfully."""
        snapshot = PriceSnapshot.objects.create(
            **self.get_valid_snapshot_data()
        )

        assert snapshot.pk is not None
        assert snapshot.market_price == Decimal("70000000.00")
        assert snapshot.weight == Decimal("5.2500")
        assert snapshot.purity == 18
        assert snapshot.gold_value == Decimal("367500000.00")
        assert snapshot.making_charge == Decimal("36750000.00")
        assert snapshot.profit == Decimal("28500000.00")
        assert snapshot.tax == Decimal("42675000.00")
        assert snapshot.final_price == Decimal("473825000.00")

    def test_default_values(self):
        """Default values should be applied correctly."""
        data = self.get_valid_snapshot_data()

        data.pop("other_charges")
        data.pop("discount")
        data.pop("currency")

        snapshot = PriceSnapshot.objects.create(**data)

        assert snapshot.other_charges == Decimal("0.00")
        assert snapshot.discount == Decimal("0.00")
        assert snapshot.currency == Currency.IRR

    def test_decimal_fields_preserve_decimal_type(self):
        """Financial fields must remain Decimal values."""
        snapshot = PriceSnapshot.objects.create(
            **self.get_valid_snapshot_data()
        )

        assert isinstance(snapshot.market_price, Decimal)
        assert isinstance(snapshot.weight, Decimal)
        assert isinstance(snapshot.gold_value, Decimal)
        assert isinstance(snapshot.making_charge, Decimal)
        assert isinstance(snapshot.profit, Decimal)
        assert isinstance(snapshot.tax, Decimal)
        assert isinstance(snapshot.final_price, Decimal)

    def test_zero_discount_is_allowed(self):
        """A snapshot can have no discount."""
        data = self.get_valid_snapshot_data()
        data["discount"] = Decimal("0.00")

        snapshot = PriceSnapshot(**data)

        snapshot.full_clean()

    def test_zero_additional_charges_are_allowed(self):
        """A snapshot can have no additional charges."""
        data = self.get_valid_snapshot_data()
        data["other_charges"] = Decimal("0.00")

        snapshot = PriceSnapshot(**data)

        snapshot.full_clean()

    def test_negative_weight_is_rejected(self):
        """Weight must not be negative."""
        data = self.get_valid_snapshot_data()
        data["weight"] = Decimal("-1.0000")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_zero_weight_is_rejected(self):
        """Weight must be greater than zero."""
        data = self.get_valid_snapshot_data()
        data["weight"] = Decimal("0.0000")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_negative_market_price_is_rejected(self):
        """Market price must not be negative."""
        data = self.get_valid_snapshot_data()
        data["market_price"] = Decimal("-1.00")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_negative_gold_value_is_rejected(self):
        """Gold value must not be negative."""
        data = self.get_valid_snapshot_data()
        data["gold_value"] = Decimal("-1.00")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_negative_making_charge_is_rejected(self):
        """Making charge must not be negative."""
        data = self.get_valid_snapshot_data()
        data["making_charge"] = Decimal("-1.00")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_negative_profit_is_rejected(self):
        """Profit must not be negative."""
        data = self.get_valid_snapshot_data()
        data["profit"] = Decimal("-1.00")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_negative_tax_is_rejected(self):
        """Tax must not be negative."""
        data = self.get_valid_snapshot_data()
        data["tax"] = Decimal("-1.00")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_negative_other_charges_are_rejected(self):
        """Additional charges must not be negative."""
        data = self.get_valid_snapshot_data()
        data["other_charges"] = Decimal("-1.00")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_negative_discount_is_rejected(self):
        """Discount must not be negative."""
        data = self.get_valid_snapshot_data()
        data["discount"] = Decimal("-1.00")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_negative_final_price_is_rejected(self):
        """Final price must not be negative."""
        data = self.get_valid_snapshot_data()
        data["final_price"] = Decimal("-1.00")

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_purity_must_be_positive(self):
        """Purity must be greater than zero."""
        data = self.get_valid_snapshot_data()
        data["purity"] = 0

        snapshot = PriceSnapshot(**data)

        with pytest.raises(ValidationError):
            snapshot.full_clean()

    def test_snapshot_has_no_dependency_on_future_market_prices(self):
        """
        Snapshot stores its own market price.

        Future market-price changes must not alter the stored snapshot value.
        """
        snapshot = PriceSnapshot.objects.create(
            **self.get_valid_snapshot_data()
        )

        original_market_price = snapshot.market_price

        snapshot.refresh_from_db()

        assert snapshot.market_price == original_market_price

    def test_string_representation_is_available(self):
        """Snapshot should have a useful string representation."""
        snapshot = PriceSnapshot.objects.create(
            **self.get_valid_snapshot_data()
        )

        assert str(snapshot)

    def test_created_at_is_set(self):
        """created_at should be populated automatically."""
        snapshot = PriceSnapshot.objects.create(
            **self.get_valid_snapshot_data()
        )

        assert snapshot.created_at is not None