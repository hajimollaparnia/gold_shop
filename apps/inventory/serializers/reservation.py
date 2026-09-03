from rest_framework import serializers


class ReservationOperationSerializer(serializers.Serializer):
    """
    Validate inventory reservation operation input.

    Reservation business rules remain inside ReservationService.
    """

    inventory_item_id = serializers.IntegerField(
        min_value=1,
    )

    quantity = serializers.IntegerField(
        min_value=1,
    )