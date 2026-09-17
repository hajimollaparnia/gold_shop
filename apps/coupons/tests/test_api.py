from decimal import Decimal

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Return a DRF API client."""

    return APIClient()


@pytest.mark.django_db
def test_validate_coupon_api(
    api_client,
    user,
    percentage_coupon,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/coupons/validate/",
        {
            "code": "gold20",
            "order_amount": "2000000",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["coupon"]["code"] == "GOLD20"
    assert Decimal(response.data["discount_amount"]) == Decimal("400000")
    assert Decimal(response.data["final_amount"]) == Decimal("1600000")


@pytest.mark.django_db
def test_validate_unknown_coupon_returns_404(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/coupons/validate/",
        {
            "code": "UNKNOWN",
            "order_amount": "2000000",
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_validate_coupon_requires_authentication(
    api_client,
):
    response = api_client.post(
        "/api/v1/coupons/validate/",
        {
            "code": "GOLD20",
            "order_amount": "2000000",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_validate_coupon_rejects_invalid_amount(
    api_client,
    user,
    percentage_coupon,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/coupons/validate/",
        {
            "code": "GOLD20",
            "order_amount": "500000",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_validate_coupon_normalizes_code(
    api_client,
    user,
    percentage_coupon,
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/coupons/validate/",
        {
            "code": "  gold20  ",
            "order_amount": "2000000",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["coupon"]["code"] == "GOLD20"