"""
Pytest configuration for services tests
"""

import pytest
import os
import sys

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.development')

import django
django.setup()


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (requires running Substrate node)"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )


@pytest.fixture(scope="session")
def django_db_setup():
    """Setup test database"""
    pass


@pytest.fixture
def substrate_url():
    """Substrate node URL for testing"""
    return os.environ.get('SUBSTRATE_WS_URL', 'ws://127.0.0.1:9944')

