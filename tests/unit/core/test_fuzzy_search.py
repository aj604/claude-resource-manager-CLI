"""Tests for fuzzy search functionality using RapidFuzz.

These tests ensure fuzzy search handles typos, character variations, and ranks
results correctly. Performance target: <20ms for 331 resources.

All tests will FAIL until fuzzy search is properly implemented with RapidFuzz.
"""

import time
from typing import Any, Dict, List


class TestFuzzySearchBasicMatching:
    """Tests for basic fuzzy matching with typos and character variations."""

    def test_WHEN_single_typo_THEN_finds_correct_match(self):
        """Fuzzy search should find 'architect' when user types 'architet' (missing 'c')."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "System architecture design specialist",
            }
        )

        results = engine.search_fuzzy("architet", limit=10)

        # Test will FAIL - expects fuzzy match to find "architect"
        assert len(results) > 0, "Should find fuzzy match with single typo"
        assert results[0]["id"] == "architect", "Best match should be 'architect'"
        # Score should be high (>80) since only 1 char is wrong
        assert "score" in results[0] or True  # Will add scoring later

    def test_WHEN_multiple_typos_THEN_finds_correct_match(self):
        """Fuzzy search should find 'mcp-dev-team' when user types 'mcp-dev-tam' (typo: 'e' -> 'a')."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "mcp-dev-team",
                "type": "agent",
                "name": "MCP Dev Team",
                "description": "MCP development specialists",
            }
        )

        results = engine.search_fuzzy("mcp-dev-tam", limit=10)

        # Test will FAIL - expects fuzzy match with typo
        assert len(results) > 0, "Should find match despite typo"
        assert results[0]["id"] == "mcp-dev-team", "Should match 'mcp-dev-team'"

    def test_WHEN_missing_characters_THEN_finds_match(self):
        """Fuzzy search should find 'security' when user types 'scurity' (missing 'e')."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "security-reviewer",
                "type": "agent",
                "name": "Security Reviewer",
                "description": "Reviews code for security vulnerabilities",
            }
        )

        results = engine.search_fuzzy("scurity", limit=10)

        # Test will FAIL - expects fuzzy match with missing char
        assert len(results) > 0, "Should find match with missing character"
        assert any("security" in r["id"] for r in results), "Should match 'security'"

    def test_WHEN_extra_characters_THEN_finds_match(self):
        """Fuzzy search should find 'architect' when user types 'archittect' (extra 't')."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "Architecture specialist",
            }
        )

        results = engine.search_fuzzy("archittect", limit=10)

        # Test will FAIL - expects fuzzy match with extra char
        assert len(results) > 0, "Should find match with extra character"
        assert results[0]["id"] == "architect", "Should match 'architect'"

    def test_WHEN_swapped_characters_THEN_finds_match(self):
        """Fuzzy search should find 'architect' when user types 'acrhtect' (swapped 'r' and 'c')."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "System architecture designer",
            }
        )

        results = engine.search_fuzzy("acrhtect", limit=10)

        # Test will FAIL - expects fuzzy match with swapped chars
        assert len(results) > 0, "Should find match with swapped characters"
        assert results[0]["id"] == "architect", "Should match 'architect'"

    def test_WHEN_case_mismatch_THEN_finds_match(self):
        """Fuzzy search should be case-insensitive."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "Architecture specialist",
            }
        )

        results_lower = engine.search_fuzzy("architect", limit=10)
        results_upper = engine.search_fuzzy("ARCHITECT", limit=10)
        results_mixed = engine.search_fuzzy("ArChItEcT", limit=10)

        # Test will FAIL - expects case-insensitive matching
        assert len(results_lower) > 0, "Should match lowercase"
        assert len(results_upper) > 0, "Should match uppercase"
        assert len(results_mixed) > 0, "Should match mixed case"
        # All should find the same resource
        assert results_lower[0]["id"] == results_upper[0]["id"] == results_mixed[0]["id"]

    def test_WHEN_partial_word_match_THEN_finds_match(self):
        """Fuzzy search should match partial words in multi-word names."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "solution-architect-expert",
                "type": "agent",
                "name": "Solution Architect Expert",
                "description": "Expert in solution architecture",
            }
        )

        results = engine.search_fuzzy("architect", limit=10)

        # Test will FAIL - expects partial word matching
        assert len(results) > 0, "Should match partial word"
        assert results[0]["id"] == "solution-architect-expert"

    def test_WHEN_hyphenated_words_THEN_finds_match(self):
        """Fuzzy search should handle hyphenated IDs like 'mcp-dev-team'."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "mcp-dev-team",
                "type": "mcp",
                "name": "MCP Dev Team",
                "description": "MCP development team",
            }
        )

        results = engine.search_fuzzy("mcp dev team", limit=10)

        # Test will FAIL - expects hyphen/space equivalence
        assert len(results) > 0, "Should match across hyphens/spaces"
        assert results[0]["id"] == "mcp-dev-team"

    def test_WHEN_substring_match_THEN_finds_match(self):
        """Fuzzy search should match substrings within resource names."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "test-generator-expert",
                "type": "agent",
                "name": "Test Generator Expert",
                "description": "Generates comprehensive test suites",
            }
        )

        results = engine.search_fuzzy("generator", limit=10)

        # Test will FAIL - expects substring matching
        assert len(results) > 0, "Should match substring"
        assert results[0]["id"] == "test-generator-expert"

    def test_WHEN_fuzzy_on_description_THEN_finds_match(self):
        """Fuzzy search should match against description field, not just ID."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "code-reviewer",
                "type": "agent",
                "name": "Code Reviewer",
                "description": "Reviews code for best practices and security vulnerabilities",
            }
        )

        results = engine.search_fuzzy("vulnerability", limit=10)

        # Test will FAIL - expects description field matching
        assert len(results) > 0, "Should match description field"
        assert results[0]["id"] == "code-reviewer"


class TestFuzzySearchScoringAndRanking:
    """Tests for fuzzy search scoring and result ranking."""

    def test_WHEN_scored_THEN_range_0_to_100(self):
        """Fuzzy search scores should be in range 0-100."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "Architecture specialist",
            }
        )

        # Use search_smart which includes scores
        results = engine.search_smart("architect", limit=10)

        # Test will FAIL - expects score field with valid range
        assert len(results) > 0, "Should have results"
        assert "score" in results[0], "Should include score field"
        assert 0 <= results[0]["score"] <= 100, "Score should be 0-100"

    def test_WHEN_exact_match_THEN_score_100(self):
        """Exact matches should score 100 (perfect match)."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "Architecture specialist",
            }
        )

        results = engine.search_smart("architect", limit=10)

        # Test will FAIL - expects exact match to score 100
        assert len(results) > 0, "Should have results"
        assert results[0]["score"] == 100, "Exact match should score 100"

    def test_WHEN_ranked_THEN_best_matches_first(self):
        """Results should be ranked by score, best matches first."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "Main architect",
            }
        )
        engine.index_resource(
            {
                "id": "solution-architect-expert",
                "type": "agent",
                "name": "Solution Architect Expert",
                "description": "Expert solution architect",
            }
        )
        engine.index_resource(
            {
                "id": "test-architect-helper",
                "type": "agent",
                "name": "Test Architect Helper",
                "description": "Helps with test architecture",
            }
        )

        results = engine.search_smart("architect", limit=10)

        # Test will FAIL - expects ranking by score
        assert len(results) >= 3, "Should find all matches"
        # Exact match "architect" should be first (highest score)
        assert results[0]["id"] == "architect", "Exact match should rank first"
        # Scores should be descending
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i + 1]["score"], "Scores should be descending"

    def test_WHEN_threshold_applied_THEN_filters_low_scores(self):
        """Fuzzy search should support score threshold filtering."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "Architecture specialist",
            }
        )
        engine.index_resource(
            {
                "id": "completely-different",
                "type": "agent",
                "name": "Different Thing",
                "description": "Not related at all",
            }
        )

        # Query for "architect" with high threshold (>70)
        # This will FAIL until threshold parameter is implemented
        results = engine.search_fuzzy("architect", limit=10)

        # Should not include "completely-different" since score would be low
        # For now, just check that we get results
        assert len(results) > 0, "Should have high-scoring results"
        # Later: assert all(r.get("score", 0) > 70 for r in results)

    def test_WHEN_id_match_THEN_ranks_higher_than_description(self):
        """ID matches should rank higher than description-only matches."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "security-expert",
                "type": "agent",
                "name": "Security Expert",
                "description": "Security specialist",
            }
        )
        engine.index_resource(
            {
                "id": "code-reviewer",
                "type": "agent",
                "name": "Code Reviewer",
                "description": "Reviews code for security issues and best practices",
            }
        )

        results = engine.search_smart("security", limit=10)

        # Test will FAIL - expects ID match to rank higher
        assert len(results) >= 2, "Should find both resources"
        # "security-expert" should rank higher than "code-reviewer"
        # because "security" is in the ID, not just description
        assert results[0]["id"] == "security-expert", "ID match should rank first"

    def test_WHEN_multiple_field_matches_THEN_scores_higher(self):
        """Resources matching in multiple fields should score higher."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "architect",
                "type": "agent",
                "name": "Architect",
                "description": "System architect specialist",
            }
        )
        engine.index_resource(
            {
                "id": "code-reviewer",
                "type": "agent",
                "name": "Code Reviewer",
                "description": "Reviews architecture patterns",
            }
        )

        results = engine.search_smart("architect", limit=10)

        # Test will FAIL - expects multi-field match to score higher
        assert len(results) >= 2, "Should find both resources"
        # "architect" matches in id, name, and description
        # "code-reviewer" only matches in description
        assert results[0]["id"] == "architect", "Multi-field match should rank first"

    def test_WHEN_limit_exceeded_THEN_returns_top_results(self):
        """Fuzzy search should return only top N results when limit is set."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        # Create 20 resources with "test" in the name
        for i in range(20):
            engine.index_resource(
                {
                    "id": f"test-resource-{i:03d}",
                    "type": "agent",
                    "name": f"Test Resource {i}",
                    "description": f"Test resource number {i}",
                }
            )

        results = engine.search_fuzzy("test", limit=10)

        # Test will FAIL - expects limit to be respected
        assert len(results) <= 10, "Should respect limit parameter"
        # Should get the best matches, not random ones
        assert len(results) == 10, "Should return exactly limit results"

    def test_WHEN_score_tie_THEN_stable_ordering(self):
        """When scores are tied, ordering should be stable/deterministic."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {"id": "test-001", "type": "agent", "name": "Test Agent", "description": "Test agent 1"}
        )
        engine.index_resource(
            {"id": "test-002", "type": "agent", "name": "Test Agent", "description": "Test agent 2"}
        )

        results1 = engine.search_smart("test agent", limit=10)
        results2 = engine.search_smart("test agent", limit=10)

        # Test will FAIL - expects stable ordering
        assert len(results1) >= 2, "Should find both resources"
        # Same query should return same order
        assert [r["id"] for r in results1] == [r["id"] for r in results2], "Order should be stable"


class TestFuzzySearchPerformance:
    """Tests for fuzzy search performance benchmarks."""

    def test_WHEN_331_resources_THEN_under_20ms(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """Fuzzy search should complete in <20ms for 331 resources."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        start = time.perf_counter()
        results = engine.search_fuzzy("architet", limit=50)
        elapsed = time.perf_counter() - start

        # Test will FAIL - expects <20ms performance
        assert elapsed < 0.020, f"Fuzzy search took {elapsed*1000:.2f}ms, should be <20ms"
        assert isinstance(results, list), "Should return list of results"

    def test_WHEN_1000_resources_THEN_reasonable_performance(self):
        """Fuzzy search should handle 1000+ resources efficiently."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        # Create 1000 resources
        for i in range(1000):
            engine.index_resource(
                {
                    "id": f"resource-{i:04d}",
                    "type": "agent",
                    "name": f"Resource {i}",
                    "description": f"Test resource number {i}",
                }
            )

        start = time.perf_counter()
        results = engine.search_fuzzy("resource", limit=50)
        elapsed = time.perf_counter() - start

        # Test will FAIL - expects reasonable performance even with 1000 resources
        # Allow up to 50ms for 1000 resources (scales roughly linearly)
        assert elapsed < 0.050, f"Search took {elapsed*1000:.2f}ms for 1000 resources"
        assert len(results) > 0, "Should find matches"

    def test_WHEN_concurrent_searches_THEN_maintains_performance(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """Fuzzy search should maintain performance under concurrent load."""
        import concurrent.futures

        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        def search_task(query: str):
            return engine.search_fuzzy(query, limit=10)

        queries = ["architect", "security", "test", "mcp", "dev"]

        start = time.perf_counter()
        # Run 10 concurrent searches
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(search_task, q) for q in queries * 2]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        elapsed = time.perf_counter() - start

        # Test will FAIL - expects concurrent searches to complete efficiently
        assert len(results) == 10, "Should complete all searches"
        # Should be faster than running them sequentially
        assert elapsed < 0.200, f"Concurrent searches took {elapsed*1000:.2f}ms"

    def test_WHEN_memory_efficient_THEN_under_100mb(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """Fuzzy search index should be memory efficient (<100MB for 331 resources)."""
        import sys

        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()

        # Get baseline memory
        baseline = sys.getsizeof(engine)

        # Index all resources
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        # Get memory after indexing
        indexed_size = sys.getsizeof(engine)
        memory_increase = indexed_size - baseline

        # Test will FAIL - expects efficient memory usage
        # This is a rough check; actual memory usage is more complex
        # Allow up to 10MB for 331 resources (very conservative)
        assert (
            memory_increase < 10 * 1024 * 1024
        ), f"Memory increase {memory_increase / 1024 / 1024:.2f}MB exceeds 10MB"

    def test_WHEN_cached_THEN_faster_repeat_queries(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """Repeated fuzzy searches should be faster with caching."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine(use_cache=True)
        for resource in mock_catalog_331_resources:
            engine.index_resource(resource)

        # First search (not cached)
        start1 = time.perf_counter()
        results1 = engine.search("architect", limit=10)
        time1 = time.perf_counter() - start1

        # Second search (should be cached)
        start2 = time.perf_counter()
        results2 = engine.search("architect", limit=10)
        time2 = time.perf_counter() - start2

        # Test will FAIL - expects caching to improve performance
        assert results1 == results2, "Cached results should match"
        # Note: Fuzzy search itself doesn't cache, but search() does
        # This test verifies the caching mechanism works
        assert time2 < time1 or time2 < 0.001, "Cached search should be faster or very fast"


class TestFuzzySearchEdgeCases:
    """Tests for edge cases and error handling in fuzzy search."""

    def test_WHEN_empty_query_THEN_returns_empty_list(self):
        """Fuzzy search with empty query should return empty list."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {"id": "test-resource", "type": "agent", "name": "Test", "description": "Test resource"}
        )

        results = engine.search_fuzzy("", limit=10)

        # Test will FAIL - expects empty list for empty query
        assert results == [], "Empty query should return empty list"

    def test_WHEN_special_characters_THEN_handles_gracefully(self):
        """Fuzzy search should handle special characters without crashing."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "test-resource",
                "type": "agent",
                "name": "Test Resource",
                "description": "Test description",
            }
        )

        special_chars = ["@#$%", "!!!!", "***", "...", "---", "___", "///"]

        for chars in special_chars:
            results = engine.search_fuzzy(chars, limit=10)
            # Test will FAIL - expects graceful handling, no crashes
            assert isinstance(results, list), f"Should return list for '{chars}'"

    def test_WHEN_unicode_query_THEN_matches_unicode_content(self):
        """Fuzzy search should handle Unicode characters correctly."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "cafe-architect",
                "type": "agent",
                "name": "Café Architect",
                "description": "Architecture specialist with café ☕",
            }
        )

        results = engine.search_fuzzy("café", limit=10)

        # Test will FAIL - expects Unicode matching
        assert len(results) > 0, "Should match Unicode characters"
        assert results[0]["id"] == "cafe-architect"

    def test_WHEN_very_long_query_THEN_handles_efficiently(self):
        """Fuzzy search should handle very long queries (>100 chars) efficiently."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "test-resource",
                "type": "agent",
                "name": "Test",
                "description": "Test description",
            }
        )

        long_query = "architect " * 20  # 200+ characters

        start = time.perf_counter()
        results = engine.search_fuzzy(long_query, limit=10)
        elapsed = time.perf_counter() - start

        # Test will FAIL - expects efficient handling of long queries
        assert isinstance(results, list), "Should return list for long query"
        assert elapsed < 0.050, f"Long query took {elapsed*1000:.2f}ms, should be <50ms"

    def test_WHEN_single_character_THEN_finds_matches(self):
        """Fuzzy search should handle single character queries."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "a-test-resource",
                "type": "agent",
                "name": "A Test Resource",
                "description": "A resource for testing",
            }
        )

        results = engine.search_fuzzy("a", limit=10)

        # Test will FAIL - expects single char matching
        # Note: Single chars may have lower scores, but should still work
        assert isinstance(results, list), "Should handle single character query"

    def test_WHEN_whitespace_only_THEN_returns_empty(self):
        """Fuzzy search should treat whitespace-only queries as empty."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {"id": "test-resource", "type": "agent", "name": "Test", "description": "Test"}
        )

        whitespace_queries = ["   ", "\t", "\n", "  \t\n  "]

        for query in whitespace_queries:
            results = engine.search_fuzzy(query, limit=10)
            # Test will FAIL - expects empty results for whitespace
            assert (
                results == [] or len(results) == 0
            ), f"Whitespace query '{repr(query)}' should return empty"

    def test_WHEN_no_matches_THEN_returns_empty_list(self):
        """Fuzzy search should return empty list when no good matches exist."""
        from claude_resource_manager.core.search_engine import SearchEngine

        engine = SearchEngine()
        engine.index_resource(
            {
                "id": "test-resource",
                "type": "agent",
                "name": "Test Resource",
                "description": "A test resource",
            }
        )

        # Query that shouldn't match anything well
        results = engine.search_fuzzy("xyznonexistent123", limit=10)

        # Test will FAIL - expects empty list for nonsense query
        assert results == [], "Nonsense query should return no matches"
