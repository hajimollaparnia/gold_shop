from django.contrib import admin

from .models import Payment, PaymentLog, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Administrative interface for payment records."""

    list_display = (
        "id",
        "order",
        "amount",
        "gateway",
        "status",
        "verified_at",
        "created_at",
    )

    list_filter = (
        "status",
        "gateway",
        "created_at",
    )

    search_fields = (
        "id",
        "order__id",
        "order__customer_phone",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "verified_at",
    )

    ordering = ("-created_at",)

    list_select_related = (
        "order",
    )

    list_per_page = 50


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    """Administrative interface for immutable payment audit logs."""

    list_display = (
        "id",
        "payment",
        "event",
        "created_at",
    )

    list_filter = (
        "event",
        "created_at",
    )

    search_fields = (
        "payment__id",
        "message",
    )

    readonly_fields = (
        "payment",
        "event",
        "message",
        "metadata",
        "created_at",
    )

    list_select_related = (
        "payment",
    )

    list_per_page = 50

    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs."""
        return False


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Administrative interface for refund records."""

    list_display = (
        "id",
        "payment",
        "amount",
        "status",
        "processed_at",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "payment__id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "processed_at",
    )

    list_select_related = (
        "payment",
    )

    ordering = ("-created_at",)

    list_per_page = 50