from rest_framework import serializers


class StockOperationSerializer(serializers.Serializer):
    """
    Validate inventory stock operation input.

    Business logic and stock mutation remain inside StockService.
    """

    inventory_item_id = serializers.IntegerField(
        min_value=1,
    )

    quantity = serializers.IntegerField()

    reference = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
    )