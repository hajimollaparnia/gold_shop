import pytest
from rest_framework.test import APIClient

from apps.reviews.models import Review


@pytest.fixture
def api_client():
    """Return a DRF API client."""

    return APIClient()


@pytest.mark.django_db
def test_create_review(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/reviews/",
        {
            "product_id": product.id,
            "rating": 5,
            "title": "Excellent",
            "comment": "Very good product.",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["product"] == product.id
    assert response.data["rating"] == 5
    assert response.data["status"] == Review.Status.PENDING


@pytest.mark.django_db
def test_create_review_with_variant(
    api_client,
    user,
    product,
    variant,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/reviews/",
        {
            "product_id": product.id,
            "variant_id": variant.id,
            "rating": 4,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["variant"] == variant.id


@pytest.mark.django_db
def test_duplicate_review_returns_400(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    payload = {
        "product_id": product.id,
        "rating": 5,
    }

    first_response = api_client.post(
        "/api/v1/reviews/",
        payload,
        format="json",
    )

    second_response = api_client.post(
        "/api/v1/reviews/",
        payload,
        format="json",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


@pytest.mark.django_db
def test_nonexistent_product_returns_404(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/reviews/",
        {
            "product_id": 999999,
            "rating": 5,
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_invalid_rating_returns_400(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/reviews/",
        {
            "product_id": product.id,
            "rating": 6,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_reviews_require_authentication(api_client):
    response = api_client.post(
        "/api/v1/reviews/",
        {
            "product_id": 1,
            "rating": 5,
        },
        format="json",
    )

    assert response.status_code == 403