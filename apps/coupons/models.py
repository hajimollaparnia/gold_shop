from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q


class Coupon(models.Model):
    """
    Represents a discount coupon that can be applied to an order.

    A coupon supports either a fixed discount amount or a percentage-based
    discount and may include expiration, usage, and minimum-order rules.
    """

    class DiscountType(models.TextChoices):
        """Supported coupon discount types."""

        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed"

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
    )

    discount_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )

    minimum_order_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal("0"),
        validators=[
            MinValueValidator(Decimal("0")),
        ],
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this coupon can be used.",
    )

    usage_count = models.PositiveIntegerField(
        default=0,
    )

    per_user_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times one user can use this coupon.",
    )

    starts_at = models.DateTimeField()

    expires_at = models.DateTimeField()

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=Q(discount_value__gt=0),
                name="coupon_discount_value_positive",
            ),
            models.CheckConstraint(
                condition=Q(minimum_order_amount__gte=0),
                name="coupon_minimum_order_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(usage_limit__isnull=True)
                | Q(usage_limit__gt=0),
                name="coupon_usage_limit_positive",
            ),
            models.CheckConstraint(
                condition=Q(per_user_limit__isnull=True)
                | Q(per_user_limit__gt=0),
                name="coupon_per_user_limit_positive",
            ),
            models.CheckConstraint(
                condition=Q(expires_at__gt=models.F("starts_at")),
                name="coupon_expiration_after_start",
            ),
        ]

    def __str__(self):
        return self.code


class CouponUsage(models.Model):
    """
    Records each successful coupon usage by a user.

    Keeping usage history separately allows the system to enforce
    per-user limits and maintain an auditable discount history.
    """

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.PROTECT,
        related_name="usages",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="coupon_usages",
    )

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="coupon_usage",
    )

    discount_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
    )

    used_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-used_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["coupon", "order"],
                name="unique_coupon_order_usage",
            ),
        ]

    def __str__(self):
        return f"{self.coupon.code} - {self.user}"