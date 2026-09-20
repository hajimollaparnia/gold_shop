from django.contrib import admin

from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Administrative interface for coupon management."""

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

    ordering = (
        "-created_at",
    )

    list_per_page = 50


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """Administrative interface for immutable coupon usage history."""

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

    list_select_related = (
        "coupon",
        "user",
        "order",
    )

    ordering = (
        "-used_at",
    )

    list_per_page = 50

    def has_add_permission(self, request):
        """Prevent manual creation of coupon usage records."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of coupon usage history."""
        return False