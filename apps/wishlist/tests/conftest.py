import pytest

from apps.accounts.models import User
from apps.catalog.models import Category, Product, ProductVariant


@pytest.fixture
def user(db):
    """Create a user for wishlist tests."""

    return User.objects.create_user(
        phone_number="09130000001",
        password="TestPassword123!",
    )


@pytest.fixture
def second_user(db):
    """Create a second user for ownership tests."""

    return User.objects.create_user(
        phone_number="09130000002",
        password="TestPassword123!",
    )


@pytest.fixture
def category(db):
    """Create a catalog category for wishlist tests."""

    return Category.objects.create(
        name="Rings",
    )


@pytest.fixture
def product(db, category):
    """Create a product for wishlist tests."""

    return Product.objects.create(
        category=category,
        name="Gold Ring",
        sku="WISH-RING-001",
        weight=5,
        purity=750,
    )


@pytest.fixture
def variant(db, product):
    """Create a product variant for wishlist tests."""

    return ProductVariant.objects.create(
        product=product,
        sku="WISH-RING-001-18K",
        weight=5,
    )