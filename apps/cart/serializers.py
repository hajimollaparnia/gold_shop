from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serialize a cart item for API responses."""

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
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "variant",
            "variant_name",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "variant_name",
            "created_at",
            "updated_at",
        ]


class AddCartItemSerializer(serializers.Serializer):
    """Validate data required to add an item to a cart."""

    product_id = serializers.IntegerField(min_value=1)
    variant_id = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """Validate data required to update cart item quantity."""

    quantity = serializers.IntegerField(min_value=1)


class CartSerializer(serializers.ModelSerializer):
    """Serialize the authenticated user's shopping cart."""

    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
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