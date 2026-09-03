import pytest
from django.contrib import admin

from apps.inventory.admin import InventoryItemAdmin
from apps.inventory.models import InventoryItem


@pytest.mark.django_db
class TestInventoryItemAdmin:
    """Test Django Admin configuration for InventoryItem."""

    def test_inventory_item_is_registered(self):
        """InventoryItem must be registered in Django Admin."""

        assert admin.site.is_registered(InventoryItem)

    def test_registered_admin_class_is_correct(self):
        """InventoryItem must use the expected ModelAdmin class."""

        registered_admin = admin.site.get_model_admin(InventoryItem)

        assert isinstance(registered_admin, InventoryItemAdmin)

    def test_list_display_contains_required_fields(self):
        """Admin list display must expose the essential inventory data."""

        registered_admin = admin.site.get_model_admin(InventoryItem)

        assert "id" in registered_admin.list_display
        assert "quantity" in registered_admin.list_display
        assert "reserved_quantity" in registered_admin.list_display
        assert "available_quantity_display" in registered_admin.list_display
        assert "is_active" in registered_admin.list_display
        assert "updated_at" in registered_admin.list_display

    def test_search_fields_are_configured(self):
        """Admin search must support product and variant identification."""

        registered_admin = admin.site.get_model_admin(InventoryItem)

        assert "product__name" in registered_admin.search_fields
        assert "product__sku" in registered_admin.search_fields
        assert "variant__sku" in registered_admin.search_fields

    def test_readonly_fields_are_configured(self):
        """Calculated and timestamp fields must be read-only."""

        registered_admin = admin.site.get_model_admin(InventoryItem)

        assert "available_quantity_display" in registered_admin.readonly_fields
        assert "created_at" in registered_admin.readonly_fields
        assert "updated_at" in registered_admin.readonly_fields

    def test_list_select_related_is_configured(self):
        """Admin should optimize related product and variant queries."""

        registered_admin = admin.site.get_model_admin(InventoryItem)

        assert "product" in registered_admin.list_select_related
        assert "variant" in registered_admin.list_select_related

    def test_available_quantity_display_returns_available_stock(self):
        """Admin must display physical stock minus reserved stock."""

        inventory_item = InventoryItem(
            quantity=10,
            reserved_quantity=3,
        )

        registered_admin = admin.site.get_model_admin(InventoryItem)

        assert (
                registered_admin.available_quantity_display(inventory_item)
                == 7
        )