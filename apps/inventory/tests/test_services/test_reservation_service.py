import pytest

from apps.catalog.models import Category, Product
from apps.inventory.models import InventoryItem
from apps.inventory.services.reservation_service import ReservationService


@pytest.fixture
def category(db):
    """Create a category for reservation service tests."""

    return Category.objects.create(
        name="Rings",
        slug="rings",
    )


@pytest.fixture
def product(category):
    """Create a product for reservation service tests."""

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
    """Create an inventory item for reservation service tests."""

    return InventoryItem.objects.create(
        product=product,
        quantity=10,
    )


@pytest.mark.django_db
class TestReserve:
    """Test stock reservation operations."""

    def test_reserve_stock(self, inventory_item):
        """Available stock can be reserved."""

        updated_inventory = ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=3,
        )

        assert updated_inventory.quantity == 10
        assert updated_inventory.reserved_quantity == 3
        assert updated_inventory.available_quantity == 7

    def test_reserve_does_not_change_physical_stock(
        self,
        inventory_item,
    ):
        """Reservation does not reduce physical stock."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        inventory_item.refresh_from_db()

        assert inventory_item.quantity == 10
        assert inventory_item.reserved_quantity == 4

    def test_multiple_reservations(self, inventory_item):
        """Multiple reservations accumulate correctly."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=3,
        )

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=2,
        )

        inventory_item.refresh_from_db()

        assert inventory_item.quantity == 10
        assert inventory_item.reserved_quantity == 5
        assert inventory_item.available_quantity == 5

    def test_reserve_rejects_zero_quantity(self, inventory_item):
        """Zero quantity cannot be reserved."""

        with pytest.raises(
            ValueError,
            match="greater than zero",
        ):
            ReservationService.reserve(
                inventory_item_id=inventory_item.id,
                quantity=0,
            )

    def test_reserve_rejects_negative_quantity(self, inventory_item):
        """Negative quantity cannot be reserved."""

        with pytest.raises(
            ValueError,
            match="greater than zero",
        ):
            ReservationService.reserve(
                inventory_item_id=inventory_item.id,
                quantity=-2,
            )

    def test_reserve_rejects_insufficient_available_stock(
        self,
        inventory_item,
    ):
        """Reservation cannot exceed available stock."""

        with pytest.raises(
            ValueError,
            match="Insufficient available stock",
        ):
            ReservationService.reserve(
                inventory_item_id=inventory_item.id,
                quantity=11,
            )

    def test_reserve_respects_existing_reservations(
        self,
        inventory_item,
    ):
        """New reservations cannot consume already reserved stock."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=7,
        )

        with pytest.raises(
            ValueError,
            match="Insufficient available stock",
        ):
            ReservationService.reserve(
                inventory_item_id=inventory_item.id,
                quantity=4,
            )

    def test_reserve_exact_available_quantity(
        self,
        inventory_item,
    ):
        """The entire available stock can be reserved."""

        updated_inventory = ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=10,
        )

        assert updated_inventory.quantity == 10
        assert updated_inventory.reserved_quantity == 10
        assert updated_inventory.available_quantity == 0


@pytest.mark.django_db
class TestRelease:
    """Test stock reservation release operations."""

    def test_release_reservation(self, inventory_item):
        """A reservation can be released."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=5,
        )

        updated_inventory = ReservationService.release(
            inventory_item_id=inventory_item.id,
            quantity=2,
        )

        assert updated_inventory.quantity == 10
        assert updated_inventory.reserved_quantity == 3
        assert updated_inventory.available_quantity == 7

    def test_release_does_not_change_physical_stock(
        self,
        inventory_item,
    ):
        """Releasing a reservation does not change physical stock."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=5,
        )

        ReservationService.release(
            inventory_item_id=inventory_item.id,
            quantity=5,
        )

        inventory_item.refresh_from_db()

        assert inventory_item.quantity == 10
        assert inventory_item.reserved_quantity == 0
        assert inventory_item.available_quantity == 10

    def test_release_entire_reservation(self, inventory_item):
        """The entire reserved quantity can be released."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=6,
        )

        updated_inventory = ReservationService.release(
            inventory_item_id=inventory_item.id,
            quantity=6,
        )

        assert updated_inventory.reserved_quantity == 0
        assert updated_inventory.available_quantity == 10

    def test_release_rejects_zero_quantity(self, inventory_item):
        """Zero quantity cannot be released."""

        with pytest.raises(
            ValueError,
            match="greater than zero",
        ):
            ReservationService.release(
                inventory_item_id=inventory_item.id,
                quantity=0,
            )

    def test_release_rejects_negative_quantity(self, inventory_item):
        """Negative quantity cannot be released."""

        with pytest.raises(
            ValueError,
            match="greater than zero",
        ):
            ReservationService.release(
                inventory_item_id=inventory_item.id,
                quantity=-1,
            )

    def test_release_cannot_exceed_reserved_quantity(
        self,
        inventory_item,
    ):
        """A release cannot exceed the current reserved quantity."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=3,
        )

        with pytest.raises(
            ValueError,
            match="cannot exceed reserved quantity",
        ):
            ReservationService.release(
                inventory_item_id=inventory_item.id,
                quantity=4,
            )


@pytest.mark.django_db
class TestCommit:
    """Test reservation commit operations."""

    def test_commit_reserved_stock(self, inventory_item):
        """A reservation can be committed into a stock deduction."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        updated_inventory = ReservationService.commit(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        assert updated_inventory.quantity == 6
        assert updated_inventory.reserved_quantity == 0
        assert updated_inventory.available_quantity == 6

    def test_commit_reduces_physical_and_reserved_stock(
        self,
        inventory_item,
    ):
        """Commit decreases both physical and reserved quantities."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=7,
        )

        ReservationService.commit(
            inventory_item_id=inventory_item.id,
            quantity=3,
        )

        inventory_item.refresh_from_db()

        assert inventory_item.quantity == 7
        assert inventory_item.reserved_quantity == 4
        assert inventory_item.available_quantity == 3

    def test_commit_cannot_exceed_reserved_quantity(
        self,
        inventory_item,
    ):
        """A commit cannot exceed the reserved quantity."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=3,
        )

        with pytest.raises(
            ValueError,
            match="cannot exceed reserved quantity",
        ):
            ReservationService.commit(
                inventory_item_id=inventory_item.id,
                quantity=4,
            )

    def test_commit_zero_quantity_is_rejected(self, inventory_item):
        """Zero quantity cannot be committed."""

        with pytest.raises(
            ValueError,
            match="greater than zero",
        ):
            ReservationService.commit(
                inventory_item_id=inventory_item.id,
                quantity=0,
            )

    def test_commit_negative_quantity_is_rejected(
        self,
        inventory_item,
    ):
        """Negative quantity cannot be committed."""

        with pytest.raises(
            ValueError,
            match="greater than zero",
        ):
            ReservationService.commit(
                inventory_item_id=inventory_item.id,
                quantity=-2,
            )

    def test_commit_entire_reserved_quantity(
        self,
        inventory_item,
    ):
        """The entire reserved quantity can be committed."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=10,
        )

        updated_inventory = ReservationService.commit(
            inventory_item_id=inventory_item.id,
            quantity=10,
        )

        assert updated_inventory.quantity == 0
        assert updated_inventory.reserved_quantity == 0
        assert updated_inventory.available_quantity == 0


@pytest.mark.django_db
class TestReservationWorkflow:
    """Test complete reservation lifecycle workflows."""

    def test_reserve_then_release(self, inventory_item):
        """A reservation can be created and later released."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        ReservationService.release(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        inventory_item.refresh_from_db()

        assert inventory_item.quantity == 10
        assert inventory_item.reserved_quantity == 0
        assert inventory_item.available_quantity == 10

    def test_reserve_then_commit(self, inventory_item):
        """A reservation can be created and later committed."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        ReservationService.commit(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        inventory_item.refresh_from_db()

        assert inventory_item.quantity == 6
        assert inventory_item.reserved_quantity == 0
        assert inventory_item.available_quantity == 6

    def test_partial_commit_then_release(self, inventory_item):
        """A reservation can be partially committed and released."""

        ReservationService.reserve(
            inventory_item_id=inventory_item.id,
            quantity=6,
        )

        ReservationService.commit(
            inventory_item_id=inventory_item.id,
            quantity=2,
        )

        ReservationService.release(
            inventory_item_id=inventory_item.id,
            quantity=4,
        )

        inventory_item.refresh_from_db()

        assert inventory_item.quantity == 8
        assert inventory_item.reserved_quantity == 0
        assert inventory_item.available_quantity == 8