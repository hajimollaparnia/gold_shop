import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.cart.models import Cart
from apps.catalog.models import Category, Product, ProductVariant


@pytest.fixture
def user(db):
    return User.objects.create_user(
        phone_number="09120000001",
        password="TestPassword123!",
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Rings",
    )


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        category=category,
        name="Gold Ring",
        sku="RING-001",
        weight=5,
        purity=750,
    )


@pytest.fixture
def variant(db, product):
    return ProductVariant.objects.create(
        product=product,
        sku="RING-001-18K",
        weight=5,
    )


@pytest.fixture
def cart(db, user):
    return Cart.objects.create(user=user)