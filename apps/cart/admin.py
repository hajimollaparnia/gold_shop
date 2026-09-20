from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Display cart items directly inside the cart administration page."""

    model = CartItem
    extra = 0

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Administrative interface for active shopping carts."""

    list_display = (
        "id",
        "user",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__phone_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
    )

    ordering = (
        "-updated_at",
    )

    list_per_page = 50

    inlines = (
        CartItemInline,
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Administrative interface for shopping cart items."""

    list_display = (
        "id",
        "cart",
        "product",
        "variant",
        "quantity",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "cart__user__phone_number",
        "product__name",
        "product__sku",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "cart",
        "product",
        "variant",
    )

    ordering = (
        "-updated_at",
    )

    list_per_page = 50