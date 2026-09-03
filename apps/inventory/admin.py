from django.contrib import admin

from .models import InventoryItem, StockMovement


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for inventory items.

    Provides a clear overview of physical, reserved, and available
    inventory while preventing direct modification of calculated data.
    """

    list_display = (
        "id",
        "get_target",
        "quantity",
        "reserved_quantity",
        "available_quantity_display",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "variant__sku",
    )

    readonly_fields = (
        "available_quantity_display",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "product",
        "variant",
    )

    ordering = (
        "-updated_at",
        "-id",
    )

    @admin.display(
        description="آیتم",
        ordering="product__name",
    )
    def get_target(self, obj):
        """Return the product or variant represented by the inventory."""

        if obj.variant_id:
            return f"{obj.variant} - {obj.variant.sku}"

        return f"{obj.product} - {obj.product.sku}"

    @admin.display(
        description="موجودی قابل فروش",
        ordering="quantity",
    )
    def available_quantity_display(self, obj):
        """Display the quantity currently available for sale."""

        return obj.available_quantity


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """
    Admin configuration for stock movements.

    Stock movements represent the audit history of inventory changes
    and should not be modified after creation.
    """

    list_display = (
        "id",
        "inventory_item",
        "movement_type",
        "quantity",
        "reference",
        "created_at",
    )

    list_filter = (
        "movement_type",
        "created_at",
    )

    search_fields = (
        "inventory_item__product__name",
        "inventory_item__product__sku",
        "inventory_item__variant__sku",
        "reference",
        "note",
    )

    readonly_fields = (
        "inventory_item",
        "movement_type",
        "quantity",
        "reference",
        "note",
        "created_at",
    )

    list_select_related = (
        "inventory_item",
        "inventory_item__product",
        "inventory_item__variant",
    )

    ordering = (
        "-created_at",
        "-id",
    )

    def has_add_permission(self, request):
        """
        Prevent manual creation of stock movements from Admin.

        Stock movements must be created through the inventory service
        layer so every stock change follows the business rules.
        """

        return False

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of stock movements from Admin.

        Stock movements are part of the inventory audit trail and
        must remain immutable.
        """

        return False
