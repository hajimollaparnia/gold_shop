from decimal import Decimal

import pytest

from apps.pricing.services.results import PricingInput, PricingResult


class TestPricingInput:

    def test_pricing_input_can_be_created(self):
        data = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        assert data.weight == Decimal("2.500")
        assert data.purity == Decimal("750")
        assert data.gold_price == Decimal("70000000.00")

    def test_pricing_input_is_immutable(self):
        data = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        with pytest.raises(AttributeError):
            data.weight = Decimal("3.000")


class TestPricingResult:

    def test_pricing_result_can_be_created(self):
        result = PricingResult(
            gold_value=Decimal("175000000.00"),
            making_fee=Decimal("17500000.00"),
            profit=Decimal("13475000.00"),
            tax=Decimal("20572500.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
            final_price=Decimal("228297500.00"),
        )

        assert result.gold_value == Decimal("175000000.00")
        assert result.making_fee == Decimal("17500000.00")
        assert result.final_price == Decimal("228297500.00")

    def test_pricing_result_is_immutable(self):
        result = PricingResult(
            gold_value=Decimal("175000000.00"),
            making_fee=Decimal("17500000.00"),
            profit=Decimal("13475000.00"),
            tax=Decimal("20572500.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
            final_price=Decimal("228297500.00"),
        )

        with pytest.raises(AttributeError):
            result.final_price = Decimal("100000000.00")