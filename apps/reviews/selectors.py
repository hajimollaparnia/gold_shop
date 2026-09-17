from .models import Review


class ReviewSelector:
    """Provides optimized read-only queries for product reviews."""

    @staticmethod
    def get_product_reviews(product_id):
        """Return approved reviews for a product."""

        return (
            Review.objects
            .select_related(
                "user",
                "product",
                "variant",
            )
            .filter(
                product_id=product_id,
                status=Review.Status.APPROVED,
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_user_reviews(user):
        """Return all reviews submitted by a user."""

        return (
            Review.objects
            .select_related(
                "product",
                "variant",
            )
            .filter(user=user)
            .order_by("-created_at")
        )

    @staticmethod
    def get_review_for_user(user, review_id):
        """Return a specific review owned by the authenticated user."""

        return (
            Review.objects
            .select_related(
                "product",
                "variant",
            )
            .filter(
                id=review_id,
                user=user,
            )
            .first()
        )