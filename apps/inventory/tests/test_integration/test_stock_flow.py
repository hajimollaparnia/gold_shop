import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.catalog.models import Category, Product
from apps.inventory.models import InventoryItem, StockMovement


@pytest.mark.django_db
class TestStockIntegrationFlow:
    """
    Integration tests for the complete stock API flow.

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
            sku="GR-001",
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

    def test_increase_stock_flow(self):
        self.authenticate_admin()

        url = reverse("inventory:stock-increase")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 5,
                "reference": "PURCHASE-001",
                "note": "New stock received.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 15
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 13

        movement = StockMovement.objects.get(
            inventory_item=self.inventory_item,
        )

        assert movement.movement_type == StockMovement.MovementType.IN
        assert movement.quantity == 5
        assert movement.reference == "PURCHASE-001"
        assert movement.note == "New stock received."

        assert response.data["inventory_item_id"] == self.inventory_item.id
        assert response.data["quantity"] == 15
        assert response.data["reserved_quantity"] == 2
        assert response.data["available_quantity"] == 13

    def test_decrease_stock_flow(self):
        self.authenticate_admin()

        url = reverse("inventory:stock-decrease")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 3,
                "reference": "ORDER-001",
                "note": "Stock sold.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 7
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 5

        movement = StockMovement.objects.get(
            inventory_item=self.inventory_item,
        )

        assert movement.movement_type == StockMovement.MovementType.OUT
        assert movement.quantity == 3
        assert movement.reference == "ORDER-001"
        assert movement.note == "Stock sold."

        assert response.data["quantity"] == 7
        assert response.data["reserved_quantity"] == 2
        assert response.data["available_quantity"] == 5

    def test_adjust_stock_increase_flow(self):
        self.authenticate_admin()

        url = reverse("inventory:stock-adjust")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 4,
                "reference": "ADJUSTMENT-001",
                "note": "Physical inventory correction.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 14
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 12

        movement = StockMovement.objects.get(
            inventory_item=self.inventory_item,
        )

        assert movement.movement_type == StockMovement.MovementType.ADJUSTMENT
        assert movement.quantity == 4
        assert movement.reference == "ADJUSTMENT-001"
        assert movement.note == "Physical inventory correction."

    def test_adjust_stock_decrease_flow(self):
        self.authenticate_admin()

        url = reverse("inventory:stock-adjust")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": -3,
                "reference": "ADJUSTMENT-002",
                "note": "Damaged stock correction.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 7
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 5

        movement = StockMovement.objects.get(
            inventory_item=self.inventory_item,
        )

        assert movement.movement_type == StockMovement.MovementType.ADJUSTMENT
        assert movement.quantity == 3
        assert movement.reference == "ADJUSTMENT-002"
        assert movement.note == "Damaged stock correction."

    def test_decrease_stock_rejects_insufficient_available_stock(self):
        self.authenticate_admin()

        url = reverse("inventory:stock-decrease")

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

        assert not StockMovement.objects.filter(
            inventory_item=self.inventory_item,
        ).exists()

    def test_increase_stock_rejects_invalid_quantity(self):
        self.authenticate_admin()

        url = reverse("inventory:stock-increase")

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

        assert not StockMovement.objects.filter(
            inventory_item=self.inventory_item,
        ).exists()

    def test_adjust_stock_rejects_zero_quantity(self):
        self.authenticate_admin()

        url = reverse("inventory:stock-adjust")

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

        assert not StockMovement.objects.filter(
            inventory_item=self.inventory_item,
        ).exists()

    def test_adjust_stock_cannot_reduce_quantity_below_reserved_stock(self):
        self.authenticate_admin()

        url = reverse("inventory:stock-adjust")

        response = self.client.post(
            url,
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": -9,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.inventory_item.refresh_from_db()

        assert self.inventory_item.quantity == 10
        assert self.inventory_item.reserved_quantity == 2
        assert self.inventory_item.available_quantity == 8

        assert not StockMovement.objects.filter(
            inventory_item=self.inventory_item,
        ).exists()

    def test_stock_operations_require_admin_permission(self):
        urls = (
            reverse("inventory:stock-increase"),
            reverse("inventory:stock-decrease"),
            reverse("inventory:stock-adjust"),
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

        assert not StockMovement.objects.filter(
            inventory_item=self.inventory_item,
        ).exists()