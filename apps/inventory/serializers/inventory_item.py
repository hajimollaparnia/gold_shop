from rest_framework import serializers

from apps.inventory.models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    """
    Serialize inventory state for API consumers.

    Available quantity is exposed as a read-only calculated field and
    cannot be modified directly through the API.
    """

    available_quantity = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = InventoryItem
        fields = (
            "id",
            "product",
            "variant",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "created_at",
            "updated_at",
        )