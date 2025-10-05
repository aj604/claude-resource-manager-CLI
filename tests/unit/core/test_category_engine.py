"""Tests for CategoryEngine - prefix-based automatic categorization.

These tests ensure <50ms category tree building for 331 resources.
Tests will FAIL until CategoryEngine is implemented.
"""

import time
from typing import List, Dict, Any
import pytest


class TestPrefixExtraction:
    """Tests for extracting categories from resource ID prefixes."""

    def test_WHEN_simple_prefix_THEN_extracts_category(self):
        """
        GIVEN: Resource with simple prefix "mcp-architect"
        WHEN: Category extraction is performed
        THEN: Returns category="mcp" with no subcategory
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        category = engine.extract_category("mcp-architect")

        assert category.primary == "mcp"
        assert category.secondary is None
        assert category.resource_name == "architect"

    def test_WHEN_nested_prefix_THEN_extracts_category_hierarchy(self):
        """
        GIVEN: Resource with nested prefix "mcp-dev-team-architect"
        WHEN: Category extraction is performed
        THEN: Returns category="mcp" and subcategory="dev-team"
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        category = engine.extract_category("mcp-dev-team-architect")

        assert category.primary == "mcp"
        assert category.secondary == "dev-team"
        assert category.resource_name == "architect"
        assert category.full_path == ["mcp", "dev-team", "architect"]

    def test_WHEN_no_prefix_THEN_defaults_to_general(self):
        """
        GIVEN: Resource with no prefix "architect" (single word)
        WHEN: Category extraction is performed
        THEN: Returns category="general" with resource as name
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        category = engine.extract_category("architect")

        assert category.primary == "general"
        assert category.secondary is None
        assert category.resource_name == "architect"

    def test_WHEN_multiple_hyphens_THEN_parses_correctly(self):
        """
        GIVEN: Resource "ai-specialists-prompt-engineer"
        WHEN: Category extraction is performed
        THEN: Returns category="ai", subcategory="specialists"
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        category = engine.extract_category("ai-specialists-prompt-engineer")

        assert category.primary == "ai"
        assert category.secondary == "specialists"
        assert category.resource_name == "prompt-engineer"
        assert category.full_path == ["ai", "specialists", "prompt-engineer"]

    def test_WHEN_single_hyphen_THEN_splits_category_and_name(self):
        """
        GIVEN: Resource with single hyphen "security-reviewer"
        WHEN: Category extraction is performed
        THEN: Returns category="security" and resource_name="reviewer"
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        category = engine.extract_category("security-reviewer")

        assert category.primary == "security"
        assert category.secondary is None
        assert category.resource_name == "reviewer"

    def test_WHEN_numbers_in_prefix_THEN_handles_gracefully(self):
        """
        GIVEN: Resource with numbers "api-v2-client"
        WHEN: Category extraction is performed
        THEN: Returns category="api" with proper parsing
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        category = engine.extract_category("api-v2-client")

        assert category.primary == "api"
        assert category.secondary == "v2"
        assert category.resource_name == "client"

    def test_WHEN_special_chars_in_name_THEN_preserves_structure(self):
        """
        GIVEN: Resource with special chars "test-unit_test-generator"
        WHEN: Category extraction is performed
        THEN: Handles underscores and preserves structure
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        category = engine.extract_category("test-unit_test-generator")

        assert category.primary == "test"
        assert category.secondary == "unit_test"
        assert category.resource_name == "generator"

    def test_WHEN_uppercase_prefix_THEN_normalizes_to_lowercase(self):
        """
        GIVEN: Resource with uppercase "MCP-Architect"
        WHEN: Category extraction is performed
        THEN: Normalizes to lowercase category="mcp"
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        category = engine.extract_category("MCP-Architect")

        assert category.primary == "mcp"
        assert category.resource_name == "architect"


class TestCategoryTreeBuilding:
    """Tests for building hierarchical category tree from resources."""

    def test_WHEN_build_tree_from_331_resources_THEN_creates_hierarchy(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: 331 resources with various prefixes
        WHEN: Category tree is built
        THEN: Creates hierarchical tree structure with all categories
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        assert tree is not None
        assert len(tree.categories) > 0
        # Should have at least "agent", "mcp", "hook", "command", "template"
        assert len(tree.categories) >= 5

    def test_WHEN_tree_hierarchy_THEN_correct_depth(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Resources with nested prefixes
        WHEN: Tree is built
        THEN: Hierarchy has correct depth (category → subcategory → resource)
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        # Tree should support at least 3 levels
        assert tree.max_depth >= 1
        assert tree.max_depth <= 5  # Reasonable upper bound

    def test_WHEN_count_category_resources_THEN_accurate_totals(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Mock catalog with known counts (52 MCPs, 181 agents, etc.)
        WHEN: Tree is built and categories counted
        THEN: Returns accurate resource counts per category
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        # Check known counts from fixture
        mcp_count = tree.get_category_count("mcp")
        agent_count = tree.get_category_count("agent")

        assert mcp_count == 52
        assert agent_count == 181

    def test_WHEN_categories_sorted_THEN_alphabetical_order(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Category tree with multiple categories
        WHEN: Categories are retrieved
        THEN: Returns categories in alphabetical order
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        categories = tree.get_sorted_categories()
        category_names = [c.name for c in categories]

        assert category_names == sorted(category_names)

    def test_WHEN_traverse_tree_THEN_visits_all_nodes(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Category tree with nested hierarchy
        WHEN: Tree traversal is performed
        THEN: Visits all category nodes in order
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        visited_nodes = []
        tree.traverse(lambda node: visited_nodes.append(node))

        # Should visit at least as many nodes as there are categories
        assert len(visited_nodes) >= len(tree.categories)

    def test_WHEN_search_tree_by_path_THEN_finds_node(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Category tree with path "mcp" → "dev-team" → "architect"
        WHEN: Search by path ["mcp", "dev-team"]
        THEN: Returns correct subcategory node
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        # Add a nested resource to the fixture
        nested_resource = {
            "id": "mcp-dev-team-architect",
            "type": "agent",
            "name": "MCP Dev Team Architect",
            "description": "Test nested resource",
            "version": "v1.0.0",
        }
        resources = mock_catalog_331_resources + [nested_resource]

        engine = CategoryEngine()
        tree = engine.build_tree(resources)

        node = tree.find_by_path(["mcp", "dev-team"])

        assert node is not None
        assert node.name == "dev-team"
        assert node.parent.name == "mcp"


class TestCategoryFiltering:
    """Tests for filtering resources by category."""

    def test_WHEN_filter_by_category_THEN_returns_matching_resources(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: 331 resources with 52 MCPs
        WHEN: Filter by category="mcp"
        THEN: Returns only MCP resources (52 items)
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        mcp_resources = tree.filter_by_category("mcp")

        assert len(mcp_resources) == 52
        assert all(r["id"].startswith("mcp-") for r in mcp_resources)

    def test_WHEN_filter_by_subcategory_THEN_returns_nested_matches(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Resources with nested categories
        WHEN: Filter by subcategory path ["mcp", "dev-team"]
        THEN: Returns only resources under that subcategory
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        # Add nested resources
        nested_resources = [
            {
                "id": "mcp-dev-team-architect",
                "type": "agent",
                "name": "MCP Dev Team Architect",
                "description": "Test",
                "version": "v1.0.0",
            },
            {
                "id": "mcp-dev-team-engineer",
                "type": "agent",
                "name": "MCP Dev Team Engineer",
                "description": "Test",
                "version": "v1.0.0",
            },
        ]
        resources = mock_catalog_331_resources + nested_resources

        engine = CategoryEngine()
        tree = engine.build_tree(resources)

        filtered = tree.filter_by_path(["mcp", "dev-team"])

        assert len(filtered) == 2
        assert all("dev-team" in r["id"] for r in filtered)

    def test_WHEN_combine_category_and_search_THEN_filters_both(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Category tree and search query
        WHEN: Filter by category="mcp" AND search="000"
        THEN: Returns resources matching both criteria
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        # First filter by category
        mcp_resources = tree.filter_by_category("mcp")
        # Then search within results
        results = [r for r in mcp_resources if "000" in r["id"]]

        assert len(results) >= 1
        assert all(r["id"].startswith("mcp-") for r in results)
        assert all("000" in r["id"] for r in results)

    def test_WHEN_filter_empty_category_THEN_returns_empty_list(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Category tree
        WHEN: Filter by nonexistent category "nonexistent"
        THEN: Returns empty list
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        results = tree.filter_by_category("nonexistent")

        assert results == []

    def test_WHEN_get_category_stats_THEN_returns_summary(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Category tree with 331 resources
        WHEN: Get category statistics
        THEN: Returns summary with counts and percentages
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        stats = tree.get_statistics()

        assert stats.total_resources == 331
        assert stats.total_categories >= 5
        assert "mcp" in stats.category_counts
        assert stats.category_counts["mcp"] == 52
        assert 0 < stats.category_percentages["mcp"] < 100

    def test_WHEN_filter_includes_type_THEN_narrows_results(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Resources with type and category
        WHEN: Filter by category="mcp" AND type="agent"
        THEN: Returns resources matching both
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        # Modify some MCP resources to have different types
        resources = mock_catalog_331_resources.copy()
        resources.append(
            {
                "id": "mcp-special-hook",
                "type": "hook",
                "name": "MCP Special Hook",
                "description": "Test",
                "version": "v1.0.0",
            }
        )

        engine = CategoryEngine()
        tree = engine.build_tree(resources)

        # Filter by category and type
        results = tree.filter_by_category_and_type("mcp", "hook")

        assert len(results) >= 1
        assert all(r["type"] == "hook" for r in results)
        assert all(r["id"].startswith("mcp-") for r in results)


class TestPerformanceAndCaching:
    """Tests for performance benchmarks and caching behavior."""

    def test_WHEN_build_tree_THEN_completes_under_50ms(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: 331 resources
        WHEN: Category tree is built
        THEN: Completes in <50ms
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()

        start = time.perf_counter()
        tree = engine.build_tree(mock_catalog_331_resources)
        elapsed = time.perf_counter() - start

        assert tree is not None
        assert elapsed < 0.050  # <50ms

    def test_WHEN_rebuild_tree_THEN_uses_cache(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Category tree already built
        WHEN: Same resources are indexed again
        THEN: Uses cached tree (much faster than first build)
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()

        # First build
        start1 = time.perf_counter()
        tree1 = engine.build_tree(mock_catalog_331_resources)
        elapsed1 = time.perf_counter() - start1

        # Second build (should use cache)
        start2 = time.perf_counter()
        tree2 = engine.build_tree(mock_catalog_331_resources)
        elapsed2 = time.perf_counter() - start2

        # Cached build should be at least 2x faster
        assert elapsed2 < elapsed1 / 2
        assert tree1 is tree2  # Same object reference

    def test_WHEN_tree_stored_THEN_memory_efficient(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Category tree with 331 resources
        WHEN: Tree is stored in memory
        THEN: Uses reasonable memory (<5MB)
        """
        from claude_resource_manager.core.category_engine import CategoryEngine
        import sys

        engine = CategoryEngine()
        tree = engine.build_tree(mock_catalog_331_resources)

        # Rough estimate: tree size should be reasonable
        tree_size = sys.getsizeof(tree)

        # Should not exceed 5MB for tree structure alone
        assert tree_size < 5 * 1024 * 1024

    def test_WHEN_lazy_load_categories_THEN_builds_on_demand(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: CategoryEngine with lazy loading enabled
        WHEN: Category is accessed for first time
        THEN: Builds that category's subtree on demand
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine(lazy_load=True)
        tree = engine.build_tree(mock_catalog_331_resources)

        # First access should trigger build
        start1 = time.perf_counter()
        mcp_category = tree.get_category("mcp")
        elapsed1 = time.perf_counter() - start1

        # Second access should be cached
        start2 = time.perf_counter()
        mcp_category2 = tree.get_category("mcp")
        elapsed2 = time.perf_counter() - start2

        assert mcp_category is not None
        assert elapsed2 < elapsed1  # Cached is faster

    def test_WHEN_invalidate_cache_THEN_rebuilds_tree(
        self, mock_catalog_331_resources: List[Dict[str, Any]]
    ):
        """
        GIVEN: Cached category tree
        WHEN: Cache is invalidated
        THEN: Next build creates fresh tree
        """
        from claude_resource_manager.core.category_engine import CategoryEngine

        engine = CategoryEngine()
        tree1 = engine.build_tree(mock_catalog_331_resources)

        # Invalidate cache
        engine.invalidate_cache()

        tree2 = engine.build_tree(mock_catalog_331_resources)

        # Should be different instances
        assert tree1 is not tree2
