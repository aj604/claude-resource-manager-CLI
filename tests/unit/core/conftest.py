"""Conftest for installer tests - provides httpx mocking."""

import pytest
from unittest.mock import AsyncMock, Mock, patch


@pytest.fixture(autouse=True)
def mock_httpx_for_installer(request):
    """Auto-mock httpx.AsyncClient for all installer tests unless explicitly patched."""
    # Check if test already has httpx mocking (by checking for patch in test)
    if 'httpx' in str(request.function):
        # If the test manually patches httpx, skip auto-mocking
        for marker in request.node.iter_markers():
            if hasattr(marker, 'args') and 'httpx' in str(marker.args):
                yield
                return

    # Auto-mock httpx for tests that don't manually mock it
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"# Test Resource\nMock content"
        mock_response.raise_for_status = Mock()

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        yield mock_client
