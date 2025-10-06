"""Conftest for core tests - provides httpx mocking for installer tests."""

from unittest.mock import AsyncMock, Mock, patch

import pytest


@pytest.fixture(scope="function")
def mock_httpx_for_core_tests():
    """Mock httpx.AsyncClient for installer tests.

    Use this fixture explicitly in tests that need httpx mocking.
    """
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"# Test Resource\nMock content"
        mock_response.raise_for_status = Mock()

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        yield mock_client
