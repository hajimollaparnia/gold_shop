from decimal import Decimal

import pytest

from apps.pricing.services.pricing_service import PricingService


class TestPricingServiceDiscount:

    def setup_method(self):
        self.service = PricingService()

    def test_calculate_fixed_discount(self):
        discount = self.service.calculate_discount(
            taxable_amount=Decimal("200000000.00"),
            discount_value=Decimal("5000000.00"),
            discount_type="FIXED",
        )

        assert discount == Decimal("5000000.00")

    def test_calculate_percentage_discount(self):
        discount = self.service.calculate_discount(
            taxable_amount=Decimal("200000000.00"),
            discount_value=Decimal("10.00"),
            discount_type="PERCENTAGE",
        )

        assert discount == Decimal("20000000.00")

    def test_zero_fixed_discount_is_allowed(self):
        discount = self.service.calculate_discount(
            taxable_amount=Decimal("200000000.00"),
            discount_value=Decimal("0.00"),
            discount_type="FIXED",
        )

        assert discount == Decimal("0.00")

    def test_zero_percentage_discount_is_allowed(self):
        discount = self.service.calculate_discount(
            taxable_amount=Decimal("200000000.00"),
            discount_value=Decimal("0.00"),
            discount_type="PERCENTAGE",
        )

        assert discount == Decimal("0.00")

    def test_negative_taxable_amount_is_rejected(self):
        with pytest.raises(ValueError):
            self.service.calculate_discount(
                taxable_amount=Decimal("-1.00"),
                discount_value=Decimal("10.00"),
                discount_type="PERCENTAGE",
            )

    def test_negative_discount_value_is_rejected(self):
        with pytest.raises(ValueError):
            self.service.calculate_discount(
                taxable_amount=Decimal("200000000.00"),
                discount_value=Decimal("-10.00"),
                discount_type="PERCENTAGE",
            )

    def test_invalid_discount_type_is_rejected(self):
        with pytest.raises(ValueError):
            self.service.calculate_discount(
                taxable_amount=Decimal("200000000.00"),
                discount_value=Decimal("10.00"),
                discount_type="INVALID",
            )

    def test_discount_cannot_exceed_taxable_amount(self):
        with pytest.raises(ValueError):
            self.service.calculate_discount(
                taxable_amount=Decimal("1000000.00"),
                discount_value=Decimal("2000000.00"),
                discount_type="FIXED",
            )

    def test_percentage_discount_cannot_exceed_100(self):
        with pytest.raises(ValueError):
            self.service.calculate_discount(
                taxable_amount=Decimal("200000000.00"),
                discount_value=Decimal("101.00"),
                discount_type="PERCENTAGE",
            )