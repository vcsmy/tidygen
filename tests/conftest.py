"""
Pytest configuration and fixtures for TidyGen Community tests.
"""

import os
import subprocess
import pytest


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Add custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line("markers", "substrate: marks tests that require Substrate node")
    config.addinivalue_line("markers", "web3: marks tests that require Web3 functionality")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names and content."""
    for item in items:
        # Add slow marker to integration tests by default
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.integration)
        
        # Add docker marker to tests that check for Docker
        if "docker" in item.nodeid.lower() or "quickstart" in item.nodeid.lower():
            item.add_marker(pytest.mark.docker)
        
        # Add substrate marker to substrate-related tests
        if "substrate" in item.nodeid.lower():
            item.add_marker(pytest.mark.substrate)


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def docker_available():
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.fixture(scope="session")
def docker_compose_available():
    """Check if Docker Compose is available."""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def pytest_runtest_setup(item):
    """Setup for each test run."""
    # Skip Docker-dependent tests if Docker is not available
    if item.get_closest_marker("docker") and not docker_available():
        pytest.skip("Docker is not available or not running")
    
    # Skip Substrate-dependent tests if Docker is not available
    if item.get_closest_marker("substrate") and not docker_available():
        pytest.skip("Docker is required for Substrate tests")