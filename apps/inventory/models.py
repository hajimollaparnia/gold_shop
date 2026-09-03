from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from apps.catalog.models import Product, ProductVariant


class InventoryItem(models.Model):
    """
    Represents the current inventory state of a sellable catalog item.

    An inventory item can belong either to a Product directly or to a
    specific ProductVariant. Inventory is intentionally separated from
    the catalog domain so stock management remains independent from
    product metadata and pricing.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="inventory_items",
        blank=True,
        null=True,
        verbose_name="محصول",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="inventory_items",
        blank=True,
        null=True,
        verbose_name="تنوع محصول",
    )

    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی",
    )

    reserved_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی رزرو شده",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "موجودی"
        verbose_name_plural = "موجودی‌ها"
        ordering = ["-updated_at"]

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(product__isnull=False, variant__isnull=True)
                    | Q(product__isnull=True, variant__isnull=False)
                ),
                name="inventory_item_single_target",
            ),
            models.CheckConstraint(
                condition=Q(reserved_quantity__lte=F("quantity")),
                name="inventory_reserved_lte_quantity",
            ),
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(product__isnull=False),
                name="unique_inventory_per_product",
            ),
            models.UniqueConstraint(
                fields=["variant"],
                condition=Q(variant__isnull=False),
                name="unique_inventory_per_variant",
            ),
        ]

        indexes = [
            models.Index(
                fields=["product", "is_active"],
                name="inventory_product_active_idx",
            ),
            models.Index(
                fields=["variant", "is_active"],
                name="inventory_variant_active_idx",
            ),
        ]

    def __str__(self):
        """Return a readable inventory identifier."""

        if self.variant_id:
            return f"{self.variant} - موجودی"

        return f"{self.product} - موجودی"

    @property
    def available_quantity(self):
        """
        Return the quantity currently available for purchase.

        Reserved units cannot be sold again until the reservation is
        released or converted into a completed sale.
        """

        return self.quantity - self.reserved_quantity


class StockMovement(models.Model):
    """
    Represents an immutable inventory movement.

    Every stock change should be recorded as a movement so inventory
    history remains auditable and traceable.
    """

    class MovementType(models.TextChoices):
        IN = "IN", "ورود"
        OUT = "OUT", "خروج"
        ADJUSTMENT = "ADJUSTMENT", "اصلاح موجودی"

    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name="موجودی",
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        verbose_name="نوع حرکت",
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="تعداد",
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="مرجع",
    )

    note = models.TextField(
        blank=True,
        verbose_name="یادداشت",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "حرکت موجودی"
        verbose_name_plural = "حرکت‌های موجودی"
        ordering = ["-created_at", "-id"]

        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="stock_movement_quantity_positive",
            ),
        ]

        indexes = [
            models.Index(
                fields=["inventory_item", "-created_at"],
                name="movement_inventory_created_idx",
            ),
            models.Index(
                fields=["movement_type", "-created_at"],
                name="movement_type_created_idx",
            ),
        ]
    def __str__(self):
        """Return a readable stock movement representation."""

        return (
            f"{self.inventory_item} - "
            f"{self.get_movement_type_display()} - "
            f"{self.quantity}"
        )