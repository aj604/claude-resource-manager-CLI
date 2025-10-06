"""Comprehensive integration tests for batch installation workflow.

This module tests the end-to-end batch installation feature that allows
installing multiple resources simultaneously. Tests cover:

- Batch workflow (multiple resource installation)
- Progress reporting (1/5, 2/5, etc.)
- Success/failure tracking per resource
- Partial failure handling and rollback
- Dependency resolution in batch context
- Performance benchmarks

Test Coverage: 15 tests
Strategy: RED phase - All tests will FAIL until batch installation is implemented

Author: TestMaster (TDD Phase)
"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from claude_resource_manager.core.installer import AsyncInstaller, InstallResult

# ============================================================================
# Batch Workflow Tests (7 tests)
# ============================================================================


class TestBatchWorkflow:
    """Test batch installation workflow and orchestration."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_install_multiple_THEN_all_succeed(
        self, temp_install_dir, mock_httpx_client
    ):
        """Batch install should install all selected resources."""
        # Setup
        installer = AsyncInstaller(temp_install_dir)

        resources = [
            {
                "id": "agent-1",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/agent-1.md"
                },
            },
            {
                "id": "agent-2",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/agent-2.md"
                },
            },
            {
                "id": "agent-3",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/agent-3.md"
                },
            },
        ]

        # Execute batch install
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            results = await installer.batch_install(resources)

        # Verify
        assert len(results) == 3
        assert all(r.success for r in results)
        assert all(r.path.exists() for r in results if r.path)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_batch_install_THEN_reports_progress(
        self, temp_install_dir, mock_httpx_client
    ):
        """Batch install should report progress for each resource."""
        installer = AsyncInstaller(temp_install_dir)

        resources = [
            {
                "id": f"agent-{i}",
                "type": "agent",
                "source": {
                    "url": f"https://raw.githubusercontent.com/test/repo/main/agents/agent-{i}.md"
                },
            }
            for i in range(5)
        ]

        progress_updates = []

        async def progress_callback(resource_id: str, current: int, total: int, status: str):
            """Track progress updates."""
            progress_updates.append(
                {
                    "resource_id": resource_id,
                    "current": current,
                    "total": total,
                    "status": status,
                }
            )

        # Execute with progress tracking
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            await installer.batch_install(resources, progress_callback=progress_callback)

        # Verify progress updates
        assert len(progress_updates) >= 5  # At least one per resource
        # Should show 1/5, 2/5, 3/5, 4/5, 5/5
        progress_counts = [p["current"] for p in progress_updates]
        assert 1 in progress_counts
        assert 5 in progress_counts

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_batch_install_THEN_tracks_per_resource_status(
        self, temp_install_dir, mock_httpx_client
    ):
        """Each resource should have individual success/failure status."""
        installer = AsyncInstaller(temp_install_dir)

        # Create one failing resource (bad URL)
        resources = [
            {
                "id": "good-1",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/good-1.md"
                },
            },
            {
                "id": "bad",
                "type": "agent",
                "source": {"url": "http://invalid.com/bad.md"},
            },  # HTTP not HTTPS - will fail
            {
                "id": "good-2",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/good-2.md"
                },
            },
        ]

        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            results = await installer.batch_install(resources)

        # Verify individual tracking
        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False  # Failed due to HTTP
        assert results[2].success is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_partial_failure_THEN_continues_installation(self, temp_install_dir):
        """Batch install should continue even if some resources fail."""
        installer = AsyncInstaller(temp_install_dir)

        # Mix of good and bad resources
        resources = [
            {
                "id": "good-1",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/good-1.md"
                },
            },
            {
                "id": "bad-url",
                "type": "agent",
                "source": {"url": "http://http-not-https.com/fail.md"},
            },
            {
                "id": "good-2",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/good-2.md"
                },
            },
            {
                "id": "bad-path",
                "type": "agent",
                "install_path": "../../../etc/passwd",  # Path traversal - will fail
                "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/bad.md"},
            },
        ]

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            return_value=AsyncMock(
                status_code=200,
                content=b"# Test",
                raise_for_status=Mock(),
            )
        )

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await installer.batch_install(resources)

        # Should complete all attempts
        assert len(results) == 4

        # Check success/failure distribution
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]

        assert len(successes) == 2  # good-1 and good-2
        assert len(failures) == 2  # bad-url and bad-path

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_batch_error_THEN_rollback_option(self, temp_install_dir, mock_httpx_client):
        """Optional: Support rollback on critical failure."""
        installer = AsyncInstaller(temp_install_dir)

        resources = [
            {
                "id": "resource-1",
                "type": "agent",
                "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/r1.md"},
            },
            {
                "id": "resource-2",
                "type": "agent",
                "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/r2.md"},
            },
        ]

        # Install successfully first
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            results = await installer.batch_install(resources)
            assert all(r.success for r in results)

        # Now simulate a critical failure requiring rollback
        installed_paths = [r.path for r in results if r.path]
        assert all(p.exists() for p in installed_paths)

        # Rollback
        await installer.rollback_batch(results)

        # Verify files removed
        assert not any(p.exists() for p in installed_paths)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_batch_install_THEN_returns_summary(
        self, temp_install_dir, mock_httpx_client
    ):
        """Batch install should return summary with counts."""
        installer = AsyncInstaller(temp_install_dir)

        resources = [
            {
                "id": f"agent-{i}",
                "type": "agent",
                "source": {
                    "url": f"https://raw.githubusercontent.com/test/repo/main/agents/agent-{i}.md"
                },
            }
            for i in range(10)
        ]

        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            summary = await installer.batch_install_with_summary(resources)

        # Verify summary structure
        assert summary["total"] == 10
        assert summary["succeeded"] == 10
        assert summary["failed"] == 0
        assert summary["skipped"] == 0
        assert "duration" in summary
        assert isinstance(summary["results"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_duplicate_resources_THEN_deduplicates(
        self, temp_install_dir, mock_httpx_client
    ):
        """Batch install should deduplicate duplicate resource IDs."""
        installer = AsyncInstaller(temp_install_dir)

        # Include duplicates
        resources = [
            {
                "id": "agent-1",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/agent-1.md"
                },
            },
            {
                "id": "agent-2",
                "type": "agent",
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/agent-2.md"
                },
            },
            {
                "id": "agent-1",
                "type": "agent",  # Duplicate
                "source": {
                    "url": "https://raw.githubusercontent.com/test/repo/main/agents/agent-1.md"
                },
            },
        ]

        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            results = await installer.batch_install(resources)

        # Should only install 2 unique resources
        assert len(results) == 2
        installed_ids = {r.path.stem for r in results if r.path}
        assert installed_ids == {"agent-1", "agent-2"}


# ============================================================================
# Dependency Handling Tests (5 tests)
# ============================================================================


class TestBatchDependencies:
    """Test dependency resolution in batch installation context."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_batch_has_deps_THEN_installs_all(self, temp_install_dir, mock_httpx_client):
        """Batch install should resolve and install all dependencies."""
        installer = AsyncInstaller(temp_install_dir)

        # Resources with dependencies
        dep1 = {
            "id": "dep-1",
            "type": "agent",
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/dep-1.md"},
        }
        dep2 = {
            "id": "dep-2",
            "type": "agent",
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/dep-2.md"},
        }

        main = {
            "id": "main-agent",
            "type": "agent",
            "dependencies": {"required": ["dep-1", "dep-2"]},
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/main.md"},
        }

        # Register dependencies
        installer.register_resource(dep1)
        installer.register_resource(dep2)

        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            results = await installer.batch_install([main])

        # Should install main + 2 dependencies = 3 total
        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_multiple_resources_share_deps_THEN_deduplicates(
        self, temp_install_dir, mock_httpx_client
    ):
        """Shared dependencies should only be installed once."""
        installer = AsyncInstaller(temp_install_dir)

        # Shared dependency
        shared_dep = {
            "id": "shared-dep",
            "type": "agent",
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/shared.md"},
        }

        # Two resources depending on same dependency
        resource1 = {
            "id": "resource-1",
            "type": "agent",
            "dependencies": {"required": ["shared-dep"]},
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/r1.md"},
        }

        resource2 = {
            "id": "resource-2",
            "type": "agent",
            "dependencies": {"required": ["shared-dep"]},
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/r2.md"},
        }

        installer.register_resource(shared_dep)

        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            results = await installer.batch_install([resource1, resource2])

        # Should install: resource-1, resource-2, shared-dep (only once) = 3 total
        assert len(results) == 3

        # Check that shared-dep appears only once
        resource_ids = [r.path.stem for r in results if r.path]
        assert resource_ids.count("shared-dep") == 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_batch_deps_THEN_correct_order(self, temp_install_dir, mock_httpx_client):
        """Dependencies should be installed in topological order."""
        installer = AsyncInstaller(temp_install_dir)

        # Create dependency chain: dep1 <- dep2 <- main
        dep1 = {
            "id": "dep-1",
            "type": "agent",
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/dep-1.md"},
        }

        dep2 = {
            "id": "dep-2",
            "type": "agent",
            "dependencies": {"required": ["dep-1"]},
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/dep-2.md"},
        }

        main = {
            "id": "main",
            "type": "agent",
            "dependencies": {"required": ["dep-2"]},
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/main.md"},
        }

        installer.register_resource(dep1)
        installer.register_resource(dep2)

        install_order = []

        async def track_install(resource, **kwargs):
            """Track installation order."""
            install_order.append(resource["id"])
            return InstallResult(success=True, path=temp_install_dir / f"{resource['id']}.md")

        installer.install = track_install

        await installer.batch_install([main])

        # Should install in order: dep-1, dep-2, main
        assert install_order == ["dep-1", "dep-2", "main"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_already_installed_in_batch_THEN_skips(
        self, temp_install_dir, mock_httpx_client
    ):
        """Already installed dependencies should be skipped in batch."""
        installer = AsyncInstaller(temp_install_dir)

        # Pre-install dep-1
        dep1_path = temp_install_dir / "agents" / "dep-1.md"
        dep1_path.parent.mkdir(parents=True, exist_ok=True)
        dep1_path.write_text("# Already installed")

        dep1 = {
            "id": "dep-1",
            "type": "agent",
            "install_path": "agents/dep-1.md",
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/dep-1.md"},
        }

        main = {
            "id": "main",
            "type": "agent",
            "dependencies": {"required": ["dep-1"]},
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/main.md"},
        }

        installer.register_resource(dep1)

        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            results = await installer.batch_install([main], skip_installed=True)

        # Should install main but skip dep-1
        skipped = [r for r in results if r.skipped]
        installed = [r for r in results if r.success and not r.skipped]

        assert len(skipped) == 1  # dep-1 skipped
        assert len(installed) == 1  # main installed

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_WHEN_circular_deps_in_batch_THEN_detects_error(self, temp_install_dir):
        """Circular dependencies should be detected and reported."""
        installer = AsyncInstaller(temp_install_dir)

        # Create circular dependency: A -> B -> C -> A
        resource_a = {
            "id": "resource-a",
            "type": "agent",
            "dependencies": {"required": ["resource-b"]},
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/a.md"},
        }

        resource_b = {
            "id": "resource-b",
            "type": "agent",
            "dependencies": {"required": ["resource-c"]},
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/b.md"},
        }

        resource_c = {
            "id": "resource-c",
            "type": "agent",
            "dependencies": {"required": ["resource-a"]},  # Circular!
            "source": {"url": "https://raw.githubusercontent.com/test/repo/main/agents/c.md"},
        }

        installer.register_resource(resource_a)
        installer.register_resource(resource_b)
        installer.register_resource(resource_c)

        # Should detect circular dependency
        with pytest.raises(Exception) as exc_info:
            await installer.batch_install([resource_a])

        assert "circular" in str(exc_info.value).lower()


# ============================================================================
# Performance Tests (3 tests)
# ============================================================================


class TestBatchPerformance:
    """Test performance and efficiency of batch operations."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.benchmark
    async def test_WHEN_parallel_downloads_THEN_faster_than_serial(self, temp_install_dir):
        """Parallel batch install should be faster than serial."""
        installer = AsyncInstaller(temp_install_dir)

        # 10 resources
        resources = [
            {
                "id": f"agent-{i}",
                "type": "agent",
                "source": {
                    "url": f"https://raw.githubusercontent.com/test/repo/main/agents/agent-{i}.md"
                },
            }
            for i in range(10)
        ]

        # Mock client with 100ms delay per download
        async def delayed_get(url, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return AsyncMock(
                status_code=200,
                content=b"# Test",
                raise_for_status=Mock(),
            )

        mock_client = AsyncMock()
        mock_client.get = delayed_get

        # Parallel install
        start = time.time()
        with patch("httpx.AsyncClient", return_value=mock_client):
            await installer.batch_install(resources, parallel=True)
        parallel_duration = time.time() - start

        # Serial install
        start = time.time()
        with patch("httpx.AsyncClient", return_value=mock_client):
            await installer.batch_install(resources, parallel=False)
        serial_duration = time.time() - start

        # Parallel should be significantly faster
        # 10 downloads * 100ms = 1000ms serial
        # But parallel should be ~100-200ms (overlapped)
        assert parallel_duration < serial_duration * 0.5

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.benchmark
    async def test_WHEN_batch_10_resources_THEN_completes_quickly(
        self, temp_install_dir, mock_httpx_client
    ):
        """Batch install of 10 resources should complete in <5 seconds."""
        installer = AsyncInstaller(temp_install_dir)

        resources = [
            {
                "id": f"agent-{i}",
                "type": "agent",
                "source": {
                    "url": f"https://raw.githubusercontent.com/test/repo/main/agents/agent-{i}.md"
                },
            }
            for i in range(10)
        ]

        start = time.time()
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            await installer.batch_install(resources)
        duration = time.time() - start

        # Should complete in under 5 seconds
        assert duration < 5.0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.benchmark
    async def test_WHEN_batch_install_THEN_memory_efficient(
        self, temp_install_dir, mock_httpx_client
    ):
        """Batch install should not consume excessive memory."""
        import tracemalloc

        installer = AsyncInstaller(temp_install_dir)

        # 50 resources
        resources = [
            {
                "id": f"agent-{i}",
                "type": "agent",
                "source": {
                    "url": f"https://raw.githubusercontent.com/test/repo/main/agents/agent-{i}.md"
                },
            }
            for i in range(50)
        ]

        tracemalloc.start()

        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            await installer.batch_install(resources)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be reasonable (< 10 MB for 50 resources)
        assert peak < 10 * 1024 * 1024  # 10 MB
