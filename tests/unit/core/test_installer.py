"""Tests for AsyncInstaller - async downloads and atomic writes.

These tests ensure secure installation with atomic file operations.
Tests will FAIL until Installer is implemented.
"""

from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, Mock, patch
import pytest
import httpx


class TestAsyncInstaller:
    """Tests for AsyncInstaller with async operations."""

    @pytest.mark.asyncio
    async def test_WHEN_resource_installed_THEN_file_created(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Valid resource to install
        WHEN: Installer installs the resource
        THEN: File is created in correct location
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        result = await installer.install(sample_resource_data)

        assert result.success is True
        assert result.path.exists()
        assert result.path.parent.name == "agents"

    @pytest.mark.asyncio
    async def test_WHEN_download_fails_THEN_retries(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Download that fails initially
        WHEN: Installer attempts installation
        THEN: Retries up to 3 times before failing
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        # Mock httpx to fail twice, then succeed
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error", request=Mock(), response=mock_response
            )

            mock_client.return_value.__aenter__.return_value.get.side_effect = [
                mock_response,  # First attempt fails
                mock_response,  # Second attempt fails
                AsyncMock(status_code=200, content=b"success"),  # Third succeeds
            ]

            result = await installer.install(sample_resource_data)

            # Should eventually succeed after retries
            assert mock_client.return_value.__aenter__.return_value.get.call_count <= 3

    @pytest.mark.asyncio
    async def test_WHEN_download_succeeds_THEN_content_written(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Successful download
        WHEN: Content is retrieved
        THEN: Content is written to file
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        expected_content = b"# Test Resource\nThis is test content"

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = expected_content
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await installer.install(sample_resource_data)

            # Verify file content
            assert result.path.read_bytes() == expected_content

    @pytest.mark.asyncio
    async def test_WHEN_atomic_write_THEN_temp_file_used(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource to install
        WHEN: Installer writes file
        THEN: Uses atomic write (temp file + rename)
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b"test"
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            # Track temp files created during write
            with patch("pathlib.Path.rename") as mock_rename:
                await installer.install(sample_resource_data)

                # Should have called rename (atomic operation)
                assert mock_rename.called

    @pytest.mark.asyncio
    async def test_WHEN_write_fails_THEN_temp_deleted(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Write operation that fails
        WHEN: Installer attempts to write
        THEN: Temporary file is cleaned up
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b"test"
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            # Mock rename to fail
            with patch("pathlib.Path.rename", side_effect=OSError("Disk full")):
                result = await installer.install(sample_resource_data)

                assert result.success is False
                # Temp file should not exist
                temp_files = list(temp_install_dir.rglob("*.tmp"))
                assert len(temp_files) == 0

    @pytest.mark.asyncio
    async def test_WHEN_network_timeout_THEN_error_raised(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Network request that times out
        WHEN: Installer attempts download
        THEN: Timeout error is raised
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir, timeout=1.0)

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                httpx.TimeoutException("Timeout")
            )

            result = await installer.install(sample_resource_data)

            assert result.success is False
            assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_WHEN_invalid_url_THEN_error_raised(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource with invalid URL
        WHEN: Installer attempts download
        THEN: Validation error is raised
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        # Set invalid URL
        sample_resource_data["source"]["url"] = "not-a-valid-url"

        result = await installer.install(sample_resource_data)

        assert result.success is False
        assert "url" in result.error.lower() or "invalid" in result.error.lower()

    @pytest.mark.asyncio
    async def test_WHEN_disk_full_THEN_error_raised(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Disk full condition
        WHEN: Installer attempts to write
        THEN: Disk full error is raised
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b"test"
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            # Mock write to raise OSError (disk full)
            with patch("pathlib.Path.write_bytes", side_effect=OSError("[Errno 28] No space left")):
                result = await installer.install(sample_resource_data)

                assert result.success is False
                assert "space" in result.error.lower() or "disk" in result.error.lower()

    @pytest.mark.asyncio
    async def test_WHEN_concurrent_installs_THEN_no_race_condition(
        self, temp_install_dir: Path, mock_catalog_331_resources: list
    ):
        """
        GIVEN: Multiple resources to install concurrently
        WHEN: Installer processes them in parallel
        THEN: No race conditions, all succeed
        """
        import asyncio
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        # Take first 10 resources
        resources = mock_catalog_331_resources[:10]

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b"test content"
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            # Install all concurrently
            tasks = [installer.install(r) for r in resources]
            results = await asyncio.gather(*tasks)

            # All should succeed
            assert all(r.success for r in results)

            # No duplicate files
            all_files = list(temp_install_dir.rglob("*.*"))
            assert len(all_files) == len(resources)

    @pytest.mark.asyncio
    async def test_WHEN_dependency_chain_THEN_topological_order(
        self, temp_install_dir: Path
    ):
        """
        GIVEN: Resources with dependency chain
        WHEN: Installer installs with dependencies
        THEN: Installation follows topological order
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        # A depends on B, B depends on C
        resource_a = {
            "id": "a",
            "type": "agent",
            "dependencies": {"required": ["b"]},
        }
        resource_b = {
            "id": "b",
            "type": "agent",
            "dependencies": {"required": ["c"]},
        }
        resource_c = {
            "id": "c",
            "type": "agent",
            "dependencies": {"required": []},
        }

        install_order = []

        async def track_install(resource):
            install_order.append(resource["id"])
            return Mock(success=True)

        installer.install = track_install

        await installer.install_with_dependencies(resource_a)

        # Should install in order: c, b, a
        assert install_order == ["c", "b", "a"]

    @pytest.mark.asyncio
    async def test_WHEN_already_installed_THEN_skipped(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource already installed
        WHEN: Installer attempts to install again
        THEN: Installation is skipped (idempotent)
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b"test"
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            # First install
            result1 = await installer.install(sample_resource_data)
            assert result1.success is True

            # Second install (should skip)
            result2 = await installer.install(sample_resource_data)

            # Should indicate already installed
            assert result2.success is True
            assert result2.skipped or "already installed" in result2.message.lower()

    @pytest.mark.asyncio
    async def test_WHEN_force_reinstall_THEN_overwrites(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource already installed
        WHEN: Installer is called with force=True
        THEN: Resource is reinstalled
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b"original content"
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            # First install
            result1 = await installer.install(sample_resource_data)
            original_content = result1.path.read_bytes()

            # Update mock content
            mock_response.content = b"new content"

            # Force reinstall
            result2 = await installer.install(sample_resource_data, force=True)

            # Content should be updated
            new_content = result2.path.read_bytes()
            assert new_content != original_content
            assert new_content == b"new content"

    @pytest.mark.asyncio
    async def test_WHEN_https_enforced_THEN_http_rejected(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource with HTTP (not HTTPS) URL
        WHEN: Installer attempts download
        THEN: Request is rejected (security control)
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        # Set HTTP URL
        sample_resource_data["source"]["url"] = sample_resource_data["source"]["url"].replace(
            "https://", "http://"
        )

        result = await installer.install(sample_resource_data)

        assert result.success is False
        assert "https" in result.error.lower()

    @pytest.mark.asyncio
    async def test_WHEN_path_traversal_THEN_blocked(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource with path traversal in install_path
        WHEN: Installer validates path
        THEN: Installation is blocked (security control)
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        # Attempt path traversal
        sample_resource_data["install_path"] = "../../../etc/passwd"

        result = await installer.install(sample_resource_data)

        assert result.success is False
        assert "path" in result.error.lower() or "security" in result.error.lower()

    @pytest.mark.asyncio
    async def test_WHEN_checksum_provided_THEN_verified(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource with checksum
        WHEN: Content is downloaded
        THEN: Checksum is verified for integrity
        """
        import hashlib
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        content = b"test content"
        expected_checksum = hashlib.sha256(content).hexdigest()

        sample_resource_data["source"]["sha256"] = expected_checksum

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = content
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await installer.install(sample_resource_data)

            assert result.success is True

    @pytest.mark.asyncio
    async def test_WHEN_checksum_mismatch_THEN_rejected(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource with checksum that doesn't match
        WHEN: Content is downloaded
        THEN: Installation is rejected
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        sample_resource_data["source"]["sha256"] = "wrong_checksum_12345"

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b"actual content"
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await installer.install(sample_resource_data)

            assert result.success is False
            assert "checksum" in result.error.lower() or "integrity" in result.error.lower()

    @pytest.mark.asyncio
    async def test_WHEN_progress_callback_THEN_updates_sent(
        self, temp_install_dir: Path, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Progress callback function
        WHEN: Installer downloads and installs
        THEN: Progress updates are sent to callback
        """
        from claude_resource_manager.core.installer import AsyncInstaller

        installer = AsyncInstaller(base_path=temp_install_dir)

        progress_updates = []

        async def progress_callback(message: str, percentage: float):
            progress_updates.append((message, percentage))

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b"test"
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            await installer.install(sample_resource_data, progress_callback=progress_callback)

            # Should have received progress updates
            assert len(progress_updates) > 0
            assert any(p[1] == 1.0 for p in progress_updates)  # 100% completion
