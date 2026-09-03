import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.inventory.models import InventoryItem
from apps.inventory.views.reservation import (
    ReservationCommitView,
    ReservationReleaseView,
    ReservationReserveView,
)


@pytest.mark.django_db
class TestReservationReserveView:
    """Test inventory reservation API."""

    def setup_method(self):
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(
            phone_number="09120000401",
            password="StrongPassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.regular_user = User.objects.create_user(
            phone_number="09120000402",
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
            sku="RING-401",
            weight="2.500",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=10,
            reserved_quantity=2,
        )

    def test_admin_can_reserve_stock(self):
        """Admin users must be able to reserve available stock."""

        request = self.factory.post(
            "/api/inventory/reservations/reserve/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 5,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = ReservationReserveView.as_view()(request)

        assert response.status_code == 200
        assert response.data["inventory_item_id"] == self.inventory_item.id
        assert response.data["quantity"] == 10
        assert response.data["reserved_quantity"] == 7
        assert response.data["available_quantity"] == 3

    def test_reserve_beyond_available_stock_returns_400(self):
        """Stock cannot be reserved beyond available quantity."""

        request = self.factory.post(
            "/api/inventory/reservations/reserve/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 9,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = ReservationReserveView.as_view()(request)

        assert response.status_code == 400
        assert response.data["detail"] == (
            "Insufficient available stock."
        )

    def test_invalid_reserve_quantity_returns_400(self):
        """Reservation quantity must be greater than zero."""

        request = self.factory.post(
            "/api/inventory/reservations/reserve/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 0,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = ReservationReserveView.as_view()(request)

        assert response.status_code == 400

    def test_unauthenticated_user_cannot_reserve_stock(self):
        """Unauthenticated users must not reserve stock."""

        request = self.factory.post(
            "/api/inventory/reservations/reserve/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 2,
            },
            format="json",
        )

        response = ReservationReserveView.as_view()(request)

        assert response.status_code == 403

    def test_regular_user_cannot_reserve_stock(self):
        """Regular users must not reserve stock."""

        request = self.factory.post(
            "/api/inventory/reservations/reserve/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 2,
            },
            format="json",
        )

        force_authenticate(request, user=self.regular_user)

        response = ReservationReserveView.as_view()(request)

        assert response.status_code == 403


@pytest.mark.django_db
class TestReservationReleaseView:
    """Test inventory reservation release API."""

    def setup_method(self):
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(
            phone_number="09120000501",
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
            sku="NECK-501",
            weight="5.250",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=15,
            reserved_quantity=6,
        )

    def test_admin_can_release_reserved_stock(self):
        """Admin users must be able to release reserved stock."""

        request = self.factory.post(
            "/api/inventory/reservations/release/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 4,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = ReservationReleaseView.as_view()(request)

        assert response.status_code == 200
        assert response.data["quantity"] == 15
        assert response.data["reserved_quantity"] == 2
        assert response.data["available_quantity"] == 13

    def test_release_beyond_reserved_quantity_returns_400(self):
        """Cannot release more than the reserved quantity."""

        request = self.factory.post(
            "/api/inventory/reservations/release/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 7,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = ReservationReleaseView.as_view()(request)

        assert response.status_code == 400
        assert response.data["detail"] == (
            "Release quantity cannot exceed reserved quantity."
        )

    def test_regular_user_cannot_release_reserved_stock(self):
        """Regular users must not release reserved stock."""

        regular_user = User.objects.create_user(
            phone_number="09120000502",
            password="StrongPassword123",
        )

        request = self.factory.post(
            "/api/inventory/reservations/release/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 2,
            },
            format="json",
        )

        force_authenticate(request, user=regular_user)

        response = ReservationReleaseView.as_view()(request)

        assert response.status_code == 403


@pytest.mark.django_db
class TestReservationCommitView:
    """Test inventory reservation commit API."""

    def setup_method(self):
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_user(
            phone_number="09120000601",
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
            sku="BRACE-601",
            weight="4.750",
            purity=750,
        )

        self.inventory_item = InventoryItem.objects.create(
            product=self.product,
            quantity=20,
            reserved_quantity=8,
        )

    def test_admin_can_commit_reserved_stock(self):
        """Admin users must be able to commit reserved stock."""

        request = self.factory.post(
            "/api/inventory/reservations/commit/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 5,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = ReservationCommitView.as_view()(request)

        assert response.status_code == 200
        assert response.data["quantity"] == 15
        assert response.data["reserved_quantity"] == 3
        assert response.data["available_quantity"] == 12

    def test_commit_beyond_reserved_quantity_returns_400(self):
        """Cannot commit more than the reserved quantity."""

        request = self.factory.post(
            "/api/inventory/reservations/commit/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 9,
            },
            format="json",
        )

        force_authenticate(request, user=self.admin_user)

        response = ReservationCommitView.as_view()(request)

        assert response.status_code == 400
        assert response.data["detail"] == (
            "Commit quantity cannot exceed reserved quantity."
        )

    def test_regular_user_cannot_commit_reserved_stock(self):
        """Regular users must not commit reserved stock."""

        regular_user = User.objects.create_user(
            phone_number="09120000602",
            password="StrongPassword123",
        )

        request = self.factory.post(
            "/api/inventory/reservations/commit/",
            {
                "inventory_item_id": self.inventory_item.id,
                "quantity": 2,
            },
            format="json",
        )

        force_authenticate(request, user=regular_user)

        response = ReservationCommitView.as_view()(request)

        assert response.status_code == 403