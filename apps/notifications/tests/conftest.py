import pytest

from apps.accounts.models import User


@pytest.fixture
def user(db):
    """Create a user for notification tests."""

    return User.objects.create_user(
        phone_number="09150000001",
        password="TestPassword123!",
    )


@pytest.fixture
def second_user(db):
    """Create a second user for ownership tests."""

    return User.objects.create_user(
        phone_number="09150000002",
        password="TestPassword123!",
    )