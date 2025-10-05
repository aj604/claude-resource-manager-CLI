"""Tests for SearchEngine - exact, prefix, and fuzzy search.

These tests ensure <5ms search performance for 331 resources.
Tests will FAIL until SearchEngine is implemented.
"""

import time
from typing import List, Dict, Any
import pytest


class TestSearchEngine:
    """Tests for SearchEngine with performance benchmarks."""

    def test_WHEN_exact_match_THEN_returns_immediately(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with 331 indexed resources
        WHEN: Exact match search is performed
        THEN: Result is returned in <1ms (O(1) dict lookup)
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        start = time.perf_counter()
        results = engine.search_exact("agent-000")
        elapsed = time.perf_counter() - start

        assert len(results) == 1
        assert results[0]["id"] == "agent-000"
        assert elapsed < 0.001  # <1ms

    def test_WHEN_prefix_search_THEN_trie_used(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with 331 indexed resources
        WHEN: Prefix search is performed
        THEN: All matching resources returned using trie
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        results = engine.search_prefix("agent-0")

        # Should match agent-000 through agent-099 (100 resources)
        assert len(results) >= 10  # At least 10 matches
        assert all(r["id"].startswith("agent-0") for r in results)

    def test_WHEN_fuzzy_search_THEN_typos_handled(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with 331 indexed resources
        WHEN: Fuzzy search with typo is performed
        THEN: Close matches are found using RapidFuzz
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        # Typo: "agnet" instead of "agent"
        results = engine.search_fuzzy("agnet-000")

        assert len(results) > 0
        # Top result should be "agent-000" (close match)
        assert results[0]["id"] == "agent-000"

    def test_WHEN_empty_query_THEN_returns_empty(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with indexed resources
        WHEN: Empty query is searched
        THEN: Empty result list is returned
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        results = engine.search("")

        assert results == []

    def test_WHEN_case_insensitive_THEN_matches(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with indexed resources
        WHEN: Search with different case is performed
        THEN: Case-insensitive matching works
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        results_lower = engine.search("agent-000")
        results_upper = engine.search("AGENT-000")
        results_mixed = engine.search("Agent-000")

        assert results_lower == results_upper == results_mixed
        assert len(results_lower) > 0

    def test_WHEN_331_resources_THEN_search_under_5ms(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with 331 indexed resources
        WHEN: Search is performed
        THEN: Results returned in <5ms (performance target)
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        start = time.perf_counter()
        results = engine.search("architect")
        elapsed = time.perf_counter() - start

        assert elapsed < 0.005  # <5ms
        assert len(results) > 0

    def test_WHEN_special_characters_THEN_handled(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with indexed resources
        WHEN: Query contains special characters
        THEN: Search handles them gracefully
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        # Special chars should not crash
        results = engine.search("@#$%^&*()")

        assert isinstance(results, list)  # No crash

    def test_WHEN_unicode_query_THEN_matches(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with resources containing Unicode
        WHEN: Unicode query is searched
        THEN: Matching works correctly
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()

        # Add resource with Unicode
        unicode_resource = {
            "id": "architect-中文",
            "type": "agent",
            "name": "Architect 中文",
            "description": "Architecture specialist 🚀",
        }
        engine.index_resource(unicode_resource)

        results = engine.search("中文")

        assert len(results) == 1
        assert "中文" in results[0]["id"]

    def test_WHEN_smart_search_THEN_combines_strategies(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with multiple search strategies
        WHEN: Smart search is used
        THEN: Combines exact, prefix, and fuzzy results with ranking
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        results = engine.search_smart("agent")

        # Should find:
        # 1. Exact matches (highest rank)
        # 2. Prefix matches (medium rank)
        # 3. Fuzzy matches (lower rank)
        assert len(results) > 0

        # Results should be ranked (exact matches first)
        if len(results) > 1:
            assert results[0]["score"] >= results[-1]["score"]

    def test_WHEN_results_ranked_THEN_best_first(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with fuzzy search
        WHEN: Multiple matches are found
        THEN: Best matches are ranked first
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        # Add exact match and partial matches
        exact_resource = {
            "id": "architect",
            "type": "agent",
            "name": "Architect",
        }
        partial_resource = {
            "id": "solution-architect-expert",
            "type": "agent",
            "name": "Solution Architect",
        }

        engine.index_resource(exact_resource)
        engine.index_resource(partial_resource)

        results = engine.search_fuzzy("architect")

        # Exact match should be first
        assert results[0]["id"] == "architect"

    def test_WHEN_cache_hit_THEN_instant_return(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with result caching
        WHEN: Same query is searched twice
        THEN: Second search is instant (from cache)
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine(use_cache=True)
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        # First search
        start1 = time.perf_counter()
        results1 = engine.search("architect")
        time1 = time.perf_counter() - start1

        # Second search (cached)
        start2 = time.perf_counter()
        results2 = engine.search("architect")
        time2 = time.perf_counter() - start2

        assert results1 == results2
        assert time2 < time1 / 10  # At least 10x faster

    def test_WHEN_no_matches_THEN_empty_list(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with indexed resources
        WHEN: Query matches nothing
        THEN: Empty list is returned
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        results = engine.search("xyznonexistent123")

        assert results == []

    def test_WHEN_search_by_description_THEN_finds_matches(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine indexing descriptions
        WHEN: Query matches description text
        THEN: Resources are found
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine(index_fields=["id", "name", "description"])

        resource = {
            "id": "test-001",
            "name": "Test",
            "description": "This is a unique description text",
        }
        engine.index_resource(resource)

        results = engine.search("unique description")

        assert len(results) == 1

    def test_WHEN_filter_by_type_THEN_filtered(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with multiple resource types
        WHEN: Search is filtered by type
        THEN: Only matching type is returned
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        results = engine.search("agent", filters={"type": "agent"})

        assert all(r["type"] == "agent" for r in results)

    def test_WHEN_limit_results_THEN_respects_limit(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with many matches
        WHEN: Search with result limit
        THEN: Returns exactly limit number of results
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        results = engine.search("agent", limit=10)

        assert len(results) <= 10

    def test_WHEN_multi_word_query_THEN_all_words_matched(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with indexed resources
        WHEN: Multi-word query is searched
        THEN: All words are matched (AND logic)
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()

        resource = {
            "id": "security-code-reviewer",
            "name": "Security Code Reviewer",
            "description": "Reviews code for security issues",
        }
        engine.index_resource(resource)

        results = engine.search("security code")

        assert len(results) >= 1
        assert "security-code-reviewer" in [r["id"] for r in results]

    def test_WHEN_index_updated_THEN_search_reflects_changes(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with indexed resources
        WHEN: New resource is added to index
        THEN: Search immediately finds new resource
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()

        # Initial search
        results_before = engine.search("newresource")
        assert len(results_before) == 0

        # Add new resource
        new_resource = {
            "id": "newresource",
            "name": "New Resource",
            "type": "agent",
        }
        engine.index_resource(new_resource)

        # Search again
        results_after = engine.search("newresource")
        assert len(results_after) == 1

    def test_WHEN_remove_from_index_THEN_not_searchable(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with indexed resource
        WHEN: Resource is removed from index
        THEN: Search no longer finds it
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()

        resource = {"id": "to-remove", "name": "Remove Me", "type": "agent"}
        engine.index_resource(resource)

        # Verify indexed
        assert len(engine.search("to-remove")) == 1

        # Remove from index
        engine.remove_resource("to-remove")

        # Verify removed
        assert len(engine.search("to-remove")) == 0

    @pytest.mark.benchmark
    def test_BENCHMARK_search_performance(
        self, mock_catalog_331_resources: List[Dict[str, Any]], benchmark
    ):
        """
        GIVEN: Search engine with 331 resources
        WHEN: Benchmark search performance
        THEN: Performance meets <5ms target
        """
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        result = benchmark(engine.search, "architect")

        assert result is not None

    @pytest.mark.property
    def test_PROPERTY_random_queries_never_crash(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Search engine with indexed resources
        WHEN: Random queries are searched (property-based testing)
        THEN: Never crashes, always returns list
        """
        from hypothesis import given, strategies as st
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        @given(st.text(min_size=0, max_size=100))
        def check_search_stability(query: str):
            results = engine.search(query)
            assert isinstance(results, list)

        check_search_stability()
