from django.db import transaction
from django.db.models import F

from apps.inventory.models import InventoryItem, StockMovement


class StockService:
    """
    Application service responsible for inventory stock operations.

    All stock modifications are performed inside database transactions
    and protected with row-level locking to prevent race conditions
    during concurrent inventory updates.
    """

    @staticmethod
    @transaction.atomic
    def increase_stock(
        inventory_item_id: int,
        quantity: int,
        reference: str = "",
        note: str = "",
    ) -> InventoryItem:
        """
        Increase the available stock of an inventory item.

        A corresponding incoming StockMovement is created for auditing.
        """

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        inventory_item = (
            InventoryItem.objects
            .select_for_update()
            .get(pk=inventory_item_id)
        )

        InventoryItem.objects.filter(
            pk=inventory_item.pk,
        ).update(
            quantity=F("quantity") + quantity,
        )

        StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.IN,
            quantity=quantity,
            reference=reference,
            note=note,
        )

        inventory_item.refresh_from_db()

        return inventory_item

    @staticmethod
    @transaction.atomic
    def decrease_stock(
        inventory_item_id: int,
        quantity: int,
        reference: str = "",
        note: str = "",
    ) -> InventoryItem:
        """
        Decrease available stock of an inventory item.

        Reserved stock cannot be consumed by a normal stock decrease.
        A corresponding outgoing StockMovement is created for auditing.
        """

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        inventory_item = (
            InventoryItem.objects
            .select_for_update()
            .get(pk=inventory_item_id)
        )

        available_quantity = (
            inventory_item.quantity
            - inventory_item.reserved_quantity
        )

        if quantity > available_quantity:
            raise ValueError("Insufficient available stock.")

        InventoryItem.objects.filter(
            pk=inventory_item.pk,
        ).update(
            quantity=F("quantity") - quantity,
        )

        StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.OUT,
            quantity=quantity,
            reference=reference,
            note=note,
        )

        inventory_item.refresh_from_db()

        return inventory_item

    @staticmethod
    @transaction.atomic
    def adjust_stock(
        inventory_item_id: int,
        quantity: int,
        reference: str = "",
        note: str = "",
    ) -> InventoryItem:
        """
        Adjust inventory quantity by a signed amount.

        Positive values increase stock.
        Negative values decrease stock.

        The resulting quantity must never become lower than the
        reserved quantity.
        """

        if quantity == 0:
            raise ValueError("Adjustment quantity cannot be zero.")

        inventory_item = (
            InventoryItem.objects
            .select_for_update()
            .get(pk=inventory_item_id)
        )

        new_quantity = inventory_item.quantity + quantity

        if new_quantity < inventory_item.reserved_quantity:
            raise ValueError(
                "Adjusted quantity cannot be lower than reserved quantity."
            )

        InventoryItem.objects.filter(
            pk=inventory_item.pk,
        ).update(
            quantity=F("quantity") + quantity,
        )

        StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            quantity=abs(quantity),
            reference=reference,
            note=note,
        )

        inventory_item.refresh_from_db()

        return inventory_item