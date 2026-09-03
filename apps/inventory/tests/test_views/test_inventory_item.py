
import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.inventory.models import InventoryItem
from apps.inventory.views.inventory_item import (
    InventoryItemDetailView,
    InventoryItemListView,
)


@pytest.mark.django_db
class TestInventoryItemListView:
    """Test inventory item list API."""

    def setup_method(self):
        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(
            phone_number="09120000001",
            password="StrongPassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.category = Category.objects.create(
            name="Gold Jewelry",
            slug="gold-jewelry",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=10,
            reserved_quantity=3,
        )

    def test_admin_can_list_inventory_items(self):
        """Admin users must be able to retrieve inventory items."""

        request = self.factory.get("/api/inventory/items/")
        force_authenticate(request, user=self.user)

        response = InventoryItemListView.as_view()(request)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == self.inventory_item.id
        assert response.data[0]["quantity"] == 10
        assert response.data[0]["reserved_quantity"] == 3
        assert response.data[0]["available_quantity"] == 7

    def test_unauthenticated_user_cannot_list_inventory_items(self):
        """Unauthenticated users must not access inventory data."""

        request = self.factory.get("/api/inventory/items/")

        response = InventoryItemListView.as_view()(request)

        assert response.status_code == 403

    def test_regular_user_cannot_list_inventory_items(self):
        """Regular users must not access inventory data."""

        regular_user = User.objects.create_user(
            phone_number="09120000002",
            password="StrongPassword123",
        )

        request = self.factory.get("/api/inventory/items/")
        force_authenticate(request, user=regular_user)

        response = InventoryItemListView.as_view()(request)

        assert response.status_code == 403


@pytest.mark.django_db
class TestInventoryItemDetailView:
    """Test inventory item detail API."""

    def setup_method(self):
        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(
            phone_number="09120000003",
            password="StrongPassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.category = Category.objects.create(
            name="Gold Jewelry",
            slug="gold-jewelry",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Gold Necklace",
            slug="gold-necklace",
            sku="NECK-001",
            weight="5.250",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=15,
            reserved_quantity=4,
        )

    def test_admin_can_retrieve_inventory_item(self):
        """Admin users must be able to retrieve an inventory item."""

        request = self.factory.get(
            f"/api/inventory/items/{self.inventory_item.id}/"
        )

        force_authenticate(request, user=self.user)

        response = InventoryItemDetailView.as_view()(
            request,
            pk=self.inventory_item.id,
        )

        assert response.status_code == 200
        assert response.data["id"] == self.inventory_item.id
        assert response.data["quantity"] == 15
        assert response.data["reserved_quantity"] == 4
        assert response.data["available_quantity"] == 11

    def test_admin_getting_nonexistent_inventory_item_returns_404(self):
        """A missing inventory item must return HTTP 404."""

        request = self.factory.get(
            "/api/inventory/items/999999/"
        )

        force_authenticate(request, user=self.user)

        response = InventoryItemDetailView.as_view()(
            request,
            pk=999999,
        )

        assert response.status_code == 404

    def test_unauthenticated_user_cannot_retrieve_inventory_item(self):
        """Unauthenticated users must not retrieve inventory data."""

        request = self.factory.get(
            f"/api/inventory/items/{self.inventory_item.id}/"
        )

        response = InventoryItemDetailView.as_view()(
            request,
            pk=self.inventory_item.id,
        )

        assert response.status_code == 403

    def test_regular_user_cannot_retrieve_inventory_item(self):
        """Regular users must not retrieve inventory data."""

        regular_user = User.objects.create_user(
            phone_number="09120000004",
            password="StrongPassword123",
        )

        request = self.factory.get(
            f"/api/inventory/items/{self.inventory_item.id}/"
        )

        force_authenticate(request, user=regular_user)

        response = InventoryItemDetailView.as_view()(
            request,
            pk=self.inventory_item.id,
        )

        assert response.status_code == 403
