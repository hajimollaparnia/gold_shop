from apps.inventory.serializers.reservation import (
    ReservationOperationSerializer,
)


class TestReservationOperationSerializer:
    """Test validation for inventory reservation operations."""

    def test_serializer_accepts_valid_input(self):
        """Serializer must accept valid reservation data."""

        serializer = ReservationOperationSerializer(
            data={
                "inventory_item_id": 1,
                "quantity": 5,
            }
        )

        assert serializer.is_valid()
        assert serializer.validated_data["inventory_item_id"] == 1
        assert serializer.validated_data["quantity"] == 5

    def test_inventory_item_id_must_be_positive(self):
        """Inventory item ID must be greater than zero."""

        serializer = ReservationOperationSerializer(
            data={
                "inventory_item_id": 0,
                "quantity": 5,
            }
        )

        assert not serializer.is_valid()
        assert "inventory_item_id" in serializer.errors

    def test_quantity_must_be_positive(self):
        """Reservation quantity must be greater than zero."""

        serializer = ReservationOperationSerializer(
            data={
                "inventory_item_id": 1,
                "quantity": 0,
            }
        )

        assert not serializer.is_valid()
        assert "quantity" in serializer.errors

    def test_negative_quantity_is_rejected(self):
        """Negative reservation quantity must be rejected."""

        serializer = ReservationOperationSerializer(
            data={
                "inventory_item_id": 1,
                "quantity": -5,
            }
        )

        assert not serializer.is_valid()
        assert "quantity" in serializer.errors

    def test_required_fields_are_enforced(self):
        """Both inventory item ID and quantity must be provided."""

        serializer = ReservationOperationSerializer(data={})

        assert not serializer.is_valid()
        assert "inventory_item_id" in serializer.errors
        assert "quantity" in serializer.errors