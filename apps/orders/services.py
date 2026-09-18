from decimal import Decimal

from django.db import transaction

from apps.inventory.models import InventoryItem
from apps.inventory.services.reservation_service import ReservationService
from apps.pricing.models import PriceSnapshot

from .exceptions import InvalidOrderItemError
from .models import Order, OrderItem, OrderStatus


class OrderService:
    """
    Application service responsible for order business logic.

    Order creation, inventory reservation, cancellation and completion
    are handled here so business rules remain centralized and testable.
    """

    @staticmethod
    def _get_inventory_item(*, product, variant=None):
        """
        Return the inventory item belonging to the selected product
        or product variant.

        A variant has its own inventory record.
        A product without a variant uses the product inventory record.
        """

        if variant is not None:
            inventory_item = (
                InventoryItem.objects
                .filter(
                    variant=variant,
                    product__isnull=True,
                    is_active=True,
                )
                .first()
            )
        else:
            inventory_item = (
                InventoryItem.objects
                .filter(
                    product=product,
                    variant__isnull=True,
                    is_active=True,
                )
                .first()
            )

        if inventory_item is None:
            raise InvalidOrderItemError(
                "Inventory record was not found for this item."
            )

        return inventory_item

    @staticmethod
    @transaction.atomic
    def create_order(
        *,
        user=None,
        customer_name,
        customer_phone,
        shipping_address,
        items,
        shipping_cost=Decimal("0"),
        discount=Decimal("0"),
        tax=Decimal("0"),
    ):
        """
        Create an order and reserve its inventory atomically.

        Orders may be created by either authenticated users or guest
        customers. Guest orders are initially created without a user
        account and can be associated with a user after successful
        payment.

        If any item fails during creation or reservation, the complete
        transaction is rolled back.
        """

        if not items:
            raise InvalidOrderItemError(
                "Order must contain at least one item."
            )

        if discount < 0:
            raise InvalidOrderItemError(
                "Discount cannot be negative."
            )

        if shipping_cost < 0:
            raise InvalidOrderItemError(
                "Shipping cost cannot be negative."
            )

        if tax < 0:
            raise InvalidOrderItemError(
                "Tax cannot be negative."
            )

        order = Order.objects.create(
            user=user,
            customer_name=customer_name,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            shipping_cost=shipping_cost,
            discount=discount,
            tax=tax,
        )

        subtotal = Decimal("0")

        for item in items:
            product = item["product"]
            variant = item.get("variant")
            quantity = item["quantity"]

            if quantity <= 0:
                raise InvalidOrderItemError(
                    "Item quantity must be greater than zero."
                )

            # Ensure the selected variant belongs to the selected product.
            if (
                variant is not None
                and variant.product_id != product.id
            ):
                raise InvalidOrderItemError(
                    "Variant does not belong to the selected product."
                )

            # Resolve the inventory record before reservation.
            inventory_item = OrderService._get_inventory_item(
                product=product,
                variant=variant,
            )

            # Retrieve the immutable pricing snapshot.
            try:
                price_snapshot = PriceSnapshot.objects.get(
                    pk=item["price_snapshot_id"]
                )
            except PriceSnapshot.DoesNotExist as exc:
                raise InvalidOrderItemError(
                    "Price snapshot was not found."
                ) from exc

            unit_price = price_snapshot.final_price
            total_price = unit_price * quantity

            subtotal += total_price

            # Reserve inventory.
            # ReservationService handles row-level locking and
            # prevents concurrent over-reservation.
            try:
                ReservationService.reserve(
                    inventory_item_id=inventory_item.pk,
                    quantity=quantity,
                )
            except ValueError as exc:
                raise InvalidOrderItemError(
                    str(exc)
                ) from exc

            # Resolve historical catalog values.
            weight = (
                variant.weight
                if variant is not None
                and variant.weight is not None
                else product.weight
            )

            sku = (
                variant.sku
                if variant is not None
                else product.sku
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                product_name_snapshot=product.name,
                sku_snapshot=sku,
                weight_snapshot=weight,
                purity_snapshot=product.purity,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                price_snapshot=price_snapshot,
            )

        total_amount = (
            subtotal
            - discount
            + shipping_cost
            + tax
        )

        if total_amount < 0:
            raise InvalidOrderItemError(
                "Order total cannot be negative."
            )

        order.subtotal = subtotal
        order.total_amount = total_amount

        order.save(
            update_fields=[
                "subtotal",
                "total_amount",
                "updated_at",
            ]
        )

        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(*, order):
        """
        Cancel an order and release all reserved inventory.

        Delivered orders cannot be cancelled because their inventory
        reservation has already been committed.
        """

        if order.status == OrderStatus.DELIVERED:
            raise InvalidOrderItemError(
                "Delivered orders cannot be cancelled."
            )

        if order.status == OrderStatus.CANCELLED:
            return order

        items = order.items.select_related(
            "product",
            "variant",
        )

        for item in items:
            inventory_item = OrderService._get_inventory_item(
                product=item.product,
                variant=item.variant,
            )

            try:
                ReservationService.release(
                    inventory_item_id=inventory_item.pk,
                    quantity=item.quantity,
                )
            except ValueError as exc:
                raise InvalidOrderItemError(
                    str(exc)
                ) from exc

        order.status = OrderStatus.CANCELLED

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return order

    @staticmethod
    @transaction.atomic
    def complete_order(*, order):
        """
        Complete an order by committing all inventory reservations.

        ReservationService.commit() decreases both physical stock and
        reserved stock atomically.
        """

        if order.status == OrderStatus.CANCELLED:
            raise InvalidOrderItemError(
                "Cancelled orders cannot be completed."
            )

        if order.status == OrderStatus.DELIVERED:
            return order

        items = order.items.select_related(
            "product",
            "variant",
        )

        for item in items:
            inventory_item = OrderService._get_inventory_item(
                product=item.product,
                variant=item.variant,
            )

            try:
                ReservationService.commit(
                    inventory_item_id=inventory_item.pk,
                    quantity=item.quantity,
                    reference=f"ORDER-{order.pk}",
                    note="Inventory committed for completed order.",
                )
            except ValueError as exc:
                raise InvalidOrderItemError(
                    str(exc)
                ) from exc

        order.status = OrderStatus.DELIVERED

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return order