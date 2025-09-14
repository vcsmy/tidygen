"""
Pytest configuration and fixtures for TidyGen ERP tests.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Permission, Role
from apps.organizations.models import Organization, OrganizationMembership

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up test database with initial data."""
    with django_db_blocker.unblock():
        # Create initial permissions and roles
        call_command('loaddata', 'tests/fixtures/initial_data.json')


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def organization():
    """Create a test organization."""
    return Organization.objects.create(
        name='Test Organization',
        slug='test-org',
        email='contact@testorg.com',
        is_active=True
    )


@pytest.fixture
def organization_membership(user, organization):
    """Create organization membership."""
    return OrganizationMembership.objects.create(
        user=user,
        organization=organization,
        is_owner=True,
        is_active=True
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Create authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create authenticated admin API client."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def permission():
    """Create a test permission."""
    return Permission.objects.create(
        name='Test Permission',
        codename='test_permission',
        description='A test permission',
        module='test'
    )


@pytest.fixture
def role(permission):
    """Create a test role with permission."""
    role = Role.objects.create(
        name='Test Role',
        description='A test role'
    )
    role.permissions.add(permission)
    return role


@pytest.fixture
def web3_wallet_address():
    """Test Web3 wallet address."""
    return '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'


@pytest.fixture
def web3_signature():
    """Test Web3 signature."""
    return '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b'


@pytest.fixture
def web3_message():
    """Test Web3 message."""
    return 'Welcome to TidyGen ERP! Please sign this message to connect your wallet.'


class APITestCase(TestCase):
    """Base test case for API tests."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        self.membership = OrganizationMembership.objects.create(
            user=self.user,
            organization=self.organization,
            is_owner=True
        )
    
    def authenticate_user(self, user=None):
        """Authenticate user for API requests."""
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def create_organization(self, name='Test Org', slug='test-org'):
        """Create a test organization."""
        return Organization.objects.create(
            name=name,
            slug=slug,
            email=f'contact@{slug}.com'
        )
    
    def create_user(self, username='testuser', email='test@example.com'):
        """Create a test user."""
        return User.objects.create_user(
            username=username,
            email=email,
            password='testpass123'
        )
