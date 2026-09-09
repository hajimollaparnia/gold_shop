from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Display order items directly inside the order administration page.
    """

    model = OrderItem
    extra = 0

    # Order item data is historical and should not be modified casually
    # after the order has been created.
    readonly_fields = (
        "product_name_snapshot",
        "sku_snapshot",
        "weight_snapshot",
        "purity_snapshot",
        "unit_price",
        "total_price",
        "price_snapshot",
        "created_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Administrative interface for customer orders.
    """

    list_display = (
        "id",
        "user",
        "status",
        "payment_status",
        "total_amount",
        "currency",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "currency",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "customer_phone",
        "user__phone_number",
    )

    readonly_fields = (
        "subtotal",
        "total_amount",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    inlines = [
        OrderItemInline,
    ]