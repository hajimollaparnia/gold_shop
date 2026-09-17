from django.conf import settings
from django.db import models


class Wishlist(models.Model):
    """
    Represents the wishlist owned by a user.

    Each user can have only one wishlist.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Wishlist #{self.pk} - {self.user}"


class WishlistItem(models.Model):
    """
    Represents a product or product variant saved by a user.

    Wishlist items do not reserve inventory and do not store prices.
    Current pricing is resolved from the pricing system when needed.
    """

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="wishlist_items",
    )

    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.PROTECT,
        related_name="wishlist_items",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"],
                condition=models.Q(variant__isnull=True),
                name="unique_wishlist_product_without_variant",
            ),
            models.UniqueConstraint(
                fields=["wishlist", "product", "variant"],
                condition=models.Q(variant__isnull=False),
                name="unique_wishlist_product_variant",
            ),
        ]

    def __str__(self):
        return f"{self.product} - Wishlist #{self.wishlist_id}"