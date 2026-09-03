import pytest
from django.db import IntegrityError

from apps.catalog.models import Category, Product, ProductVariant
from apps.inventory.models import InventoryItem


@pytest.mark.django_db
class TestInventoryItemCreation:
    """Test InventoryItem creation and basic relationships."""

    def test_create_inventory_for_product(self):
        """An inventory item can be created for a product."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        inventory = InventoryItem.objects.create(
            product=product,
            quantity=10,
        )

        assert inventory.pk is not None
        assert inventory.product == product
        assert inventory.variant is None
        assert inventory.quantity == 10
        assert inventory.reserved_quantity == 0

    def test_create_inventory_for_product_variant(self):
        """An inventory item can be created for a product variant."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        variant = ProductVariant.objects.create(
            product=product,
            sku="RING-001-S16",
            weight="2.500",
        )

        inventory = InventoryItem.objects.create(
            variant=variant,
            quantity=5,
        )

        assert inventory.pk is not None
        assert inventory.variant == variant
        assert inventory.product is None
        assert inventory.quantity == 5
        assert inventory.reserved_quantity == 0


@pytest.mark.django_db
class TestInventoryItemAvailableQuantity:
    """Test available inventory calculation."""

    def test_available_quantity_without_reservation(self):
        """Available quantity equals total quantity when nothing is reserved."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        inventory = InventoryItem.objects.create(
            product=product,
            quantity=10,
        )

        assert inventory.available_quantity == 10

    def test_available_quantity_with_reservation(self):
        """Reserved quantity is excluded from available inventory."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        inventory = InventoryItem.objects.create(
            product=product,
            quantity=10,
            reserved_quantity=3,
        )

        assert inventory.available_quantity == 7

    def test_available_quantity_when_all_stock_is_reserved(self):
        """Available quantity becomes zero when all stock is reserved."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        inventory = InventoryItem.objects.create(
            product=product,
            quantity=5,
            reserved_quantity=5,
        )

        assert inventory.available_quantity == 0


@pytest.mark.django_db
class TestInventoryItemConstraints:
    """Test database-level inventory constraints."""

    def test_product_and_variant_cannot_be_set_together(self):
        """An inventory item cannot belong to both product and variant."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        variant = ProductVariant.objects.create(
            product=product,
            sku="RING-001-S16",
            weight="2.500",
        )

        inventory = InventoryItem(
            product=product,
            variant=variant,
            quantity=10,
        )

        with pytest.raises(IntegrityError):
            inventory.save()

    def test_product_and_variant_cannot_both_be_empty(self):
        """An inventory item must belong to either a product or a variant."""

        inventory = InventoryItem(
            quantity=10,
        )

        with pytest.raises(IntegrityError):
            inventory.save()

    def test_reserved_quantity_cannot_exceed_quantity(self):
        """Reserved inventory cannot exceed total inventory."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        inventory = InventoryItem(
            product=product,
            quantity=5,
            reserved_quantity=6,
        )

        with pytest.raises(IntegrityError):
            inventory.save()

    def test_only_one_inventory_item_per_product(self):
        """A product cannot have multiple inventory records."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        InventoryItem.objects.create(
            product=product,
            quantity=10,
        )

        with pytest.raises(IntegrityError):
            InventoryItem.objects.create(
                product=product,
                quantity=5,
            )

    def test_only_one_inventory_item_per_variant(self):
        """A product variant cannot have multiple inventory records."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        variant = ProductVariant.objects.create(
            product=product,
            sku="RING-001-S16",
            weight="2.500",
        )

        InventoryItem.objects.create(
            variant=variant,
            quantity=5,
        )

        with pytest.raises(IntegrityError):
            InventoryItem.objects.create(
                variant=variant,
                quantity=3,
            )


@pytest.mark.django_db
class TestInventoryItemStringRepresentation:
    """Test InventoryItem string representation."""

    def test_product_inventory_string(self):
        """Product inventory should contain the product name."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        inventory = InventoryItem.objects.create(
            product=product,
            quantity=10,
        )

        assert str(inventory) == "Gold Ring - موجودی"

    def test_variant_inventory_string(self):
        """Variant inventory should contain the variant representation."""

        category = Category.objects.create(
            name="Rings",
            slug="rings",
        )

        product = Product.objects.create(
            category=category,
            name="Gold Ring",
            slug="gold-ring",
            sku="RING-001",
            weight="2.500",
            purity=750,
        )

        variant = ProductVariant.objects.create(
            product=product,
            sku="RING-001-S16",
            weight="2.500",
        )

        inventory = InventoryItem.objects.create(
            variant=variant,
            quantity=5,
        )

        assert str(inventory) == (
            "Gold Ring - RING-001-S16 - موجودی"
        )