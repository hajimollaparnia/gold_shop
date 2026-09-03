import pytest

from apps.inventory.models import InventoryItem, StockMovement
from apps.inventory.services.stock_service import StockService


@pytest.fixture
def category(db):
    """Create a category for stock service tests."""

    from apps.catalog.models import Category

    return Category.objects.create(
        name="Rings",
        slug="rings",
    )


@pytest.fixture
def product(category):
    """Create a product for stock service tests."""

    from apps.catalog.models import Product

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
    """Create an inventory item for stock service tests."""

    return InventoryItem.objects.create(
        product=product,
        quantity=10,
    )


@pytest.mark.django_db
class TestIncreaseStock:
    """Test stock increase operations."""

    def test_increase_stock(self, inventory_item):
        """Stock quantity increases correctly."""

        updated_inventory = StockService.increase_stock(
            inventory_item_id=inventory_item.id,
            quantity=5,
        )

        assert updated_inventory.quantity == 15
        assert updated_inventory.reserved_quantity == 0

    def test_increase_stock_creates_movement(self, inventory_item):
        """Increasing stock creates an incoming movement."""

        StockService.increase_stock(
            inventory_item_id=inventory_item.id,
            quantity=5,
            reference="PURCHASE-001",
            note="Stock received.",
        )

        movement = StockMovement.objects.get(
            inventory_item=inventory_item,
        )

        assert movement.movement_type == StockMovement.MovementType.IN
        assert movement.quantity == 5
        assert movement.reference == "PURCHASE-001"
        assert movement.note == "Stock received."

    def test_increase_stock_rejects_zero_quantity(self, inventory_item):
        """Zero quantity cannot be added."""

        with pytest.raises(ValueError, match="greater than zero"):
            StockService.increase_stock(
                inventory_item_id=inventory_item.id,
                quantity=0,
            )

    def test_increase_stock_rejects_negative_quantity(self, inventory_item):
        """Negative quantity cannot be added."""

        with pytest.raises(ValueError, match="greater than zero"):
            StockService.increase_stock(
                inventory_item_id=inventory_item.id,
                quantity=-5,
            )


@pytest.mark.django_db
class TestDecreaseStock:
    """Test stock decrease operations."""

    def test_decrease_stock(self, inventory_item):
        """Stock quantity decreases correctly."""

        updated_inventory = StockService.decrease_stock(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        assert updated_inventory.quantity == 6
        assert updated_inventory.reserved_quantity == 0

    def test_decrease_stock_creates_movement(self, inventory_item):
        """Decreasing stock creates an outgoing movement."""

        StockService.decrease_stock(
            inventory_item_id=inventory_item.id,
            quantity=4,
            reference="ORDER-001",
            note="Order fulfilled.",
        )

        movement = StockMovement.objects.get(
            inventory_item=inventory_item,
        )

        assert movement.movement_type == StockMovement.MovementType.OUT
        assert movement.quantity == 4
        assert movement.reference == "ORDER-001"
        assert movement.note == "Order fulfilled."

    def test_decrease_stock_rejects_insufficient_stock(
        self,
        inventory_item,
    ):
        """Stock cannot be decreased below available quantity."""

        with pytest.raises(ValueError, match="Insufficient available stock"):
            StockService.decrease_stock(
                inventory_item_id=inventory_item.id,
                quantity=11,
            )

    def test_decrease_stock_respects_reserved_quantity(
        self,
        inventory_item,
    ):
        """Reserved stock cannot be consumed by normal decrease."""

        inventory_item.reserved_quantity = 7
        inventory_item.save(update_fields=["reserved_quantity"])

        with pytest.raises(ValueError, match="Insufficient available stock"):
            StockService.decrease_stock(
                inventory_item_id=inventory_item.id,
                quantity=4,
            )

    def test_decrease_stock_rejects_zero_quantity(self, inventory_item):
        """Zero quantity cannot be removed."""

        with pytest.raises(ValueError, match="greater than zero"):
            StockService.decrease_stock(
                inventory_item_id=inventory_item.id,
                quantity=0,
            )

    def test_decrease_stock_rejects_negative_quantity(self, inventory_item):
        """Negative quantity cannot be removed."""

        with pytest.raises(ValueError, match="greater than zero"):
            StockService.decrease_stock(
                inventory_item_id=inventory_item.id,
                quantity=-2,
            )


@pytest.mark.django_db
class TestAdjustStock:
    """Test inventory adjustment operations."""

    def test_positive_adjustment_increases_stock(self, inventory_item):
        """A positive adjustment increases stock."""

        updated_inventory = StockService.adjust_stock(
            inventory_item_id=inventory_item.id,
            quantity=5,
        )

        assert updated_inventory.quantity == 15

    def test_negative_adjustment_decreases_stock(self, inventory_item):
        """A negative adjustment decreases stock."""

        updated_inventory = StockService.adjust_stock(
            inventory_item_id=inventory_item.id,
            quantity=-3,
        )

        assert updated_inventory.quantity == 7

    def test_adjustment_creates_movement(self, inventory_item):
        """An adjustment creates an adjustment movement."""

        StockService.adjust_stock(
            inventory_item_id=inventory_item.id,
            quantity=5,
            reference="ADJUST-001",
            note="Physical inventory correction.",
        )

        movement = StockMovement.objects.get(
            inventory_item=inventory_item,
        )

        assert (
            movement.movement_type
            == StockMovement.MovementType.ADJUSTMENT
        )
        assert movement.quantity == 5
        assert movement.reference == "ADJUST-001"
        assert movement.note == "Physical inventory correction."

    def test_adjustment_quantity_cannot_be_zero(self, inventory_item):
        """An adjustment cannot have zero quantity."""

        with pytest.raises(ValueError, match="cannot be zero"):
            StockService.adjust_stock(
                inventory_item_id=inventory_item.id,
                quantity=0,
            )

    def test_adjustment_cannot_reduce_below_reserved_quantity(
        self,
        inventory_item,
    ):
        """Adjustment cannot reduce stock below reserved quantity."""

        inventory_item.reserved_quantity = 8
        inventory_item.save(update_fields=["reserved_quantity"])

        with pytest.raises(
            ValueError,
            match="cannot be lower than reserved quantity",
        ):
            StockService.adjust_stock(
                inventory_item_id=inventory_item.id,
                quantity=-3,
            )

    def test_multiple_stock_operations_are_recorded(
        self,
        inventory_item,
    ):
        """Every stock operation creates an audit movement."""

        StockService.increase_stock(
            inventory_item_id=inventory_item.id,
            quantity=5,
        )

        StockService.decrease_stock(
            inventory_item_id=inventory_item.id,
            quantity=3,
        )

        StockService.adjust_stock(
            inventory_item_id=inventory_item.id,
            quantity=2,
        )

        assert StockMovement.objects.filter(
            inventory_item=inventory_item,
        ).count() == 3

        inventory_item.refresh_from_db()

        assert inventory_item.quantity == 14