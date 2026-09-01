from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class MarketAsset(models.TextChoices):
    """
    Supported market assets.

    The pricing engine is intentionally designed around an asset concept
    instead of being hard-coded to gold only. This allows us to support
    silver and coins in the future without redesigning the pricing domain.
    """

    GOLD = "gold", "Gold"
    SILVER = "silver", "Silver"
    COIN = "coin", "Coin"


class PriceProvider(models.TextChoices):
    """
    Identifies the system/provider that supplied the market price.

    External API integrations will be implemented later through the
    providers package. The model only stores the provider identity.
    """

    MANUAL = "manual", "Manual"
    EXTERNAL_API = "external_api", "External API"


class Currency(models.TextChoices):
    """
    Supported currencies.

    IRR is the primary currency for the Iranian gold shop.
    """

    IRR = "IRR", "Iranian Rial"


class ChargeType(models.TextChoices):
    """
    Defines how a pricing charge is calculated.

    PERCENTAGE:
        The charge is calculated as a percentage of its configured base.

    FIXED:
        A fixed monetary amount is added.
    """

    PERCENTAGE = "percentage", "Percentage"
    FIXED = "fixed", "Fixed"


class DiscountType(models.TextChoices):
    """
    Defines how a discount is calculated.
    """

    PERCENTAGE = "percentage", "Percentage"
    FIXED = "fixed", "Fixed"


class MarketPrice(models.Model):
    """
    Stores a historical market price.

    Each record represents the market price of an asset at a specific
    point in time.

    Historical records are never overwritten. New market prices should
    create new records so that previous prices remain available for
    auditing and order price snapshots.
    """

    asset = models.CharField(
        max_length=20,
        choices=MarketAsset.choices,
        db_index=True,
        help_text="Market asset such as gold, silver, or coin.",
    )

    purity = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
        ],
        help_text=(
            "Purity/karat of the asset when applicable. "
            "For example, 18 or 24 for gold."
        ),
    )

    buy_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Market purchase price.",
    )

    sell_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Market selling price.",
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.IRR,
        help_text="Currency of the market prices.",
    )

    provider = models.CharField(
        max_length=30,
        choices=PriceProvider.choices,
        default=PriceProvider.MANUAL,
        db_index=True,
        help_text="Provider that supplied this market price.",
    )

    source = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=(
            "Human-readable source information. "
            "For example, an API name or administrative source."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this market price is currently active.",
    )

    effective_at = models.DateTimeField(
        db_index=True,
        help_text="The exact time at which this market price became effective.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-effective_at", "-id"]

        indexes = [
            models.Index(
                fields=["asset", "purity", "-effective_at"],
                name="pricing_market_asset_time_idx",
            ),
            models.Index(
                fields=["asset", "is_active", "-effective_at"],
                name="pricing_market_active_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(buy_price__gte=0),
                name="market_buy_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(sell_price__gte=0),
                name="market_sell_price_non_negative",
            ),
        ]

    def __str__(self):
        purity = f" {self.purity}K" if self.purity else ""
        return (
            f"{self.get_asset_display()}{purity} - "
            f"{self.sell_price} {self.currency}"
        )


class PricingRule(models.Model):
    """
    Stores the configurable rules used by the pricing engine.

    PricingRule does not calculate prices itself.

    It only stores configuration such as:
        - making fee
        - seller profit
        - tax
        - other charges

    Actual calculation belongs to the service/calculator layer.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique human-readable name for this pricing rule.",
    )

    making_fee_type = models.CharField(
        max_length=20,
        choices=ChargeType.choices,
        default=ChargeType.PERCENTAGE,
    )

    making_fee_value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        help_text="Making fee value. Percentage or fixed amount.",
    )

    profit_type = models.CharField(
        max_length=20,
        choices=ChargeType.choices,
        default=ChargeType.PERCENTAGE,
    )

    profit_value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        help_text="Seller profit value. Percentage or fixed amount.",
    )

    tax_rate = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        help_text="Tax rate as a percentage.",
    )

    other_charge = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        help_text="Additional fixed charges.",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    effective_from = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When this pricing rule becomes effective.",
    )

    effective_until = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When this pricing rule stops being effective.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["is_active", "-created_at"],
                name="pricing_rule_active_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(making_fee_value__gte=0),
                name="pricing_rule_making_fee_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(profit_value__gte=0),
                name="pricing_rule_profit_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(tax_rate__gte=0),
                name="pricing_rule_tax_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(other_charge__gte=0),
                name="pricing_rule_other_charge_non_negative",
            ),
        ]

    def __str__(self):
        return self.name


class PriceSnapshot(models.Model):
    """
    Immutable financial snapshot of a product price calculation.

    This model is extremely important for orders.

    Once an order is created, its historical price must not change when
    the market price changes.

    The snapshot therefore stores the complete result of the calculation
    rather than relying on the current market price.
    """

    market_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Market price used during the calculation.",
    )

    weight = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal("0.0001")),
        ],
        help_text="Product weight used for the calculation.",
    )

    purity = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        help_text="Product gold purity/karat at calculation time.",
    )

    gold_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Base gold value before additional charges.",
    )

    making_charge = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Making fee calculated at the time of pricing.",
    )

    profit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Seller profit calculated at the time of pricing.",
    )

    tax = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Tax amount calculated at the time of pricing.",
    )

    other_charges = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        help_text="Other charges included in the final price.",
    )

    discount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        help_text="Discount amount applied to the price.",
    )

    subtotal = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Price before discount.",
    )

    final_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        help_text="Final customer price after all adjustments.",
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.IRR,
    )

    calculated_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Time at which this price snapshot was created.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        ordering = ["-calculated_at", "-id"]

        indexes = [
            models.Index(
                fields=["-calculated_at"],
                name="pricing_snapshot_time_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(market_price__gte=0),
                name="snapshot_market_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(weight__gt=0),
                name="snapshot_weight_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(gold_value__gte=0),
                name="snapshot_gold_value_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(making_charge__gte=0),
                name="snapshot_making_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(profit__gte=0),
                name="snapshot_profit_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(tax__gte=0),
                name="snapshot_tax_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(other_charges__gte=0),
                name="snapshot_other_charges_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(discount__gte=0),
                name="snapshot_discount_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0),
                name="snapshot_subtotal_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(final_price__gte=0),
                name="snapshot_final_price_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.final_price} {self.currency}"