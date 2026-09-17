import pytest

from apps.reviews.exceptions import (
    ProductNotFoundError,
    ProductVariantNotFoundError,
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
)
from apps.reviews.models import Review
from apps.reviews.services import ReviewService


@pytest.mark.django_db
def test_create_review(user, product):
    review = ReviewService.create_review(
        user=user,
        product_id=product.id,
        rating=5,
        title="Excellent",
        comment="Very good product.",
    )

    assert review.user == user
    assert review.product == product
    assert review.rating == 5
    assert review.status == Review.Status.PENDING


@pytest.mark.django_db
def test_create_review_with_variant(
    user,
    product,
    variant,
):
    review = ReviewService.create_review(
        user=user,
        product_id=product.id,
        variant_id=variant.id,
        rating=4,
    )

    assert review.variant == variant


@pytest.mark.django_db
def test_create_review_with_nonexistent_product(user):
    with pytest.raises(ProductNotFoundError):
        ReviewService.create_review(
            user=user,
            product_id=999999,
            rating=5,
        )


@pytest.mark.django_db
def test_create_review_with_nonexistent_variant(
    user,
    product,
):
    with pytest.raises(ProductVariantNotFoundError):
        ReviewService.create_review(
            user=user,
            product_id=product.id,
            variant_id=999999,
            rating=5,
        )


@pytest.mark.django_db
def test_variant_must_belong_to_product(
    user,
    product,
    second_product,
    variant,
):
    from apps.catalog.models import ProductVariant

    another_variant = ProductVariant.objects.create(
        product=second_product,
        sku="REV-OTHER-VARIANT",
        weight=10,
    )

    with pytest.raises(ProductVariantNotFoundError):
        ReviewService.create_review(
            user=user,
            product_id=product.id,
            variant_id=another_variant.id,
            rating=5,
        )


@pytest.mark.django_db
def test_duplicate_review_raises_error(
    user,
    product,
):
    ReviewService.create_review(
        user=user,
        product_id=product.id,
        rating=5,
    )

    with pytest.raises(ReviewAlreadyExistsError):
        ReviewService.create_review(
            user=user,
            product_id=product.id,
            rating=4,
        )


@pytest.mark.django_db
def test_delete_review(user, product):
    review = ReviewService.create_review(
        user=user,
        product_id=product.id,
        rating=5,
    )

    ReviewService.delete_review(
        user=user,
        review_id=review.id,
    )

    assert not Review.objects.filter(
        id=review.id,
    ).exists()


@pytest.mark.django_db
def test_delete_nonexistent_review_raises_error(user):
    with pytest.raises(ReviewNotFoundError):
        ReviewService.delete_review(
            user=user,
            review_id=999999,
        )


@pytest.mark.django_db
def test_user_cannot_delete_another_users_review(
    user,
    second_user,
    product,
):
    review = ReviewService.create_review(
        user=second_user,
        product_id=product.id,
        rating=5,
    )

    with pytest.raises(ReviewNotFoundError):
        ReviewService.delete_review(
            user=user,
            review_id=review.id,
        )