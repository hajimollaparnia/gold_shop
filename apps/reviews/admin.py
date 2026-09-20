from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Administrative interface for product reviews."""

    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "status",
        "title",
        "created_at",
    )

    list_filter = (
        "status",
        "rating",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "user__phone_number",
        "title",
        "comment",
    )

    readonly_fields = (
        "user",
        "product",
        "variant",
        "rating",
        "title",
        "comment",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
        "product",
        "variant",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    actions = (
        "approve_reviews",
        "reject_reviews",
    )

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        """Approve selected reviews."""
        queryset.update(status=Review.Status.APPROVED)

    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):
        """Reject selected reviews."""
        queryset.update(status=Review.Status.REJECTED)