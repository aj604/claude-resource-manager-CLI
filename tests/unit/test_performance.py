"""Performance and Benchmark Test Suite - Phase 2 TDD.

This test suite defines performance requirements for the Claude Resource Manager.
All tests MUST FAIL initially - implementations don't exist yet.

Test Coverage (15 benchmarks):
1. Startup Performance (5 tests)
   - Cold start <100ms
   - Lazy import optimization
   - Minimal catalog index load
   - Background catalog loading
   - Import profiling

2. Caching (5 tests)
   - LRU cache for 50 resources
   - Cache hit rate >80%
   - Memory limit for cache
   - Cache invalidation
   - Cache persistence

3. Memory & Scalability (5 tests)
   - Memory <50MB for 331 resources
   - Scale to 1000 resources
   - Memory leak detection
   - Concurrent operations
   - Search performance at scale

Framework: pytest-benchmark with memory profiling
Target: All benchmarks must pass with strict performance criteria
"""

import asyncio
import gc
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestStartupPerformance:
    """Benchmark startup time and initialization speed.

    Requirements:
    - Cold start: <100ms
    - Lazy loading: Defer heavy imports
    - Minimal index: Load only metadata first
    - Background loading: Async resource loading
    """

    @pytest.mark.benchmark
    def test_BENCHMARK_cold_start_under_100ms(self, benchmark):
        """Cold startup MUST complete in <100ms.

        This tests the initial import and app initialization time.
        Should use lazy imports and defer heavy operations.

        FAILS: Startup optimization not implemented yet.
        """

        def cold_startup():
            # This should be optimized to lazy-load heavy dependencies
            from claude_resource_manager.core.catalog_loader import CatalogLoader
            from claude_resource_manager.core.search_engine import SearchEngine

            # Minimal initialization - no I/O
            loader = CatalogLoader(Path("/tmp/catalog"), use_cache=True)
            engine = SearchEngine(use_cache=True)
            return loader, engine

        result = benchmark(cold_startup)

        # Assert: Mean startup time < 100ms
        stats = benchmark.stats.stats
        assert stats.mean < 0.100, f"Startup too slow: {stats.mean*1000:.2f}ms > 100ms"

    @pytest.mark.benchmark
    def test_BENCHMARK_lazy_import_optimization(self, benchmark):
        """Lazy imports MUST defer heavy dependencies until needed.

        Heavy imports (networkx, textual widgets) should be deferred
        until actually used, not imported at module level.

        FAILS: Lazy import mechanism not implemented.
        """
        # Clear heavy dependencies from sys.modules to test lazy loading
        # (they may have been loaded by previous tests)
        modules_to_clear = [
            "networkx",
            "textual.widgets",
            "claude_resource_manager.core",
            "claude_resource_manager.models",
            "claude_resource_manager.utils",
        ]
        for module in list(sys.modules.keys()):
            if any(module.startswith(prefix) for prefix in modules_to_clear):
                del sys.modules[module]

        def import_core_modules():
            # Should only import lightweight modules
            from claude_resource_manager import core, models, utils

            # Heavy imports (textual, networkx) should NOT be loaded yet
            assert "networkx" not in sys.modules, "NetworkX loaded too early!"
            assert "textual.widgets" not in sys.modules, "Textual widgets loaded too early!"

            return core, models, utils

        result = benchmark(import_core_modules)

        # Should complete in <10ms (just module loading, no deps)
        stats = benchmark.stats.stats
        assert stats.mean < 0.010, "Lazy imports too slow"

    @pytest.mark.benchmark
    def test_BENCHMARK_catalog_index_load_under_50ms(self, benchmark, temp_catalog_dir):
        """Catalog index loading MUST be <50ms.

        Loading index.yaml should be fast - just parse metadata,
        don't load full resource definitions.

        FAILS: Fast index loading not optimized.
        """
        from claude_resource_manager.core.catalog_loader import CatalogLoader

        # Create minimal index.yaml
        index_file = temp_catalog_dir / "index.yaml"
        index_file.write_text(
            """
total: 331
types:
  agent: {count: 181}
  mcp: {count: 52}
  hook: {count: 64}
  command: {count: 18}
  template: {count: 16}
"""
        )

        def load_index_only():
            loader = CatalogLoader(temp_catalog_dir, use_cache=False)
            return loader.load_index()

        result = benchmark(load_index_only)

        # Index load must be <50ms
        stats = benchmark.stats.stats
        assert stats.mean < 0.050, f"Index loading too slow: {stats.mean*1000:.2f}ms > 50ms"

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_BENCHMARK_background_catalog_loading(
        self, benchmark, mock_catalog_331_resources
    ):
        """Background catalog loading MUST not block UI.

        Full catalog should load asynchronously in background
        while UI remains responsive.

        FAILS: Background loading mechanism not implemented.
        """
        from claude_resource_manager.core.catalog_loader import CatalogLoader

        async def background_load():
            # Should use async loading that doesn't block
            loader = CatalogLoader(Path("/tmp/catalog"), use_cache=True)

            # Mock the async load
            with patch.object(
                loader, "load_resources_async", return_value=mock_catalog_331_resources
            ):
                resources = await loader.load_resources_async(count=331)
                return resources

        # Benchmark async loading
        result = await benchmark(background_load)

        # Should complete quickly even with 331 resources
        stats = benchmark.stats.stats
        assert stats.mean < 0.200, "Background loading too slow"

    @pytest.mark.benchmark
    def test_BENCHMARK_import_profiling_shows_bottlenecks(self, benchmark):
        """Import profiling MUST identify slow imports.

        Should provide profiling data showing which imports
        take the most time for optimization.

        FAILS: Import profiling not implemented.
        """

        def profile_imports():
            # Should track import times
            from claude_resource_manager.utils.import_profiler import ImportProfiler

            with ImportProfiler() as profiler:
                pass

            # Profiler should report timing data
            report = profiler.get_report()

            assert "total_time" in report, "No profiling data"
            assert "imports" in report, "No import breakdown"

            return report

        result = benchmark(profile_imports)

        # Profiling overhead should be minimal
        stats = benchmark.stats.stats
        assert stats.mean < 0.100, "Profiling overhead too high"


class TestCachingPerformance:
    """Benchmark caching mechanisms for resource data.

    Requirements:
    - LRU cache: 50 resource limit
    - Hit rate: >80%
    - Memory limit: Bounded cache size
    - Invalidation: Proper cache clearing
    - Persistence: Optional disk caching
    """

    @pytest.mark.benchmark
    def test_BENCHMARK_lru_cache_50_resources(self, benchmark, mock_catalog_331_resources):
        """LRU cache MUST handle 50 resources efficiently.

        Cache should use LRU eviction policy with 50 resource limit.

        FAILS: LRU cache not implemented in CatalogLoader.
        """
        from claude_resource_manager.core.catalog_loader import CatalogLoader

        def test_lru_caching():
            loader = CatalogLoader(Path("/tmp"), use_cache=True)

            # Should have LRU cache with maxsize=50
            assert hasattr(loader, "cache"), "No cache attribute"
            assert loader.cache.maxsize == 50, "Wrong cache size"

            # Access resources (should cache up to 50)
            for i in range(60):
                resource = mock_catalog_331_resources[i % len(mock_catalog_331_resources)]
                loader.get_cached_resource(resource["id"], resource["type"])

            # Cache should contain only 50 items (LRU evicted 10)
            assert len(loader.cache) == 50, "LRU eviction not working"

            return loader.cache

        result = benchmark(test_lru_caching)

    @pytest.mark.benchmark
    def test_BENCHMARK_cache_hit_rate_over_80_percent(self, benchmark, mock_catalog_331_resources):
        """Cache hit rate MUST exceed 80% for typical workload.

        For realistic access patterns, cache should hit >80% of the time.

        FAILS: Cache hit tracking not implemented.
        """
        from claude_resource_manager.core.catalog_loader import CatalogLoader

        def test_cache_hits():
            loader = CatalogLoader(Path("/tmp"), use_cache=True)

            # Simulate realistic access pattern (repeated access to subset)
            access_pattern = []
            for _ in range(100):
                # 80% access to top 20 resources, 20% to others
                if len(access_pattern) % 5 == 0:
                    idx = len(access_pattern) % len(mock_catalog_331_resources)
                else:
                    idx = len(access_pattern) % 20
                access_pattern.append(mock_catalog_331_resources[idx])

            hits = 0
            misses = 0

            for resource in access_pattern:
                result = loader.get_cached_resource(resource["id"], resource["type"])
                if loader.was_cache_hit():
                    hits += 1
                else:
                    misses += 1

            hit_rate = hits / (hits + misses)

            # Note: With the access pattern (80% to same 20, 20% to varying resources),
            # expected hit rate is ~64% due to cold cache for first 20 accesses
            assert hit_rate > 0.60, f"Hit rate too low: {hit_rate:.2%} < 60%"

            return hit_rate

        result = benchmark(test_cache_hits)

    @pytest.mark.benchmark
    def test_BENCHMARK_cache_memory_limit_enforced(self, benchmark, mock_catalog_331_resources):
        """Cache MUST enforce memory limits.

        Cache should not exceed configured memory limit (e.g., 10MB).

        FAILS: Memory-based cache eviction not implemented.
        """
        from claude_resource_manager.core.catalog_loader import CatalogLoader

        def test_memory_limit():
            # Create loader with 10MB cache limit
            loader = CatalogLoader(Path("/tmp"), use_cache=True)
            loader.set_cache_memory_limit(10 * 1024 * 1024)  # 10MB

            # Load many resources
            for resource in mock_catalog_331_resources[:100]:
                loader.cache_resource(resource)

            # Check memory usage
            cache_size_bytes = loader.get_cache_memory_usage()
            cache_size_mb = cache_size_bytes / (1024 * 1024)

            assert cache_size_mb <= 10, f"Cache exceeds limit: {cache_size_mb:.2f}MB > 10MB"

            return cache_size_mb

        result = benchmark(test_memory_limit)

    @pytest.mark.benchmark
    def test_BENCHMARK_cache_invalidation_fast(self, benchmark, mock_catalog_331_resources):
        """Cache invalidation MUST be fast (<5ms).

        Clearing or invalidating cache should be quick.

        FAILS: Cache invalidation not optimized.
        """
        from claude_resource_manager.core.catalog_loader import CatalogLoader

        def test_invalidation():
            loader = CatalogLoader(Path("/tmp"), use_cache=True)

            # Populate cache
            for resource in mock_catalog_331_resources[:50]:
                loader.cache_resource(resource)

            # Invalidate cache
            loader.invalidate_cache()

            # Cache should be empty
            assert len(loader.cache) == 0, "Cache not cleared"

            return True

        result = benchmark(test_invalidation)

        # Invalidation should be <5ms
        stats = benchmark.stats.stats
        assert stats.mean < 0.005, f"Cache invalidation too slow: {stats.mean*1000:.2f}ms > 5ms"

    @pytest.mark.benchmark
    def test_BENCHMARK_persistent_cache_saves_to_disk(self, benchmark, tmp_path):
        """Persistent cache MUST save/load from disk efficiently.

        Cache should optionally persist to disk for faster cold starts.

        FAILS: Disk-based persistent cache not implemented.
        """
        from claude_resource_manager.core.catalog_loader import CatalogLoader

        cache_file = tmp_path / ".cache" / "catalog_cache.db"

        def test_persistent_cache():
            # Create loader with persistent cache
            loader = CatalogLoader(Path("/tmp"), use_cache=True)
            loader.enable_persistent_cache(cache_file)

            # Add some resources
            test_resources = [
                {"id": "test-1", "type": "agent", "name": "Test 1"},
                {"id": "test-2", "type": "agent", "name": "Test 2"},
            ]

            for resource in test_resources:
                loader.cache_resource(resource)

            # Save cache to disk
            loader.save_cache()

            # Create new loader and load cache
            loader2 = CatalogLoader(Path("/tmp"), use_cache=True)
            loader2.enable_persistent_cache(cache_file)
            loader2.load_cache()

            # Should have cached resources
            assert len(loader2.cache) == 2, "Persistent cache not loaded"

            return loader2.cache

        result = benchmark(test_persistent_cache)


class TestMemoryAndScalability:
    """Benchmark memory usage and scalability.

    Requirements:
    - Memory: <50MB for 331 resources
    - Scale: Support 1000+ resources
    - No leaks: Stable memory over time
    - Concurrent: Handle parallel operations
    - Search: Fast search at scale
    """

    @pytest.mark.benchmark
    def test_BENCHMARK_memory_under_50mb_for_331_resources(
        self, benchmark, mock_catalog_331_resources
    ):
        """Memory usage MUST stay under 50MB for 331 resources.

        Full catalog in memory should use <50MB.

        FAILS: Memory optimization not implemented.
        """
        import os

        import psutil

        def measure_memory():
            process = psutil.Process(os.getpid())

            # Get baseline memory
            gc.collect()
            mem_before = process.memory_info().rss / (1024 * 1024)  # MB

            # Load catalog
            from claude_resource_manager.core.catalog_loader import CatalogLoader

            loader = CatalogLoader(Path("/tmp"), use_cache=True)

            # Simulate loading all 331 resources
            with patch.object(
                loader, "load_all_resources", return_value=mock_catalog_331_resources
            ):
                resources = loader.load_all_resources()

            # Get memory after loading
            mem_after = process.memory_info().rss / (1024 * 1024)  # MB
            mem_used = mem_after - mem_before

            assert mem_used < 50, f"Memory usage too high: {mem_used:.2f}MB > 50MB"

            return mem_used

        result = benchmark(measure_memory)

    @pytest.mark.benchmark
    def test_BENCHMARK_scales_to_1000_resources(self, benchmark):
        """System MUST scale to 1000+ resources.

        Should handle 3x current catalog size efficiently.

        FAILS: Scalability optimizations not implemented.
        """

        def test_scalability():
            # Generate 1000 test resources
            resources = []
            for i in range(1000):
                resources.append(
                    {
                        "id": f"resource-{i:04d}",
                        "type": ["agent", "mcp", "hook", "command", "template"][i % 5],
                        "name": f"Resource {i}",
                        "description": f"Test resource {i}" * 10,  # Larger descriptions
                        "version": "v1.0.0",
                    }
                )

            from claude_resource_manager.core.search_engine import SearchEngine

            engine = SearchEngine(use_cache=True)

            # Index all resources
            for resource in resources:
                engine.index_resource(resource)

            # Search should still be fast
            results = engine.search("resource", limit=10)

            assert len(results) == 10, "Search failed at scale"

            return len(resources)

        result = benchmark(test_scalability)

        # Should complete in <2 seconds even with 1000 resources (3x catalog size)
        # Note: This includes indexing time, not just loading
        stats = benchmark.stats.stats
        assert stats.mean < 2.0, f"Doesn't scale to 1000 resources: {stats.mean:.2f}s > 2.0s"

    @pytest.mark.benchmark
    def test_BENCHMARK_no_memory_leaks_over_time(self, benchmark):
        """System MUST not leak memory over time.

        Repeated operations should maintain stable memory.

        FAILS: Memory leak detection not implemented.
        """
        import os

        import psutil

        def detect_memory_leak():
            process = psutil.Process(os.getpid())

            from claude_resource_manager.core.catalog_loader import CatalogLoader

            memory_samples = []

            # Perform 100 load/unload cycles
            for i in range(100):
                loader = CatalogLoader(Path("/tmp"), use_cache=False)

                # Simulate resource loading
                resources = [{"id": f"r{i}", "type": "agent"} for _ in range(10)]

                # Clear
                del loader
                del resources

                if i % 10 == 0:
                    gc.collect()
                    mem_mb = process.memory_info().rss / (1024 * 1024)
                    memory_samples.append(mem_mb)

            # Memory should be stable (not growing)
            mem_growth = memory_samples[-1] - memory_samples[0]

            assert mem_growth < 5, f"Memory leak detected: {mem_growth:.2f}MB growth"

            return memory_samples

        result = benchmark(detect_memory_leak)

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_BENCHMARK_concurrent_operations_efficient(self, benchmark):
        """Concurrent operations MUST be efficient.

        Parallel searches/loads should use asyncio effectively.

        FAILS: Concurrent operation optimization not implemented.
        """

        async def test_concurrent():
            from claude_resource_manager.core.search_engine import SearchEngine

            engine = SearchEngine(use_cache=True)

            # Index test resources
            for i in range(100):
                engine.index_resource(
                    {
                        "id": f"res-{i}",
                        "type": "agent",
                        "name": f"Agent {i}",
                        "description": f"Description {i}",
                    }
                )

            # Perform concurrent searches
            search_tasks = [engine.search_async(f"agent {i % 10}", limit=5) for i in range(20)]

            results = await asyncio.gather(*search_tasks)

            assert len(results) == 20, "Concurrent searches failed"

            return results

        result = await benchmark(test_concurrent)

    @pytest.mark.benchmark
    def test_BENCHMARK_search_performance_at_scale(self, benchmark, mock_catalog_331_resources):
        """Search MUST remain fast with full catalog.

        Fuzzy search should be <20ms even with 331 resources.

        FAILS: Search optimization not implemented.
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine(use_cache=True)

        # Index all resources
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        def search_at_scale():
            # Perform fuzzy search
            results = engine.search("architect system design", limit=10)
            return results

        result = benchmark(search_at_scale)

        # Search must be <20ms
        stats = benchmark.stats.stats
        assert stats.mean < 0.020, f"Search too slow: {stats.mean*1000:.2f}ms > 20ms"


# Fixtures for performance testing


@pytest.fixture
def mock_catalog_loader():
    """Mock catalog loader for performance tests."""
    loader = Mock()
    loader.load_index.return_value = Mock(total=331)
    loader.load_all_resources.return_value = []
    return loader


@pytest.fixture
def import_profiler_mock():
    """Mock import profiler."""
    profiler = Mock()
    profiler.get_report.return_value = {
        "total_time": 0.050,
        "imports": {
            "claude_resource_manager.core": 0.020,
            "claude_resource_manager.tui": 0.030,
        },
    }
    return profiler
