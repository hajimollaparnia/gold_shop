from django.db import transaction
from django.db.models import F

from apps.inventory.models import InventoryItem


class ReservationService:
    """
    Application service responsible for inventory reservations.

    Reservations temporarily reduce the available stock without
    reducing the physical inventory quantity.

    All reservation operations use database transactions and row-level
    locking to prevent concurrent requests from over-reserving stock.
    """

    @staticmethod
    @transaction.atomic
    def reserve(
        inventory_item_id: int,
        quantity: int,
    ) -> InventoryItem:
        """
        Reserve available stock for an inventory item.

        Reserved quantity is increased while the physical stock
        quantity remains unchanged.

        Raises:
            ValueError: If quantity is not positive or available stock
                is insufficient.
            InventoryItem.DoesNotExist: If the inventory item does not
                exist.
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
            reserved_quantity=F("reserved_quantity") + quantity,
        )

        inventory_item.refresh_from_db()

        return inventory_item

    @staticmethod
    @transaction.atomic
    def release(
        inventory_item_id: int,
        quantity: int,
    ) -> InventoryItem:
        """
        Release a previously reserved quantity.

        Physical stock remains unchanged while reserved stock is
        decreased.

        Raises:
            ValueError: If quantity is not positive or exceeds the
                currently reserved quantity.
            InventoryItem.DoesNotExist: If the inventory item does not
                exist.
        """

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        inventory_item = (
            InventoryItem.objects
            .select_for_update()
            .get(pk=inventory_item_id)
        )

        if quantity > inventory_item.reserved_quantity:
            raise ValueError(
                "Release quantity cannot exceed reserved quantity."
            )

        InventoryItem.objects.filter(
            pk=inventory_item.pk,
        ).update(
            reserved_quantity=F("reserved_quantity") - quantity,
        )

        inventory_item.refresh_from_db()

        return inventory_item

    @staticmethod
    @transaction.atomic
    def commit(
        inventory_item_id: int,
        quantity: int,
    ) -> InventoryItem:
        """
        Commit a reservation into a completed stock deduction.

        Both physical quantity and reserved quantity are decreased
        by the committed amount.

        Raises:
            ValueError: If quantity is not positive or exceeds the
                currently reserved quantity.
            InventoryItem.DoesNotExist: If the inventory item does not
                exist.
        """

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        inventory_item = (
            InventoryItem.objects
            .select_for_update()
            .get(pk=inventory_item_id)
        )

        if quantity > inventory_item.reserved_quantity:
            raise ValueError(
                "Commit quantity cannot exceed reserved quantity."
            )

        InventoryItem.objects.filter(
            pk=inventory_item.pk,
        ).update(
            quantity=F("quantity") - quantity,
            reserved_quantity=F("reserved_quantity") - quantity,
        )

        inventory_item.refresh_from_db()

        return inventory_item