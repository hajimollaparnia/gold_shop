from django.conf import settings
from django.db import models
from django.db.models import Q


class Cart(models.Model):
    """
    Represents the active shopping cart owned by a user.

    Each user can have only one active cart at a time.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Cart #{self.pk} - {self.user}"


class CartItem(models.Model):
    """
    Represents a single product or product variant inside a cart.

    A cart item stores the selected quantity and the catalog reference.
    The actual price is resolved from the pricing system when the order
    is created rather than trusting client-provided values.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="cart_items",
    )

    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.PROTECT,
        related_name="cart_items",
        null=True,
        blank=True,
    )

    quantity = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="cart_item_quantity_positive",
            ),
            models.UniqueConstraint(
                fields=["cart", "product", "variant"],
                name="unique_cart_product_variant",
            ),
        ]

    def __str__(self):
        return f"{self.product} x {self.quantity}"