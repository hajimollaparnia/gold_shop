from rest_framework import serializers

from apps.catalog.models import Product, ProductVariant
from apps.pricing.models import PriceSnapshot

from .models import Order, OrderItem


class CreateOrderItemSerializer(serializers.Serializer):
    """
    Serializer for validating a single order item.

    The serializer only validates input data.
    Business logic such as inventory reservation is handled
    by OrderService.
    """

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
    )

    variant = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    price_snapshot_id = serializers.PrimaryKeyRelatedField(
        queryset=PriceSnapshot.objects.all(),
        source="price_snapshot",
    )

    quantity = serializers.IntegerField(
        min_value=1,
    )

    def validate(self, attrs):
        """
        Ensure the selected variant belongs to the selected product.
        """

        product = attrs["product"]
        variant = attrs.get("variant")

        if variant is not None and variant.product_id != product.id:
            raise serializers.ValidationError(
                {
                    "variant": (
                        "Variant does not belong to the selected product."
                    )
                }
            )

        return attrs


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer for creating an order.

    Orders can be created by guest customers. Customer information
    is captured directly from the checkout request and is not required
    to belong to an existing user account.
    """

    customer_name = serializers.CharField(
        max_length=200,
    )

    customer_phone = serializers.CharField(
        max_length=11,
    )

    shipping_address = serializers.CharField()

    shipping_cost = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        min_value=0,
        default=0,
    )

    discount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        min_value=0,
        default=0,
    )

    tax = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        min_value=0,
        default=0,
    )

    items = CreateOrderItemSerializer(
        many=True,
        allow_empty=False,
    )


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying order item information.
    """

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "variant",
            "product_name_snapshot",
            "sku_snapshot",
            "weight_snapshot",
            "purity_snapshot",
            "quantity",
            "unit_price",
            "total_price",
            "price_snapshot",
            "created_at",
        ]

        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying complete order information.

    The user field is read-only because account association is handled
    by the application service after successful payment.
    """

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "payment_status",
            "customer_name",
            "customer_phone",
            "shipping_address",
            "subtotal",
            "discount",
            "shipping_cost",
            "tax",
            "total_amount",
            "currency",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields