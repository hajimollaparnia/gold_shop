import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.inventory.models import InventoryItem
from apps.inventory.views.stock import (
    StockAdjustView,
    StockDecreaseView,
    StockIncreaseView,
)


@pytest.mark.django_db
class TestStockIncreaseView:
    """Test inventory stock increase API."""

    def setup_method(self):
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(
            phone_number="09120000101",
            password="StrongPassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.regular_user = User.objects.create_user(
            phone_number="09120000102",
            password="StrongPassword123",
        )

        self.category = Category.objects.create(
            name="Gold Jewelry",
            slug="gold-jewelry",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-101",
            weight="2.500",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=10,
            reserved_quantity=2,
        )

    def test_admin_can_increase_stock(self):
        """Admin users must be able to increase stock."""

        request = self.factory.post(
            "/api/inventory/stock/increase/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 5,
                "reference": "PURCHASE-001",
                "note": "New stock received",
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = StockIncreaseView.as_view()(request)

        assert response.status_code == 200
        assert response.data["inventory_item_id"] == self.inventory_item.id
        assert response.data["quantity"] == 15
        assert response.data["reserved_quantity"] == 2
        assert response.data["available_quantity"] == 13

    def test_unauthenticated_user_cannot_increase_stock(self):
        """Unauthenticated users must not modify inventory."""

        request = self.factory.post(
            "/api/inventory/stock/increase/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 5,
            },
            format="json",
        )

        response = StockIncreaseView.as_view()(request)

        assert response.status_code == 403

    def test_regular_user_cannot_increase_stock(self):
        """Regular users must not modify inventory."""

        request = self.factory.post(
            "/api/inventory/stock/increase/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 5,
            },
            format="json",
        )

        force_authenticate(request, user=self.regular_user)

        response = StockIncreaseView.as_view()(request)

        assert response.status_code == 403

    def test_invalid_quantity_returns_400(self):
        """Invalid stock quantity must return HTTP 400."""

        request = self.factory.post(
            "/api/inventory/stock/increase/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 0,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = StockIncreaseView.as_view()(request)

        assert response.status_code == 400
        assert response.data["detail"] == (
            "Quantity must be greater than zero."
        )


@pytest.mark.django_db
class TestStockDecreaseView:
    """Test inventory stock decrease API."""

    def setup_method(self):
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(
            phone_number="09120000201",
            password="StrongPassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.regular_user = User.objects.create_user(
            phone_number="09120000202",
            password="StrongPassword123",
        )

        self.category = Category.objects.create(
            name="Gold Jewelry",
            slug="gold-jewelry",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Gold Necklace",
            slug="gold-necklace",
            sku="NECK-101",
            weight="5.250",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=15,
            reserved_quantity=4,
        )

    def test_admin_can_decrease_stock(self):
        """Admin users must be able to decrease available stock."""

        request = self.factory.post(
            "/api/inventory/stock/decrease/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 5,
                "reference": "ORDER-001",
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = StockDecreaseView.as_view()(request)

        assert response.status_code == 200
        assert response.data["quantity"] == 10
        assert response.data["reserved_quantity"] == 4
        assert response.data["available_quantity"] == 6

    def test_decrease_beyond_available_stock_returns_400(self):
        """Stock cannot be decreased below available quantity."""

        request = self.factory.post(
            "/api/inventory/stock/decrease/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 12,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = StockDecreaseView.as_view()(request)

        assert response.status_code == 400
        assert response.data["detail"] == (
            "Insufficient available stock."
        )

    def test_regular_user_cannot_decrease_stock(self):
        """Regular users must not modify inventory."""

        request = self.factory.post(
            "/api/inventory/stock/decrease/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 2,
            },
            format="json",
        )

        force_authenticate(request, user=self.regular_user)

        response = StockDecreaseView.as_view()(request)

        assert response.status_code == 403


@pytest.mark.django_db
class TestStockAdjustView:
    """Test inventory stock adjustment API."""

    def setup_method(self):
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(
            phone_number="09120000301",
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
            name="Gold Bracelet",
            slug="gold-bracelet",
            sku="BRACE-101",
            weight="4.750",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=20,
            reserved_quantity=5,
        )

    def test_admin_can_increase_stock_with_adjustment(self):
        """Positive adjustment must increase stock."""

        request = self.factory.post(
            "/api/inventory/stock/adjust/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 3,
                "reference": "COUNT-001",
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = StockAdjustView.as_view()(request)

        assert response.status_code == 200
        assert response.data["quantity"] == 23
        assert response.data["reserved_quantity"] == 5
        assert response.data["available_quantity"] == 18

    def test_admin_can_decrease_stock_with_adjustment(self):
        """Negative adjustment must decrease stock."""

        request = self.factory.post(
            "/api/inventory/stock/adjust/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": -4,
                "reference": "COUNT-002",
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = StockAdjustView.as_view()(request)

        assert response.status_code == 200
        assert response.data["quantity"] == 16
        assert response.data["reserved_quantity"] == 5
        assert response.data["available_quantity"] == 11

    def test_zero_adjustment_returns_400(self):
        """Zero adjustment must be rejected."""

        request = self.factory.post(
            "/api/inventory/stock/adjust/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 0,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = StockAdjustView.as_view()(request)

        assert response.status_code == 400
        assert response.data["detail"] == (
            "Adjustment quantity cannot be zero."
        )

    def test_adjustment_cannot_go_below_reserved_quantity(self):
        """Adjustment cannot reduce stock below reserved quantity."""

        request = self.factory.post(
            "/api/inventory/stock/adjust/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": -16,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = StockAdjustView.as_view()(request)

        assert response.status_code == 400
        assert response.data["detail"] == (
            "Adjusted quantity cannot be lower than reserved quantity."
        )