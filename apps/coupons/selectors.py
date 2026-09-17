from django.db.models import Count

from .models import Coupon, CouponUsage


class CouponSelector:
    """Provides optimized read-only queries for the coupon domain."""

    @staticmethod
    def get_by_code(code):
        """
        Return a coupon by its normalized code.

        The query is intentionally read-only and does not apply business
        validation rules. Validation belongs to the service layer.
        """

        return Coupon.objects.filter(
            code=code.upper(),
        ).first()

    @staticmethod
    def get_usage_count_for_user(coupon, user):
        """Return the number of times a user has used a coupon."""

        return CouponUsage.objects.filter(
            coupon=coupon,
            user=user,
        ).count()

    @staticmethod
    def get_coupon_with_usage_count(code):
        """
        Return a coupon with its total usage count loaded efficiently.
        """

        return (
            Coupon.objects
            .filter(code=code.upper())
            .annotate(
                total_usage_count=Count("usages"),
            )
            .first()
        )