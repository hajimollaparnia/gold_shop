from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import Product, ProductVariant
from apps.pricing.models import PriceSnapshot


class OrderStatus(models.TextChoices):
    """Defines the lifecycle states of an order."""

    PENDING = "pending", "در انتظار"
    CONFIRMED = "confirmed", "تایید شده"
    PROCESSING = "processing", "در حال پردازش"
    SHIPPED = "shipped", "ارسال شده"
    DELIVERED = "delivered", "تحویل شده"
    CANCELLED = "cancelled", "لغو شده"


class PaymentStatus(models.TextChoices):
    """Defines the payment state of an order."""

    PENDING = "pending", "در انتظار پرداخت"
    PAID = "paid", "پرداخت شده"
    FAILED = "failed", "ناموفق"
    REFUNDED = "refunded", "بازپرداخت شده"


class Currency(models.TextChoices):
    """Supported currencies for order monetary values."""

    IRR = "IRR", "ریال ایران"


class Order(models.Model):
    """
    Represents a customer order.

    The order stores a historical financial snapshot so that changes
    in product prices, user information, or market prices do not
    modify an existing order.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر",
    )

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت سفارش",
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت پرداخت",
    )

    # Customer information is snapshotted at order creation time.
    customer_name = models.CharField(
        max_length=200,
        verbose_name="نام مشتری",
    )

    customer_phone = models.CharField(
        max_length=11,
        verbose_name="شماره تماس",
    )

    # Shipping address is stored as a snapshot of the address
    # used for this specific order.
    shipping_address = models.TextField(
        verbose_name="آدرس ارسال",
    )

    # Financial values are stored using Decimal for accuracy.
    subtotal = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        verbose_name="جمع جزء",
    )

    discount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        verbose_name="تخفیف",
    )

    shipping_cost = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        verbose_name="هزینه ارسال",
    )

    tax = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        verbose_name="مالیات",
    )

    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        default=Decimal("0"),
        verbose_name="مبلغ نهایی",
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.IRR,
        verbose_name="واحد پول",
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
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "-created_at"],
                name="order_user_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="order_status_created_idx",
            ),
            models.Index(
                fields=["payment_status", "-created_at"],
                name="order_payment_created_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0),
                name="order_subtotal_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(discount__gte=0),
                name="order_discount_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(shipping_cost__gte=0),
                name="order_shipping_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(tax__gte=0),
                name="order_tax_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(total_amount__gte=0),
                name="order_total_non_negative",
            ),
        ]

    def __str__(self):
        """Return a readable order identifier."""

        return f"Order #{self.pk}"


class OrderItem(models.Model):
    """
    Represents a single product line inside an order.

    Product and pricing information is snapshotted so historical
    order data remains stable after catalog or pricing changes.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="محصول",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items",
        blank=True,
        null=True,
        verbose_name="تنوع محصول",
    )

    # Product identity snapshot.
    product_name_snapshot = models.CharField(
        max_length=255,
        verbose_name="نام محصول در زمان سفارش",
    )

    sku_snapshot = models.CharField(
        max_length=80,
        verbose_name="SKU در زمان سفارش",
    )

    # Physical product snapshot.
    weight_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal("0.0001")),
        ],
        verbose_name="وزن در زمان سفارش",
    )

    purity_snapshot = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="عیار در زمان سفارش",
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="تعداد",
    )

    # Unit price is frozen at the time the order is created.
    unit_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        verbose_name="قیمت واحد",
    )

    total_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
        verbose_name="قیمت کل",
    )

    # Stores the complete pricing calculation used for this item.
    price_snapshot = models.ForeignKey(
        PriceSnapshot,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="اسنپ‌شات قیمت",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"
        ordering = ["id"]

        indexes = [
            models.Index(
                fields=["order", "product"],
                name="orderitem_order_product_idx",
            ),
            models.Index(
                fields=["product"],
                name="orderitem_product_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="orderitem_quantity_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="orderitem_unit_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(total_price__gte=0),
                name="orderitem_total_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(weight_snapshot__gt=0),
                name="orderitem_weight_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(purity_snapshot__gt=0),
                name="orderitem_purity_positive",
            ),
        ]

    def __str__(self):
        """Return a readable representation of the order item."""

        return f"{self.product_name_snapshot} × {self.quantity}"