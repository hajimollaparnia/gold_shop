import pytest

from apps.accounts.models import User
from apps.catalog.models import Product, ProductVariant


@pytest.mark.django_db
def test_get_cart(authenticated_client):
    response = authenticated_client.get("/api/v1/cart/")

    assert response.status_code == 200
    assert "items" in response.data


@pytest.mark.django_db
def test_add_cart_item(authenticated_client, product):
    response = authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["quantity"] == 2


@pytest.mark.django_db
def test_add_cart_item_requires_authentication(api_client, product):
    response = api_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_add_nonexistent_product(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": 999999,
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_add_invalid_variant(
    authenticated_client,
    product,
):
    other_product = Product.objects.create(
        category=product.category,
        name="Gold Necklace",
        sku="NECKLACE-001",
        weight=10,
        purity=750,
    )

    variant = ProductVariant.objects.create(
        product=other_product,
        sku="NECKLACE-001-18K",
        weight=10,
    )

    response = authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "variant_id": variant.id,
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_add_invalid_quantity(authenticated_client, product):
    response = authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "quantity": 0,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_update_cart_item(authenticated_client, product):
    add_response = authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    item_id = add_response.data["id"]

    response = authenticated_client.patch(
        f"/api/v1/cart/items/{item_id}/",
        {"quantity": 5},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["quantity"] == 5


@pytest.mark.django_db
def test_update_nonexistent_cart_item(authenticated_client):
    response = authenticated_client.patch(
        "/api/v1/cart/items/999999/",
        {"quantity": 5},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_update_invalid_quantity(authenticated_client, product):
    add_response = authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    item_id = add_response.data["id"]

    response = authenticated_client.patch(
        f"/api/v1/cart/items/{item_id}/",
        {"quantity": 0},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_cannot_update_another_users_cart_item(
    authenticated_client,
    product,
):
    another_user = User.objects.create_user(
        phone_number="09120000004",
        password="TestPassword123!",
    )

    other_client_item_response = authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    item_id = other_client_item_response.data["id"]

    # The authenticated client owns this item, so create the second
    # user's item directly through the model/service boundary.
    from apps.cart.services import CartService

    item = CartService.add_item(
        user=another_user,
        product_id=product.id,
        quantity=2,
    )

    response = authenticated_client.patch(
        f"/api/v1/cart/items/{item.id}/",
        {"quantity": 5},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_cart_item(authenticated_client, product):
    add_response = authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    item_id = add_response.data["id"]

    response = authenticated_client.delete(
        f"/api/v1/cart/items/{item_id}/delete/"
    )

    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_nonexistent_cart_item(authenticated_client):
    response = authenticated_client.delete(
        "/api/v1/cart/items/999999/delete/"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_clear_cart(authenticated_client, product):
    authenticated_client.post(
        "/api/v1/cart/items/",
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    response = authenticated_client.delete(
        "/api/v1/cart/clear/"
    )

    assert response.status_code == 204