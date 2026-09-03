import pytest
from django.db import IntegrityError


from apps.catalog.models import Category, Product, ProductVariant
from apps.inventory.models import  InventoryItem, StockMovement

from django.core.exceptions import ValidationError
@pytest.fixture
def category(db):
    """Create a category for inventory test data."""

    return Category.objects.create(
        name="Rings",
        slug="rings",
    )


@pytest.fixture
def product(category):
    """Create a product for inventory test data."""

    return Product.objects.create(
        category=category,
        name="Gold Ring",
        slug="gold-ring",
        sku="RING-001",
        weight="2.500",
        purity=750,
    )


@pytest.fixture
def inventory_item(product):
    """Create an inventory item associated with a product."""

    return InventoryItem.objects.create(
        product=product,
        quantity=10,
    )


@pytest.mark.django_db
class TestStockMovementCreation:
    """Test stock movement creation and relationships."""

    def test_create_in_movement(self, inventory_item):
        """An incoming stock movement can be created."""

        movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.IN,
            quantity=10,
        )

        assert movement.pk is not None
        assert movement.inventory_item == inventory_item
        assert movement.movement_type == StockMovement.MovementType.IN
        assert movement.quantity == 10

    def test_create_out_movement(self, inventory_item):
        """An outgoing stock movement can be created."""

        movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.OUT,
            quantity=2,
        )

        assert movement.pk is not None
        assert movement.inventory_item == inventory_item
        assert movement.movement_type == StockMovement.MovementType.OUT
        assert movement.quantity == 2

    def test_create_adjustment_movement(self, inventory_item):
        """An inventory adjustment movement can be created."""

        movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            quantity=3,
        )

        assert movement.pk is not None
        assert movement.inventory_item == inventory_item
        assert movement.movement_type == StockMovement.MovementType.ADJUSTMENT
        assert movement.quantity == 3

    def test_movement_can_store_reference_and_note(self, inventory_item):
        """A movement can store an external reference and an explanatory note."""

        movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.IN,
            quantity=5,
            reference="PURCHASE-001",
            note="Initial stock received from supplier.",
        )

        assert movement.reference == "PURCHASE-001"
        assert movement.note == "Initial stock received from supplier."


@pytest.mark.django_db
class TestStockMovementValidation:
    """Test StockMovement database constraints and validation."""

    def test_quantity_must_be_positive(self, inventory_item):
        """A stock movement cannot contain zero quantity."""

        movement = StockMovement(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.IN,
            quantity=0,
        )

        with pytest.raises(IntegrityError):
            movement.save()

    def test_inventory_item_is_required(self):
        """A stock movement must belong to an inventory item."""

        movement = StockMovement(
            movement_type=StockMovement.MovementType.IN,
            quantity=5,
        )

        with pytest.raises(IntegrityError):
            movement.save()

    def test_movement_type_is_required(self, inventory_item):
        """A stock movement must have a movement type."""

        movement = StockMovement(
            inventory_item=inventory_item,
            quantity=5,
        )

        with pytest.raises(
                ValidationError,
                match="این فیلد نمی تواند خالی باشد",
        ):
            movement.full_clean()
@pytest.mark.django_db
class TestStockMovementRelationships:
    """Test relationships between inventory items and stock movements."""

    def test_inventory_item_has_related_movements(self, inventory_item):
        """InventoryItem exposes its related stock movements."""

        first_movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.IN,
            quantity=10,
        )

        second_movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.OUT,
            quantity=2,
        )

        movements = inventory_item.movements.all()

        assert movements.count() == 2
        assert first_movement in movements
        assert second_movement in movements

    def test_movement_is_protected_from_inventory_deletion(
        self,
        inventory_item,
    ):
        """InventoryItem deletion is protected when movements exist."""

        StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.IN,
            quantity=10,
        )

        with pytest.raises(Exception):
            inventory_item.delete()


@pytest.mark.django_db
class TestStockMovementStringRepresentation:
    """Test StockMovement string representation."""

    def test_string_representation(self, inventory_item):
        """Movement string representation contains key movement information."""

        movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.IN,
            quantity=10,
        )

        assert str(movement) == (
            "Gold Ring - موجودی - ورود - 10"
        )


@pytest.mark.django_db
class TestStockMovementOrdering:
    """Test default movement ordering."""

    def test_movements_are_ordered_by_creation_date_descending(
        self,
        inventory_item,
    ):
        """Newest movements appear first."""

        first_movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.IN,
            quantity=10,
        )

        second_movement = StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type=StockMovement.MovementType.OUT,
            quantity=2,
        )

        movements = list(inventory_item.movements.all())

        assert movements[0] == second_movement
        assert movements[1] == first_movement