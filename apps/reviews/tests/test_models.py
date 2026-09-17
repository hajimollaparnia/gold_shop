import pytest
from django.db import IntegrityError

from apps.reviews.models import Review


@pytest.mark.django_db
def test_review_can_be_created(user, product):
    review = Review.objects.create(
        user=user,
        product=product,
        rating=5,
        title="Excellent",
        comment="Very good quality.",
    )

    assert review.user == user
    assert review.product == product
    assert review.rating == 5
    assert review.status == Review.Status.PENDING


@pytest.mark.django_db
def test_review_can_reference_variant(
    user,
    product,
    variant,
):
    review = Review.objects.create(
        user=user,
        product=product,
        variant=variant,
        rating=4,
    )

    assert review.variant == variant


@pytest.mark.django_db
def test_user_can_have_only_one_review_for_product(
    user,
    product,
):
    Review.objects.create(
        user=user,
        product=product,
        rating=5,
    )

    with pytest.raises(IntegrityError):
        Review.objects.create(
            user=user,
            product=product,
            rating=4,
        )


@pytest.mark.django_db
def test_same_user_can_review_different_products(
    user,
    product,
    second_product,
):
    first_review = Review.objects.create(
        user=user,
        product=product,
        rating=5,
    )

    second_review = Review.objects.create(
        user=user,
        product=second_product,
        rating=4,
    )

    assert first_review.pk != second_review.pk


@pytest.mark.django_db
def test_review_default_status_is_pending(user, product):
    review = Review.objects.create(
        user=user,
        product=product,
        rating=5,
    )

    assert review.status == Review.Status.PENDING