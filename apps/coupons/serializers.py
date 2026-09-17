from rest_framework import serializers

from .models import Coupon


class CouponValidateSerializer(serializers.Serializer):
    """Validate coupon validation requests."""

    code = serializers.CharField(
        max_length=50,
    )

    order_amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        min_value=0,
    )

    def validate_code(self, value):
        """Normalize coupon codes before processing."""

        return value.strip().upper()


class CouponResponseSerializer(serializers.ModelSerializer):
    """Serialize coupon information returned by the API."""

    class Meta:
        model = Coupon
        fields = [
            "code",
            "discount_type",
            "discount_value",
            "minimum_order_amount",
            "starts_at",
            "expires_at",
            "is_active",
        ]
        read_only_fields = fields


class CouponValidationResponseSerializer(serializers.Serializer):
    """Serialize the result of coupon validation."""

    coupon = CouponResponseSerializer()
    discount_amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
    )
    final_amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
    )