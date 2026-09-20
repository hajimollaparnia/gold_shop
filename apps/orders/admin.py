from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Display immutable order items inside the order administration page.

    Order item data represents historical snapshots captured at checkout
    and must not be modified manually through the admin interface.
    """

    model = OrderItem
    extra = 0
    can_delete = False

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

    Provides operational visibility into order status, payment status,
    financial totals, customer information, and historical order items.
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

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "user",
    )

    inlines = (
        OrderItemInline,
    )

    list_per_page = 50