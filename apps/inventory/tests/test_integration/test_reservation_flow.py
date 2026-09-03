import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.catalog.models import Category, Product
from apps.inventory.models import InventoryItem


@pytest.mark.django_db
class TestReservationIntegrationFlow:
    """
    Integration tests for the complete reservation API flow.

    These tests verify the interaction between:
        URL → View → Serializer → Service → Database
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()

        self.category = Category.objects.create(
            name="Gold",
            slug="gold",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            sku="GR-002",
            weight="5.000",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=10,
            reserved_quantity=2,
        )

    def authenticate_admin(self):
        """
        Authenticate the API client as an admin user.
        """
        from django.contrib.auth import get_user_model

        user_model = get_user_model()

        self.admin = user_model.objects.create_superuser(
            phone_number="09120000001",
            password="StrongPassword123!",
        )

        self.client.force_authenticate(user=self.admin)

    def test_reserve_stock_flow(self):
        self.authenticate_admin()

        url = reverse("inventory:reservation-reserve")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 3,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 5
        assert self.inventory_item.available_quantity == 5

        assert response.data["inventory_item_id"] == self.inventory_item.id
        assert response.data["quantity"] == 10
        assert response.data["reserved_quantity"] == 5
        assert response.data["available_quantity"] == 5

    def test_release_reserved_stock_flow(self):
        self.authenticate_admin()

        self.inventory_item.reserved_quantity = 5
        self.inventory_item.save(
            update_fields=["reserved_quantity"],
        )

        url = reverse("inventory:reservation-release")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 3,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8

        assert response.data["inventory_item_id"] == self.inventory_item.id
        assert response.data["quantity"] == 10
        assert response.data["reserved_quantity"] == 2
        assert response.data["available_quantity"] == 8

    def test_commit_reserved_stock_flow(self):
        self.authenticate_admin()

        self.inventory_item.reserved_quantity = 5
        self.inventory_item.save(
            update_fields=["reserved_quantity"],
        )

        url = reverse("inventory:reservation-commit")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 3,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 7
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 5

        assert response.data["inventory_item_id"] == self.inventory_item.id
        assert response.data["quantity"] == 7
        assert response.data["reserved_quantity"] == 2
        assert response.data["available_quantity"] == 5

    def test_reserve_rejects_insufficient_available_stock(self):
        self.authenticate_admin()

        url = reverse("inventory:reservation-reserve")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 9,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8

    def test_release_rejects_quantity_above_reserved_stock(self):
        self.authenticate_admin()

        url = reverse("inventory:reservation-release")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 3,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8

    def test_commit_rejects_quantity_above_reserved_stock(self):
        self.authenticate_admin()

        url = reverse("inventory:reservation-commit")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 3,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8

    def test_reserve_rejects_invalid_quantity(self):
        self.authenticate_admin()

        url = reverse("inventory:reservation-reserve")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 0,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8

    def test_release_rejects_invalid_quantity(self):
        self.authenticate_admin()

        url = reverse("inventory:reservation-release")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 0,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8

    def test_commit_rejects_invalid_quantity(self):
        self.authenticate_admin()

        url = reverse("inventory:reservation-commit")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 0,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8

    def test_reservation_operations_require_admin_permission(self):
        urls = (
            reverse("inventory:reservation-reserve"),
            reverse("inventory:reservation-release"),
            reverse("inventory:reservation-commit"),
        )

        for url in urls:
            response = self.client.post(
                url,
                {
                    "inventory_item_id": self.inventory_item.id,
                    "quantity": 1,
                },
                format="json",
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8