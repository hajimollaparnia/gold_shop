import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Return a DRF API client."""

    return APIClient()


@pytest.mark.django_db
def test_get_wishlist(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/v1/wishlist/",
    )

    assert response.status_code == 200
    assert "items" in response.data


@pytest.mark.django_db
def test_add_product_to_wishlist(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/wishlist/items/",
        {
            "product_id": product.id,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["product"] == product.id
    assert response.data["variant"] is None


@pytest.mark.django_db
def test_add_variant_to_wishlist(
    api_client,
    user,
    product,
    variant,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/wishlist/items/",
        {
            "product_id": product.id,
            "variant_id": variant.id,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["product"] == product.id
    assert response.data["variant"] == variant.id


@pytest.mark.django_db
def test_duplicate_item_returns_400(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    payload = {
        "product_id": product.id,
    }

    first_response = api_client.post(
        "/api/v1/wishlist/items/",
        payload,
        format="json",
    )

    second_response = api_client.post(
        "/api/v1/wishlist/items/",
        payload,
        format="json",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


@pytest.mark.django_db
def test_delete_wishlist_item(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    create_response = api_client.post(
        "/api/v1/wishlist/items/",
        {
            "product_id": product.id,
        },
        format="json",
    )

    item_id = create_response.data["id"]

    response = api_client.delete(
        f"/api/v1/wishlist/items/{item_id}/delete/",
    )

    assert response.status_code == 204


@pytest.mark.django_db
def test_clear_wishlist(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    api_client.post(
        "/api/v1/wishlist/items/",
        {
            "product_id": product.id,
        },
        format="json",
    )

    response = api_client.delete(
        "/api/v1/wishlist/clear/",
    )

    assert response.status_code == 204


@pytest.mark.django_db
def test_wishlist_requires_authentication(api_client):
    response = api_client.get(
        "/api/v1/wishlist/",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_nonexistent_product_returns_404(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/wishlist/items/",
        {
            "product_id": 999999,
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_invalid_variant_returns_404(
    api_client,
    user,
    product,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/wishlist/items/",
        {
            "product_id": product.id,
            "variant_id": 999999,
        },
        format="json",
    )

    assert response.status_code == 404