from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serialize payment information for API responses."""

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "amount",
            "currency",
            "gateway",
            "status",
            "receipt_image",
            "failure_reason",
            "verified_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "order",
            "amount",
            "currency",
            "gateway",
            "status",
            "failure_reason",
            "verified_at",
            "created_at",
            "updated_at",
        ]


class ReceiptUploadSerializer(serializers.Serializer):
    """Validate a customer-uploaded payment receipt."""

    receipt_image = serializers.ImageField(
        required=True,
        allow_empty_file=False,
    )