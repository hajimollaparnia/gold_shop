import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.payments.models import Payment, PaymentStatus


User = get_user_model()


@pytest.fixture
def api_client():
    """Return a DRF API client."""

    return APIClient()


@pytest.fixture
def authenticated_client(api_client, order):
    """Return an API client authenticated as the order owner."""

    api_client.force_authenticate(user=order.user)

    return api_client


@pytest.fixture
def valid_receipt():
    """Return a valid uploaded JPEG image."""

    image = Image.new("RGB", (100, 100), "white")

    image_file = io.BytesIO()
    image.save(image_file, format="JPEG")

    return SimpleUploadedFile(
        "receipt.jpg",
        image_file.getvalue(),
        content_type="image/jpeg",
    )


@pytest.mark.django_db
def test_initialize_payment_api(
    authenticated_client,
    order,
):
    """Ensure an authenticated user can initialize a payment."""

    response = authenticated_client.post(
        f"/api/payments/orders/{order.pk}/initialize/",
    )

    assert response.status_code == 201
    assert response.data["order"] == order.pk
    assert response.data["status"] == PaymentStatus.PENDING

    assert Payment.objects.filter(
        order=order,
        status=PaymentStatus.PENDING,
    ).exists()


@pytest.mark.django_db
def test_initialize_payment_requires_authentication(
    api_client,
    order,
):
    """Ensure unauthenticated users cannot initialize payments."""

    response = api_client.post(
        f"/api/payments/orders/{order.pk}/initialize/",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_initialize_payment_for_another_users_order(
    api_client,
    order,
):
    """Ensure users cannot initialize payments for another user's order."""

    user = User.objects.create_user(
        phone_number="09987654321",
    )

    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/payments/orders/{order.pk}/initialize/",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_payment_receipt_api(
    authenticated_client,
    order,
    valid_receipt,
):
    """Ensure an authenticated user can upload a payment receipt."""

    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount,
        currency=order.currency,
    )

    response = authenticated_client.post(
        f"/api/payments/{payment.pk}/receipt/",
        {"receipt_image": valid_receipt},
        format="multipart",
    )

    assert response.status_code == 200

    payment.refresh_from_db()

    assert payment.receipt_image.name
    assert payment.status == PaymentStatus.PENDING


@pytest.mark.django_db
def test_upload_receipt_requires_authentication(
    api_client,
    order,
    valid_receipt,
):
    """Ensure unauthenticated users cannot upload receipts."""

    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount,
        currency=order.currency,
    )

    response = api_client.post(
        f"/api/payments/{payment.pk}/receipt/",
        {"receipt_image": valid_receipt},
        format="multipart",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_upload_receipt_for_another_users_payment(
    api_client,
    order,
    valid_receipt,
):
    """Ensure users cannot upload receipts for another user's payment."""

    user = User.objects.create_user(
        phone_number="09987654321",
    )

    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount,
        currency=order.currency,
    )

    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/payments/{payment.pk}/receipt/",
        {"receipt_image": valid_receipt},
        format="multipart",
    )

    assert response.status_code == 404