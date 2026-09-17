from django.contrib import admin

from .models import Wishlist, WishlistItem


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin configuration for user wishlists."""

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


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin configuration for wishlist items."""

    list_display = (
        "id",
        "wishlist",
        "product",
        "variant",
        "created_at",
    )

    search_fields = (
        "wishlist__user__phone_number",
        "product__name",
        "product__sku",
    )

    list_filter = (
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )