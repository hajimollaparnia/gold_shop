import pytest

from apps.reviews.models import Review
from apps.reviews.selectors import ReviewSelector
from apps.reviews.services import ReviewService


@pytest.mark.django_db
def test_get_product_reviews_returns_only_approved_reviews(
    user,
    second_user,
    product,
):
    Review.objects.create(
        user=user,
        product=product,
        rating=5,
        status=Review.Status.APPROVED,
    )

    Review.objects.create(
        user=second_user,
        product=product,
        rating=3,
        status=Review.Status.PENDING,
    )

    reviews = ReviewSelector.get_product_reviews(product.id)

    assert reviews.count() == 1
    assert reviews.first().status == Review.Status.APPROVED


@pytest.mark.django_db
def test_get_product_reviews_returns_empty_when_no_approved_review(
    product,
):
    reviews = ReviewSelector.get_product_reviews(product.id)

    assert reviews.count() == 0


@pytest.mark.django_db
def test_get_user_reviews(user, product, second_product):
    ReviewService.create_review(
        user=user,
        product_id=product.id,
        rating=5,
    )

    ReviewService.create_review(
        user=user,
        product_id=second_product.id,
        rating=4,
    )

    reviews = ReviewSelector.get_user_reviews(user)

    assert reviews.count() == 2


@pytest.mark.django_db
def test_get_review_for_user(user, product):
    review = ReviewService.create_review(
        user=user,
        product_id=product.id,
        rating=5,
    )

    result = ReviewSelector.get_review_for_user(
        user=user,
        review_id=review.id,
    )

    assert result is not None
    assert result.pk == review.pk


@pytest.mark.django_db
def test_get_review_for_user_respects_ownership(
    user,
    second_user,
    product,
):
    review = ReviewService.create_review(
        user=second_user,
        product_id=product.id,
        rating=5,
    )

    result = ReviewSelector.get_review_for_user(
        user=user,
        review_id=review.id,
    )

    assert result is None