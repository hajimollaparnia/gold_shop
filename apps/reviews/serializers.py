from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize product reviews for API responses."""

    user_phone = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "user_phone",
            "product",
            "variant",
            "rating",
            "title",
            "comment",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_phone",
            "status",
            "created_at",
            "updated_at",
        ]


class CreateReviewSerializer(serializers.Serializer):
    """Validate data required to create a product review."""

    product_id = serializers.IntegerField(min_value=1)

    variant_id = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )

    rating = serializers.IntegerField(
        min_value=1,
        max_value=5,
    )

    title = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
    )

    comment = serializers.CharField(
        required=False,
        allow_blank=True,
    )