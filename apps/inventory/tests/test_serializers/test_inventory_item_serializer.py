from apps.inventory.models import InventoryItem
from apps.inventory.serializers.inventory_item import InventoryItemSerializer


class TestInventoryItemSerializer:
    """Test API serialization for InventoryItem."""

    def test_serializer_contains_expected_fields(self):
        """Serializer must expose the expected inventory fields."""

        serializer = InventoryItemSerializer()

        expected_fields = {
            "id",
            "product",
            "variant",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "is_active",
            "created_at",
            "updated_at",
        }

        assert set(serializer.fields.keys()) == expected_fields

    def test_read_only_fields_are_configured(self):
        """Inventory state fields must not be directly writable."""

        serializer = InventoryItemSerializer()

        expected_read_only_fields = {
            "id",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "created_at",
            "updated_at",
        }

        actual_read_only_fields = {
            field_name
            for field_name, field in serializer.fields.items()
            if field.read_only
        }

        assert actual_read_only_fields == expected_read_only_fields

    def test_available_quantity_is_serialized_correctly(self):
        """Available quantity must equal quantity minus reserved quantity."""

        inventory_item = InventoryItem(
            quantity=10,
            reserved_quantity=3,
        )

        serializer = InventoryItemSerializer(
            instance=inventory_item,
        )

        assert serializer.data["available_quantity"] == 7

    def test_quantity_cannot_be_modified_directly(self):
        """Quantity must not be accepted as writable input."""

        inventory_item = InventoryItem(
            quantity=10,
            reserved_quantity=3,
        )

        serializer = InventoryItemSerializer(
            instance=inventory_item,
            data={
                "quantity": 999,
            },
            partial=True,
        )

        assert serializer.is_valid()

        assert "quantity" not in serializer.validated_data

    def test_reserved_quantity_cannot_be_modified_directly(self):
        """Reserved quantity must not be accepted as writable input."""

        inventory_item = InventoryItem(
            quantity=10,
            reserved_quantity=3,
        )

        serializer = InventoryItemSerializer(
            instance=inventory_item,
            data={
                "reserved_quantity": 999,
            },
            partial=True,
        )

        assert serializer.is_valid()

        assert "reserved_quantity" not in serializer.validated_data