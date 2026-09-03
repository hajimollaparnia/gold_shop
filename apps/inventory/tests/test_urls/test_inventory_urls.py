import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestInventoryURLs:
    """Test Inventory URL routing."""

    def test_inventory_item_list_url(self):
        """Inventory item list URL must resolve correctly."""

        url = reverse("inventory:inventory-item-list")

        assert url == "/api/inventory/items/"

    def test_inventory_item_detail_url(self):
        """Inventory item detail URL must resolve correctly."""

        url = reverse(
            "inventory:inventory-item-detail",
            kwargs={"pk": 1},
        )

        assert url == "/api/inventory/items/1/"

    def test_stock_increase_url(self):
        """Stock increase URL must resolve correctly."""

        url = reverse("inventory:stock-increase")

        assert url == "/api/inventory/stock/increase/"

    def test_stock_decrease_url(self):
        """Stock decrease URL must resolve correctly."""

        url = reverse("inventory:stock-decrease")

        assert url == "/api/inventory/stock/decrease/"

    def test_stock_adjust_url(self):
        """Stock adjustment URL must resolve correctly."""

        url = reverse("inventory:stock-adjust")

        assert url == "/api/inventory/stock/adjust/"

    def test_reservation_reserve_url(self):
        """Reservation reserve URL must resolve correctly."""

        url = reverse("inventory:reservation-reserve")

        assert url == "/api/inventory/reservations/reserve/"

    def test_reservation_release_url(self):
        """Reservation release URL must resolve correctly."""

        url = reverse("inventory:reservation-release")

        assert url == "/api/inventory/reservations/release/"

    def test_reservation_commit_url(self):
        """Reservation commit URL must resolve correctly."""

        url = reverse("inventory:reservation-commit")

        assert url == "/api/inventory/reservations/commit/"