from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """
    Represents a product review submitted by an authenticated user.

    Each user can submit only one review for a given product.
    Reviews can optionally be linked to a specific product variant.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.SET_NULL,
        related_name="reviews",
        null=True,
        blank=True,
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    title = models.CharField(
        max_length=200,
        blank=True,
    )

    comment = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_review",
            ),
        ]
        indexes = [
            models.Index(
                fields=["product", "status"],
                name="review_product_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.product} - {self.rating}/5 - {self.user}"