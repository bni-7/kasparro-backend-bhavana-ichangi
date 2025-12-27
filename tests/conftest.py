"""Test configuration and fixtures."""
import pytest


@pytest.fixture(scope="session")
def test_settings():
    """Test settings fixture."""
    return {
        "database_url": "sqlite:///./test.db",
        "max_retries": 3,
        "initial_retry_delay": 0.1,  # Faster for tests
        "rate_limit_delay": 0.1,
    }
