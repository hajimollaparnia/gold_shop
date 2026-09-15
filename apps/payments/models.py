from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.orders.models import Order


class PaymentStatus(models.TextChoices):
    """Defines the lifecycle states of a payment."""

    PENDING = "pending", "در انتظار بررسی"
    PROCESSING = "processing", "در حال پردازش"
    SUCCESS = "success", "موفق"
    FAILED = "failed", "ناموفق"
    REFUNDED = "refunded", "بازپرداخت شده"


class PaymentGateway(models.TextChoices):
    """Defines the payment gateway used to process a payment."""

    CARD_TO_CARD = "card_to_card", "کارت به کارت"
    ZARINPAL = "zarinpal", "زرین پال"


class PaymentLogEvent(models.TextChoices):
    """Defines auditable events that can occur during a payment lifecycle."""

    CREATED = "created", "ایجاد پرداخت"
    RECEIPT_UPLOADED = "receipt_uploaded", "آپلود فیش"
    PROCESSING = "processing", "شروع پردازش"
    SUCCESS = "success", "پرداخت موفق"
    FAILED = "failed", "پرداخت ناموفق"
    REFUND_REQUESTED = "refund_requested", "درخواست بازپرداخت"
    REFUND_COMPLETED = "refund_completed", "بازپرداخت موفق"
    REFUND_FAILED = "refund_failed", "بازپرداخت ناموفق"


class RefundStatus(models.TextChoices):
    """Defines the lifecycle states of a refund."""

    PENDING = "pending", "در انتظار"
    PROCESSING = "processing", "در حال پردازش"
    SUCCESS = "success", "موفق"
    FAILED = "failed", "ناموفق"


class Payment(models.Model):
    """
    Represents a payment attempt for an order.

    A payment stores the financial and gateway-related state of a
    single payment attempt. Multiple attempts may exist for the same
    order, allowing failed payments to remain part of the audit trail.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="سفارش",
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
        verbose_name="مبلغ پرداخت",
    )

    currency = models.CharField(
        max_length=3,
        choices=Order._meta.get_field("currency").choices,
        default="IRR",
        verbose_name="واحد پول",
    )

    gateway = models.CharField(
        max_length=30,
        choices=PaymentGateway.choices,
        default=PaymentGateway.CARD_TO_CARD,
        db_index=True,
        verbose_name="درگاه پرداخت",
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت پرداخت",
    )

    # Card-to-card payments are verified manually through the uploaded receipt.
    receipt_image = models.ImageField(
        upload_to="payments/receipts/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="تصویر فیش واریزی",
    )

    failure_reason = models.TextField(
        blank=True,
        verbose_name="دلیل شکست پرداخت",
    )

    # Set when the payment is manually or automatically verified successfully.
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="تاریخ تایید پرداخت",
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
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["order", "-created_at"],
                name="payment_order_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="payment_status_created_idx",
            ),
            models.Index(
                fields=["gateway", "status"],
                name="payment_gateway_status_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="payment_amount_positive",
            ),
        ]

    def __str__(self):
        """Return a readable payment identifier."""

        return f"Payment #{self.pk} - Order #{self.order_id}"


class PaymentLog(models.Model):
    """
    Stores an immutable audit trail for payment-related events.

    Payment logs are intended for auditing, debugging, and tracing
    important state transitions without modifying historical records.
    """

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name="پرداخت",
    )

    event = models.CharField(
        max_length=30,
        choices=PaymentLogEvent.choices,
        db_index=True,
        verbose_name="رویداد",
    )

    message = models.TextField(
        blank=True,
        verbose_name="پیام",
    )

    # Stores non-sensitive gateway or processing metadata.
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="اطلاعات تکمیلی",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "لاگ پرداخت"
        verbose_name_plural = "لاگ‌های پرداخت"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["payment", "-created_at"],
                name="paymentlog_payment_created_idx",
            ),
            models.Index(
                fields=["event", "-created_at"],
                name="paymentlog_event_created_idx",
            ),
        ]

    def __str__(self):
        """Return a readable payment log representation."""

        return f"{self.payment} - {self.event}"


class Refund(models.Model):
    """
    Represents a refund request associated with a successful payment.

    The model is intentionally gateway-agnostic so that automated
    refund support can be added when a compatible payment provider
    becomes available.
    """

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
        verbose_name="پرداخت",
    )

    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
        verbose_name="مبلغ بازپرداخت",
    )

    status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت بازپرداخت",
    )

    reason = models.TextField(
        blank=True,
        verbose_name="دلیل بازپرداخت",
    )

    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="تاریخ پردازش",
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
        verbose_name = "بازپرداخت"
        verbose_name_plural = "بازپرداخت‌ها"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["payment", "-created_at"],
                name="refund_payment_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="refund_status_created_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="refund_amount_positive",
            ),
        ]

    def __str__(self):
        """Return a readable refund identifier."""

        return f"Refund #{self.pk} - Payment #{self.payment_id}"