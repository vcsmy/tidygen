"""
Pytest configuration and fixtures.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


@pytest.fixture
def user():
    """User fixture."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Admin user fixture."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def freelancer_user():
    """User with freelancer profile fixture."""
    user = User.objects.create_user(
        username='freelancer',
        email='freelancer@example.com',
        password='testpass123',
        first_name='John',
        last_name='Freelancer'
    )
    return user


@pytest.fixture
def client_user():
    """User who posts jobs fixture."""
    return User.objects.create_user(
        username='client',
        email='client@example.com',
        password='testpass123',
        first_name='Jane',
        last_name='Client'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Authenticated API client fixture."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Admin API client fixture."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'first_name': 'New',
        'last_name': 'User',
        'password': 'newpass123',
        'password_confirm': 'newpass123'
    }


@pytest.fixture
def sample_freelancer_data():
    """Sample freelancer data for testing."""
    return {
        'first_name': 'John',
        'last_name': 'Freelancer',
        'date_of_birth': '1990-01-01',
        'personal_email': 'john@example.com',
        'personal_phone': '+1234567890',
        'address_line1': '123 Main St',
        'city': 'New York',
        'state': 'NY',
        'postal_code': '10001',
        'country': 'US',
        'cleaning_types': ['residential', 'commercial'],
        'hourly_rate': 25.00,
        'currency': 'USD'
    }


@pytest.fixture
def mock_web3_provider(mocker):
    """Mock Web3 provider for testing."""
    mock_provider = mocker.Mock()
    mock_provider.is_connected.return_value = True
    mock_provider.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
    return mock_provider


@pytest.fixture
def mock_wallet_address():
    """Mock wallet address for testing."""
    return '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'


@pytest.fixture
def freelancer_profile(freelancer_user, sample_freelancer_data):
    """Freelancer profile fixture."""
    from apps.freelancers.models import Freelancer
    return Freelancer.objects.create(
        user=freelancer_user,
        **sample_freelancer_data
    )


@pytest.fixture
def gig_category():
    """Gig category fixture."""
    from apps.gig_management.models import GigCategory
    return GigCategory.objects.create(
        name='Residential Cleaning',
        description='Home cleaning services',
        default_hourly_rate_min=20.00,
        default_hourly_rate_max=50.00
    )


@pytest.fixture
def gig_job(client_user, gig_category):
    """Gig job fixture."""
    from apps.gig_management.models import GigJob
    return GigJob.objects.create(
        title='House Cleaning Service',
        description='Regular house cleaning for 2-bedroom apartment',
        category=gig_category,
        client=client_user,
        client_type='individual',
        service_address='456 Oak St',
        city='New York',
        state='NY',
        postal_code='10002',
        country='US',
        service_type='regular_cleaning',
        property_type='apartment',
        payment_method='hourly',
        hourly_rate=35.00,
        currency='USD',
        estimated_duration_hours=4.0
    )


@pytest.fixture
def payment_method():
    """Payment method fixture."""
    from apps.contractor_payments.models import PaymentMethod
    return PaymentMethod.objects.create(
        name='Bank Transfer',
        payment_type='bank_transfer',
        processing_fee_percentage=1.5,
        min_payment_amount=10.00,
        max_payment_amount=10000.00,
        supported_currencies=['USD', 'EUR']
    )


class BaseTestCase(TestCase):
    """Base test case with common setup."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Organization setup removed for community version
        self.client = APIClient()
        
    def authenticate_user(self, user=None):
        """Authenticate a user for API requests."""
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
