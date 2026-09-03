import pytest

from apps.inventory.serializers.stock import StockOperationSerializer


class TestStockOperationSerializer:
    """Test validation for inventory stock operations."""

    def test_serializer_accepts_valid_input(self):
        """Serializer must accept valid stock operation data."""

        data = {
            "inventory_item_id": 1,
            "quantity": 5,
            "reference": "purchase-001",
            "note": "Initial stock",
        }

        serializer = StockOperationSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["inventory_item_id"] == 1
        assert serializer.validated_data["quantity"] == 5
        assert serializer.validated_data["reference"] == "purchase-001"
        assert serializer.validated_data["note"] == "Initial stock"

    def test_reference_and_note_are_optional(self):
        """Reference and note must be optional."""

        serializer = StockOperationSerializer(
            data={
                "inventory_item_id": 1,
                "quantity": 5,
            }
        )

        assert serializer.is_valid()

    def test_inventory_item_id_must_be_positive(self):
        """Inventory item ID must be greater than zero."""

        serializer = StockOperationSerializer(
            data={
                "inventory_item_id": 0,
                "quantity": 5,
            }
        )

        assert not serializer.is_valid()
        assert "inventory_item_id" in serializer.errors

    def test_negative_quantity_is_accepted_for_adjustments(self):
        """Negative quantity must be accepted for stock adjustments."""

        serializer = StockOperationSerializer(
            data={
                "inventory_item_id": 1,
                "quantity": -5,
            }
        )

        assert serializer.is_valid()
        assert serializer.validated_data["quantity"] == -5

    def test_zero_quantity_is_accepted_by_serializer(self):
        """
        Zero quantity is structurally valid input.

        Service layer is responsible for rejecting zero-value
        stock operations according to the operation being performed.
        """

        serializer = StockOperationSerializer(
            data={
                "inventory_item_id": 1,
                "quantity": 0,
            }
        )

        assert serializer.is_valid()

    def test_reference_cannot_exceed_maximum_length(self):
        """Reference must respect the model-compatible maximum length."""

        serializer = StockOperationSerializer(
            data={
                "inventory_item_id": 1,
                "quantity": 5,
                "reference": "x" * 101,
            }
        )

        assert not serializer.is_valid()
        assert "reference" in serializer.errors

    def test_note_accepts_long_text(self):
        """Note should accept arbitrary-length explanatory text."""

        serializer = StockOperationSerializer(
            data={
                "inventory_item_id": 1,
                "quantity": 5,
                "note": "x" * 1000,
            }
        )

        assert serializer.is_valid()