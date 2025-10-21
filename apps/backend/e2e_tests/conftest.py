import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


@pytest.fixture
def live_server_db(live_server):
    """
    Fixture that provides a live server with database access.
    """
    return live_server


@pytest.fixture
def test_user(db):
    """
    Create a test user for E2E tests.
    """
    return User.objects.create_user(
        username='e2etest',
        email='e2etest@example.com',
        first_name='E2E',
        last_name='Test',
        password='e2etestpass123'
    )


@pytest.fixture
def authenticated_user(db):
    """
    Create and return an authenticated user for tests.
    """
    user = User.objects.create_user(
        username='authtest',
        email='authtest@example.com',
        first_name='Auth',
        last_name='Test',
        password='authtestpass123'
    )
    return user
