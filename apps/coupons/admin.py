from django.contrib import admin

from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin configuration for managing coupons."""

    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "usage_count",
        "usage_limit",
        "is_active",
        "starts_at",
        "expires_at",
    )

    list_filter = (
        "discount_type",
        "is_active",
    )

    search_fields = (
        "code",
    )

    readonly_fields = (
        "usage_count",
        "created_at",
        "updated_at",
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """Admin configuration for coupon usage history."""

    list_display = (
        "coupon",
        "user",
        "order",
        "discount_amount",
        "used_at",
    )

    list_filter = (
        "used_at",
    )

    search_fields = (
        "coupon__code",
        "user__phone_number",
    )

    readonly_fields = (
        "coupon",
        "user",
        "order",
        "discount_amount",
        "used_at",
    )