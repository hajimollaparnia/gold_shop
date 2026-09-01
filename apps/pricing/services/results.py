from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PricingInput:
    """
    Immutable input data required by the pricing engine.

    This object contains only pricing-related data and remains
    independent from Catalog, Cart, Order, and other domains.
    """

    # Product weight in grams.
    weight: Decimal

    # Gold purity / karat value.
    purity: Decimal

    # Current gold market price per gram.
    gold_price: Decimal

    # Making fee amount or percentage.
    making_fee_value: Decimal

    # Making fee calculation type.
    making_fee_type: str

    # Seller profit rate.
    profit_value: Decimal

    # Tax percentage.
    tax_rate: Decimal

    # Additional charges.
    other_charge: Decimal

    # Discount amount or percentage.
    discount_value: Decimal

    # Discount calculation type.
    discount_type: str


@dataclass(frozen=True, slots=True)
class PricingResult:
    """
    Immutable result produced by the pricing engine.

    All monetary values are represented using Decimal.
    """

    # Raw gold value.
    gold_value: Decimal

    # Calculated making fee.
    making_fee: Decimal

    # Calculated seller profit.
    profit: Decimal

    # Calculated tax.
    tax: Decimal

    # Additional charges.
    other_charge: Decimal

    # Calculated discount.
    discount_value: Decimal

    # Discount calculation type.
    discount_type: str

    # Final customer-facing price.
    final_price: Decimal