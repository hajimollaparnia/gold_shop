from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.pricing.models import PricingRule


@pytest.mark.django_db
class TestPricingRuleModel:
    """Test suite for the PricingRule model."""

    def get_valid_pricing_rule_data(self):
        """Return valid data for creating a PricingRule instance."""
        return {
            "name": "Default Gold Pricing",
            "making_fee_type": "percentage",
            "making_fee_value": Decimal("10.0000"),
            "profit_type": "percentage",
            "profit_value": Decimal("7.0000"),
            "tax_rate": Decimal("10.0000"),
            "other_charge": Decimal("0.00"),
        }

    def test_create_pricing_rule(self):
        """A valid pricing rule should be created successfully."""
        rule = PricingRule.objects.create(
            **self.get_valid_pricing_rule_data()
        )

        assert rule.pk is not None
        assert rule.name == "Default Gold Pricing"
        assert rule.making_fee_type == "percentage"
        assert rule.making_fee_value == Decimal("10.0000")
        assert rule.profit_type == "percentage"
        assert rule.profit_value == Decimal("7.0000")
        assert rule.tax_rate == Decimal("10.0000")
        assert rule.other_charge == Decimal("0.00")

    def test_default_active_status(self):
        """New pricing rules should be active by default."""
        rule = PricingRule.objects.create(
            **self.get_valid_pricing_rule_data()
        )

        assert rule.is_active is True

    def test_rule_can_be_deactivated(self):
        """A pricing rule should be able to be deactivated."""
        data = self.get_valid_pricing_rule_data()
        data["is_active"] = False

        rule = PricingRule.objects.create(**data)

        assert rule.is_active is False

    def test_name_must_be_unique(self):
        """Pricing rule names must be unique."""
        PricingRule.objects.create(
            **self.get_valid_pricing_rule_data()
        )

        duplicate = PricingRule(
            **self.get_valid_pricing_rule_data()
        )

        with pytest.raises(ValidationError):
            duplicate.full_clean()

    def test_database_rejects_duplicate_name(self):
        """Database should reject duplicate pricing rule names."""
        PricingRule.objects.create(
            **self.get_valid_pricing_rule_data()
        )

        with pytest.raises(IntegrityError):
            PricingRule.objects.create(
                **self.get_valid_pricing_rule_data()
            )

    def test_decimal_values_are_preserved(self):
        """Financial and percentage values must remain Decimal."""
        rule = PricingRule.objects.create(
            **self.get_valid_pricing_rule_data()
        )

        assert isinstance(rule.making_fee_value, Decimal)
        assert isinstance(rule.profit_value, Decimal)
        assert isinstance(rule.tax_rate, Decimal)
        assert isinstance(rule.other_charge, Decimal)

    def test_zero_values_are_allowed(self):
        """Zero values should be allowed for optional pricing components."""
        data = self.get_valid_pricing_rule_data()

        data["making_fee_value"] = Decimal("0.0000")
        data["profit_value"] = Decimal("0.0000")
        data["tax_rate"] = Decimal("0.0000")
        data["other_charge"] = Decimal("0.00")

        rule = PricingRule(**data)

        rule.full_clean()

    def test_negative_making_fee_is_rejected(self):
        """Negative making fees should fail validation."""
        data = self.get_valid_pricing_rule_data()
        data["making_fee_value"] = Decimal("-1.0000")

        rule = PricingRule(**data)

        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_negative_profit_is_rejected(self):
        """Negative profit values should fail validation."""
        data = self.get_valid_pricing_rule_data()
        data["profit_value"] = Decimal("-1.0000")

        rule = PricingRule(**data)

        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_negative_tax_is_rejected(self):
        """Negative tax rates should fail validation."""
        data = self.get_valid_pricing_rule_data()
        data["tax_rate"] = Decimal("-1.0000")

        rule = PricingRule(**data)

        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_negative_other_charge_is_rejected(self):
        """Negative additional charges should fail validation."""
        data = self.get_valid_pricing_rule_data()
        data["other_charge"] = Decimal("-1.0000")

        rule = PricingRule(**data)

        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_string_representation(self):
        """Pricing rule should have a useful string representation."""
        rule = PricingRule.objects.create(
            **self.get_valid_pricing_rule_data()
        )

        assert str(rule) == "Default Gold Pricing"

    def test_created_at_is_set(self):
        """created_at should be populated automatically."""
        rule = PricingRule.objects.create(
            **self.get_valid_pricing_rule_data()
        )

        assert rule.created_at is not None

    def test_updated_at_is_set(self):
        """updated_at should be populated automatically."""
        rule = PricingRule.objects.create(
            **self.get_valid_pricing_rule_data()
        )

        assert rule.updated_at is not None