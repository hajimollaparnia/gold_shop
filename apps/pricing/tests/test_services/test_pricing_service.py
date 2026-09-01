from decimal import Decimal

import pytest

from apps.pricing.services.pricing_service import PricingService

from apps.pricing.services.results import PricingInput, PricingResult

class TestPricingService:

    @pytest.fixture
    def service(self):
        return PricingService()

    def test_calculate_gold_value(self, service):
        """
        Raw gold value should equal weight multiplied by market price.
        """
        result = service.calculate_gold_value(
            weight=Decimal("2.500"),
            gold_price=Decimal("70000000.00"),
        )

        assert result == Decimal("175000000.000")

    def test_calculate_gold_value_preserves_decimal_precision(self, service):
        """
        Financial calculations must preserve Decimal precision.
        """
        result = service.calculate_gold_value(
            weight=Decimal("1.250"),
            gold_price=Decimal("69500000.00"),
        )

        assert isinstance(result, Decimal)
        assert result == Decimal("86875000.000")

    def test_negative_weight_is_rejected(self, service):
        """
        Negative product weight must be rejected.
        """
        with pytest.raises(ValueError, match="weight"):
            service.calculate_gold_value(
                weight=Decimal("-1.000"),
                gold_price=Decimal("70000000.00"),
            )

    def test_negative_gold_price_is_rejected(self, service):
        """
        Negative market price must be rejected.
        """
        with pytest.raises(ValueError, match="gold_price"):
            service.calculate_gold_value(
                weight=Decimal("2.500"),
                gold_price=Decimal("-70000000.00"),
            )

    def test_zero_weight_is_allowed(self, service):
        """
        Zero weight is mathematically valid at this low-level calculation layer.
        """
        result = service.calculate_gold_value(
            weight=Decimal("0.000"),
            gold_price=Decimal("70000000.00"),
        )

        assert result == Decimal("0.000")

    def test_zero_gold_price_is_allowed(self, service):
        """
        Zero market price is mathematically valid at this low-level layer.
        """
        result = service.calculate_gold_value(
            weight=Decimal("2.500"),
            gold_price=Decimal("0.00"),
        )

        assert result == Decimal("0.000")

    def test_calculate_fixed_making_fee(self, service):
        result = service.calculate_making_fee(
            gold_value=Decimal("175000000.00"),
            making_fee_value=Decimal("1500000.00"),
            making_fee_type="FIXED",
        )

        assert result == Decimal("1500000.00")

    def test_calculate_percentage_making_fee(self, service):
        result = service.calculate_making_fee(
            gold_value=Decimal("175000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
        )

        assert result == Decimal("17500000.0000")

    def test_zero_fixed_making_fee_is_allowed(self, service):
        result = service.calculate_making_fee(
            gold_value=Decimal("175000000.00"),
            making_fee_value=Decimal("0.00"),
            making_fee_type="FIXED",
        )

        assert result == Decimal("0.00")

    def test_zero_percentage_making_fee_is_allowed(self, service):
        result = service.calculate_making_fee(
            gold_value=Decimal("175000000.00"),
            making_fee_value=Decimal("0.00"),
            making_fee_type="PERCENTAGE",
        )

        assert result == Decimal("0.0000")

    def test_negative_gold_value_is_rejected(self, service):
        with pytest.raises(ValueError, match="gold_value"):
            service.calculate_making_fee(
                gold_value=Decimal("-1.00"),
                making_fee_value=Decimal("10.00"),
                making_fee_type="PERCENTAGE",
            )

    def test_negative_making_fee_is_rejected(self, service):
        with pytest.raises(ValueError, match="making_fee_value"):
            service.calculate_making_fee(
                gold_value=Decimal("175000000.00"),
                making_fee_value=Decimal("-10.00"),
                making_fee_type="PERCENTAGE",
            )

    def test_invalid_making_fee_type_is_rejected(self, service):
        with pytest.raises(ValueError, match="Unsupported"):
            service.calculate_making_fee(
                gold_value=Decimal("175000000.00"),
                making_fee_value=Decimal("10.00"),
                making_fee_type="INVALID",
            )
    def test_calculate_profit(self, service):
        result = service.calculate_profit(
            gold_value=Decimal("175000000.00"),
            making_fee=Decimal("17500000.00"),
            profit_rate=Decimal("7.00"),
        )

        assert result == Decimal("13475000.0000")

    def test_profit_is_based_on_gold_value_plus_making_fee(self, service):
        result = service.calculate_profit(
            gold_value=Decimal("100000000.00"),
            making_fee=Decimal("10000000.00"),
            profit_rate=Decimal("10.00"),
        )

        assert result == Decimal("11000000.0000")

    def test_zero_profit_is_allowed(self, service):
        result = service.calculate_profit(
            gold_value=Decimal("175000000.00"),
            making_fee=Decimal("17500000.00"),
            profit_rate=Decimal("0.00"),
        )

        assert result == Decimal("0.0000")

    def test_negative_gold_value_is_rejected_for_profit(self, service):
        with pytest.raises(ValueError, match="gold_value"):
            service.calculate_profit(
                gold_value=Decimal("-1.00"),
                making_fee=Decimal("1000.00"),
                profit_rate=Decimal("7.00"),
            )

    def test_negative_making_fee_is_rejected_for_profit(self, service):
        with pytest.raises(ValueError, match="making_fee"):
            service.calculate_profit(
                gold_value=Decimal("175000000.00"),
                making_fee=Decimal("-1.00"),
                profit_rate=Decimal("7.00"),
            )

    def test_negative_profit_rate_is_rejected(self, service):
        with pytest.raises(ValueError, match="profit_rate"):
            service.calculate_profit(
                gold_value=Decimal("175000000.00"),
                making_fee=Decimal("17500000.00"),
                profit_rate=Decimal("-7.00"),
            )

    def test_calculate_tax(self, service):
        result = service.calculate_tax(
            gold_value=Decimal("175000000.00"),
            making_fee=Decimal("17500000.00"),
            profit=Decimal("13475000.00"),
            tax_rate=Decimal("10.00"),
        )

        assert result == Decimal("20597500.0000")

    def test_tax_is_calculated_from_taxable_base(self, service):
        result = service.calculate_tax(
            gold_value=Decimal("100000000.00"),
            making_fee=Decimal("10000000.00"),
            profit=Decimal("11000000.00"),
            tax_rate=Decimal("10.00"),
        )

        assert result == Decimal("12100000.0000")

    def test_zero_tax_is_allowed(self, service):
        result = service.calculate_tax(
            gold_value=Decimal("175000000.00"),
            making_fee=Decimal("17500000.00"),
            profit=Decimal("13475000.00"),
            tax_rate=Decimal("0.00"),
        )

        assert result == Decimal("0.0000")

    def test_negative_gold_value_is_rejected_for_tax(self, service):
        with pytest.raises(ValueError, match="gold_value"):
            service.calculate_tax(
                gold_value=Decimal("-1.00"),
                making_fee=Decimal("1000.00"),
                profit=Decimal("5000.00"),
                tax_rate=Decimal("10.00"),
            )

    def test_negative_making_fee_is_rejected_for_tax(self, service):
        with pytest.raises(ValueError, match="making_fee"):
            service.calculate_tax(
                gold_value=Decimal("175000000.00"),
                making_fee=Decimal("-1.00"),
                profit=Decimal("5000.00"),
                tax_rate=Decimal("10.00"),
            )

    def test_negative_profit_is_rejected_for_tax(self, service):
        with pytest.raises(ValueError, match="profit"):
            service.calculate_tax(
                gold_value=Decimal("175000000.00"),
                making_fee=Decimal("17500000.00"),
                profit=Decimal("-1.00"),
                tax_rate=Decimal("10.00"),
            )

    def test_negative_tax_rate_is_rejected(self, service):
        with pytest.raises(ValueError, match="tax_rate"):
            service.calculate_tax(
                gold_value=Decimal("175000000.00"),
                making_fee=Decimal("17500000.00"),
                profit=Decimal("13475000.00"),
                tax_rate=Decimal("-10.00"),
            )
    def test_calculate_price_returns_pricing_result(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("500000.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert isinstance(result, PricingResult)

    def test_calculate_price_calculates_gold_value(self, service):
        pricing_input = PricingInput(
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

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert result.gold_value == Decimal("175000000.000")

    def test_calculate_price_calculates_making_fee(self, service):
        pricing_input = PricingInput(
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

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert result.making_fee == Decimal("17500000.000")

    def test_calculate_price_calculates_profit(self, service):
        pricing_input = PricingInput(
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

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        expected_profit = (
            Decimal("175000000.000")
            + Decimal("17500000.000")
        ) * Decimal("7.00") / Decimal("100")

        assert result.profit == expected_profit

    def test_calculate_price_calculates_tax(self, service):
        pricing_input = PricingInput(
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

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        gold_value = Decimal("175000000.000")
        making_fee = Decimal("17500000.000")
        profit = (
            gold_value + making_fee
        ) * Decimal("7.00") / Decimal("100")

        expected_tax = (
            gold_value
            + making_fee
            + profit
        ) * Decimal("10.00") / Decimal("100")

        assert result.tax == expected_tax

    def test_calculate_price_includes_other_charge(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("500000.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert result.other_charge == Decimal("500000.00")

    def test_calculate_price_applies_fixed_discount(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("5000000.00"),
            discount_type="FIXED",
        )

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert result.discount_value == Decimal("5000000.00")

    def test_calculate_price_applies_percentage_discount(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("10.00"),
            discount_type="PERCENTAGE",
        )

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        expected_discount = (
            result.gold_value
            + result.making_fee
            + result.profit
            + result.tax
        ) * Decimal("10.00") / Decimal("100")

        assert result.discount_value == expected_discount

    def test_calculate_price_calculates_final_price(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("500000.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        expected_final_price = (
            result.gold_value
            + result.making_fee
            + result.profit
            + result.tax
            + result.other_charge
            - result.discount_value
        )

        assert result.final_price == expected_final_price

    def test_calculate_price_with_zero_values(self, service):
        pricing_input = PricingInput(
            weight=Decimal("0.000"),
            purity=Decimal("750"),
            gold_price=Decimal("0.00"),
            making_fee_value=Decimal("0.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("0.00"),
            tax_rate=Decimal("0.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert result.gold_value == Decimal("0")
        assert result.making_fee == Decimal("0")
        assert result.profit == Decimal("0")
        assert result.tax == Decimal("0")
        assert result.other_charge == Decimal("0")
        assert result.discount_value == Decimal("0")
        assert result.final_price == Decimal("0")

    def test_calculate_price_rejects_negative_weight(self, service):
        pricing_input = PricingInput(
            weight=Decimal("-1.000"),
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

        with pytest.raises(ValueError):
            service.calculate_price(
                pricing_input=pricing_input,
            )

    def test_calculate_price_rejects_negative_gold_price(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("-70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        with pytest.raises(ValueError):
            service.calculate_price(
                pricing_input=pricing_input,
            )

    def test_calculate_price_rejects_negative_other_charge(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("-1.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        with pytest.raises(ValueError):
            service.calculate_price(
                pricing_input=pricing_input,
            )

    def test_calculate_price_preserves_decimal_precision(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.375"),
            purity=Decimal("750"),
            gold_price=Decimal("70123456.789"),
            making_fee_value=Decimal("8.75"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("6.25"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("123.45"),
            discount_value=Decimal("250.55"),
            discount_type="FIXED",
        )

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert isinstance(result.final_price, Decimal)

    def test_calculate_price_does_not_mutate_input(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("10.00"),
            making_fee_type="PERCENTAGE",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("5000000.00"),
            discount_type="FIXED",
        )

        original = pricing_input

        service.calculate_price(
            pricing_input=pricing_input,
        )

        assert pricing_input == original

    def test_calculate_price_uses_percentage_making_fee(self, service):
        pricing_input = PricingInput(
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

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert result.making_fee == Decimal("17500000.000")

    def test_calculate_price_uses_fixed_making_fee(self, service):
        pricing_input = PricingInput(
            weight=Decimal("2.500"),
            purity=Decimal("750"),
            gold_price=Decimal("70000000.00"),
            making_fee_value=Decimal("5000000.00"),
            making_fee_type="FIXED",
            profit_value=Decimal("7.00"),
            tax_rate=Decimal("10.00"),
            other_charge=Decimal("0.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        result = service.calculate_price(
            pricing_input=pricing_input,
        )

        assert result.making_fee == Decimal("5000000.00")