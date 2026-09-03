import pytest
from django.contrib import admin

from apps.inventory.admin import StockMovementAdmin
from apps.inventory.models import StockMovement


@pytest.mark.django_db
class TestStockMovementAdmin:
    """Test Django Admin configuration for StockMovement."""

    def test_stock_movement_is_registered(self):
        """StockMovement must be registered in Django Admin."""

        assert admin.site.is_registered(StockMovement)

    def test_registered_admin_class_is_correct(self):
        """StockMovement must use the expected ModelAdmin class."""

        registered_admin = admin.site.get_model_admin(StockMovement)

        assert isinstance(registered_admin, StockMovementAdmin)

    def test_list_display_contains_required_fields(self):
        """Admin list display must expose essential movement data."""

        registered_admin = admin.site.get_model_admin(StockMovement)

        assert "id" in registered_admin.list_display
        assert "inventory_item" in registered_admin.list_display
        assert "movement_type" in registered_admin.list_display
        assert "quantity" in registered_admin.list_display
        assert "reference" in registered_admin.list_display
        assert "created_at" in registered_admin.list_display

    def test_search_fields_are_configured(self):
        """Admin search must support inventory and movement references."""

        registered_admin = admin.site.get_model_admin(StockMovement)

        assert "inventory_item__product__name" in registered_admin.search_fields
        assert "inventory_item__product__sku" in registered_admin.search_fields
        assert "inventory_item__variant__sku" in registered_admin.search_fields
        assert "reference" in registered_admin.search_fields
        assert "note" in registered_admin.search_fields

    def test_readonly_fields_are_configured(self):
        """All movement fields must be read-only in Admin."""

        registered_admin = admin.site.get_model_admin(StockMovement)

        expected_fields = {
            "inventory_item",
            "movement_type",
            "quantity",
            "reference",
            "note",
            "created_at",
        }

        assert expected_fields.issubset(
            set(registered_admin.readonly_fields)
        )

    def test_list_select_related_is_configured(self):
        """Admin should optimize related inventory queries."""

        registered_admin = admin.site.get_model_admin(StockMovement)

        assert "inventory_item" in registered_admin.list_select_related
        assert "inventory_item__product" in registered_admin.list_select_related
        assert "inventory_item__variant" in registered_admin.list_select_related

    def test_manual_creation_is_disabled(self):
        """Stock movements must not be created manually from Admin."""

        registered_admin = admin.site.get_model_admin(StockMovement)

        assert registered_admin.has_add_permission(None) is False

    def test_deletion_is_disabled(self):
        """Stock movements must not be deleted from Admin."""

        registered_admin = admin.site.get_model_admin(StockMovement)

        assert registered_admin.has_delete_permission(None) is False

    def test_ordering_is_deterministic(self):
        """Admin ordering must remain deterministic for equal timestamps."""

        registered_admin = admin.site.get_model_admin(StockMovement)

        assert registered_admin.ordering == (
            "-created_at",
            "-id",
        )