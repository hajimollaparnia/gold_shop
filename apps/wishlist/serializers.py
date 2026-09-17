from rest_framework import serializers

from .models import Wishlist, WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serialize a wishlist item for API responses."""

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    variant_name = serializers.CharField(
        source="variant.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "product",
            "product_name",
            "variant",
            "variant_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "variant_name",
            "created_at",
        ]


class AddWishlistItemSerializer(serializers.Serializer):
    """Validate data required to add an item to a wishlist."""

    product_id = serializers.IntegerField(min_value=1)

    variant_id = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )


class WishlistSerializer(serializers.ModelSerializer):
    """Serialize the authenticated user's wishlist."""

    items = WishlistItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "items",
            "created_at",
            "updated_at",
        ]