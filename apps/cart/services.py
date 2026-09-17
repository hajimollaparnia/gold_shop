from django.db import transaction

from apps.catalog.models import Product, ProductVariant

from .exceptions import (
    InvalidCartQuantityError,
    ProductNotFoundError,
    ProductVariantNotFoundError,
)
from .models import Cart, CartItem


class CartService:
    """Provides transactional business operations for shopping carts."""

    @staticmethod
    @transaction.atomic
    def get_or_create_cart(user):
        """Return the user's existing cart or create a new one."""

        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    @transaction.atomic
    def add_item(user, product_id, quantity, variant_id=None):
        """Add a product or variant to the user's cart."""

        if quantity <= 0:
            raise InvalidCartQuantityError(
                "Cart item quantity must be greater than zero."
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist as exc:
            raise ProductNotFoundError(
                "The requested product does not exist."
            ) from exc

        variant = None

        if variant_id is not None:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product,
                )
            except ProductVariant.DoesNotExist as exc:
                raise ProductVariantNotFoundError(
                    "The requested product variant does not exist."
                ) from exc

        cart = CartService.get_or_create_cart(user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={"quantity": quantity},
        )

        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])

        return item

    @staticmethod
    @transaction.atomic
    def update_item(user, item_id, quantity):
        """Update the quantity of an existing cart item."""

        if quantity <= 0:
            raise InvalidCartQuantityError(
                "Cart item quantity must be greater than zero."
            )

        try:
            item = CartItem.objects.select_for_update().get(
                id=item_id,
                cart__user=user,
            )
        except CartItem.DoesNotExist as exc:
            from .exceptions import CartItemNotFoundError

            raise CartItemNotFoundError(
                "The requested cart item does not exist."
            ) from exc

        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])

        return item

    @staticmethod
    @transaction.atomic
    def remove_item(user, item_id):
        """Remove an item from the user's cart."""

        try:
            item = CartItem.objects.get(
                id=item_id,
                cart__user=user,
            )
        except CartItem.DoesNotExist as exc:
            from .exceptions import CartItemNotFoundError

            raise CartItemNotFoundError(
                "The requested cart item does not exist."
            ) from exc

        item.delete()

    @staticmethod
    @transaction.atomic
    def clear_cart(user):
        """Remove all items from the user's cart."""

        cart = Cart.objects.filter(user=user).first()

        if cart:
            cart.items.all().delete()

    @staticmethod
    def get_cart(user):
        """Return the user's cart."""

        return Cart.objects.filter(user=user).prefetch_related(
            "items"
        ).first()