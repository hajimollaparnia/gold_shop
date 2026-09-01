from decimal import Decimal

from .results import PricingInput, PricingResult


class PricingService:
    """
    Application service responsible for product price calculation.

    All financial calculations are performed using Decimal.
    """

    def calculate_gold_value(
        self,
        *,
        weight: Decimal,
        gold_price: Decimal,
    ) -> Decimal:
        """
        Calculate the raw gold value.

        Formula:
            weight × gold_price
        """
        if weight < Decimal("0"):
            raise ValueError("weight must not be negative.")

        if gold_price < Decimal("0"):
            raise ValueError("gold_price must not be negative.")

        return weight * gold_price

    def calculate_making_fee(
        self,
        *,
        gold_value: Decimal,
        making_fee_value: Decimal,
        making_fee_type: str,
    ) -> Decimal:
        """
        Calculate the product making fee.

        FIXED:
            making_fee_value is treated as a fixed monetary amount.

        PERCENTAGE:
            gold_value × making_fee_value / 100
        """
        if gold_value < Decimal("0"):
            raise ValueError("gold_value must not be negative.")

        if making_fee_value < Decimal("0"):
            raise ValueError(
                "making_fee_value must not be negative."
            )

        if making_fee_type == "FIXED":
            return making_fee_value

        if making_fee_type == "PERCENTAGE":
            return (
                gold_value
                * making_fee_value
                / Decimal("100")
            )

        raise ValueError("Unsupported making_fee_type.")

    def calculate_profit(
        self,
        *,
        gold_value: Decimal,
        making_fee: Decimal,
        profit_rate: Decimal,
    ) -> Decimal:
        """
        Calculate seller profit.

        Formula:
            (gold_value + making_fee) × profit_rate / 100
        """
        if gold_value < Decimal("0"):
            raise ValueError(
                "gold_value must not be negative."
            )

        if making_fee < Decimal("0"):
            raise ValueError(
                "making_fee must not be negative."
            )

        if profit_rate < Decimal("0"):
            raise ValueError(
                "profit_rate must not be negative."
            )

        profit_base = gold_value + making_fee

        return (
            profit_base
            * profit_rate
            / Decimal("100")
        )

    def calculate_tax(
        self,
        *,
        gold_value: Decimal,
        making_fee: Decimal,
        profit: Decimal,
        tax_rate: Decimal,
    ) -> Decimal:
        """
        Calculate tax based on the taxable amount.

        Formula:
            taxable_base = gold_value + making_fee + profit
            tax = taxable_base × tax_rate / 100
        """
        if gold_value < Decimal("0"):
            raise ValueError(
                "gold_value must not be negative."
            )

        if making_fee < Decimal("0"):
            raise ValueError(
                "making_fee must not be negative."
            )

        if profit < Decimal("0"):
            raise ValueError(
                "profit must not be negative."
            )

        if tax_rate < Decimal("0"):
            raise ValueError(
                "tax_rate must not be negative."
            )

        taxable_base = (
            gold_value
            + making_fee
            + profit
        )

        return (
            taxable_base
            * tax_rate
            / Decimal("100")
        )

    def calculate_discount(
        self,
        *,
        taxable_amount: Decimal,
        discount_value: Decimal,
        discount_type: str,
    ) -> Decimal:
        """
        Calculate product discount.

        FIXED:
            discount_value is treated as a fixed monetary amount.

        PERCENTAGE:
            taxable_amount × discount_value / 100

        A discount can never exceed the taxable amount.
        """
        if taxable_amount < Decimal("0"):
            raise ValueError(
                "taxable_amount must not be negative."
            )

        if discount_value < Decimal("0"):
            raise ValueError(
                "discount_value must not be negative."
            )

        if discount_type == "FIXED":
            if discount_value > taxable_amount:
                raise ValueError(
                    "discount cannot exceed taxable amount."
                )

            return discount_value

        if discount_type == "PERCENTAGE":
            if discount_value > Decimal("100"):
                raise ValueError(
                    "percentage discount cannot exceed 100."
                )

            discount = (
                taxable_amount
                * discount_value
                / Decimal("100")
            )

            return discount

        raise ValueError("Unsupported discount_type.")

    def calculate_price(
        self,
        *,
        pricing_input: PricingInput,
    ) -> PricingResult:
        """
        Calculate the complete final product price.

        Calculation pipeline:

            1. Gold value
            2. Making fee
            3. Profit
            4. Tax
            5. Other charges
            6. Discount
            7. Final price

        All financial calculations use Decimal.
        """

        # 1. Gold value
        gold_value = self.calculate_gold_value(
            weight=pricing_input.weight,
            gold_price=pricing_input.gold_price,
        )

        # 2. Making fee
        making_fee = self.calculate_making_fee(
            gold_value=gold_value,
            making_fee_value=pricing_input.making_fee_value,
            making_fee_type=pricing_input.making_fee_type,
        )

        # 3. Profit
        profit = self.calculate_profit(
            gold_value=gold_value,
            making_fee=making_fee,
            profit_rate=pricing_input.profit_value,
        )

        # 4. Tax
        tax = self.calculate_tax(
            gold_value=gold_value,
            making_fee=making_fee,
            profit=profit,
            tax_rate=pricing_input.tax_rate,
        )

        # 5. Other charges
        if pricing_input.other_charge < Decimal("0"):
            raise ValueError(
                "other_charge must not be negative."
            )

        other_charge = pricing_input.other_charge

        # 6. Discount
        taxable_amount = (
            gold_value
            + making_fee
            + profit
            + tax
            + other_charge
        )

        discount = self.calculate_discount(
            taxable_amount=taxable_amount,
            discount_value=pricing_input.discount_value,
            discount_type=pricing_input.discount_type,
        )

        # 7. Final price
        final_price = (
            taxable_amount
            - discount
        )

        if final_price < Decimal("0"):
            raise ValueError(
                "final_price must not be negative."
            )

        return PricingResult(
            gold_value=gold_value,
            making_fee=making_fee,
            profit=profit,
            tax=tax,
            other_charge=other_charge,
            discount_value=discount,
            discount_type=pricing_input.discount_type,
            final_price=final_price,
        )