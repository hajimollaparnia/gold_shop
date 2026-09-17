from django.db import transaction

from apps.catalog.models import Product, ProductVariant

from .exceptions import (
    ProductNotFoundError,
    ProductVariantNotFoundError,
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
)
from .models import Review


class ReviewService:
    """Provides transactional business operations for product reviews."""

    @staticmethod
    @transaction.atomic
    def create_review(
        user,
        product_id,
        rating,
        title="",
        comment="",
        variant_id=None,
    ):
        """Create a review for a product."""

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist as exc:
            raise ProductNotFoundError(
                "The requested product does not exist."
            ) from exc

        variant = None

        if variant_id is not None:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                )
            except ProductVariant.DoesNotExist as exc:
                raise ProductVariantNotFoundError(
                    "The requested product variant does not exist."
                ) from exc

        if Review.objects.filter(
            user=user,
            product=product,
        ).exists():
            raise ReviewAlreadyExistsError(
                "You have already reviewed this product."
            )

        return Review.objects.create(
            user=user,
            product=product,
            variant=variant,
            rating=rating,
            title=title,
            comment=comment,
        )

    @staticmethod
    @transaction.atomic
    def delete_review(user, review_id):
        """Delete a review owned by the authenticated user."""

        try:
            review = Review.objects.get(
                id=review_id,
                user=user,
            )
        except Review.DoesNotExist as exc:
            raise ReviewNotFoundError(
                "The requested review does not exist."
            ) from exc

        review.delete()

    @staticmethod
    def get_review(review_id):
        """Return a review by its identifier."""

        return (
            Review.objects
            .select_related(
                "user",
                "product",
                "variant",
            )
            .filter(id=review_id)
            .first()
        )