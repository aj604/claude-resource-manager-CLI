"""Comprehensive unit tests for DependencyResolver class.

Tests cover:
- Simple dependency chains (A→B→C)
- Diamond dependencies (A→B,C; B,C→D)
- Circular dependency detection (A→B→C→A)
- Deep nesting (5+ levels)
- Missing dependencies
- Empty graphs
- Single resource (no dependencies)
- Required vs recommended dependencies
- Already installed resources
- Install order correctness (topological)

Coverage target: >90%
Test count: 27 tests
"""

from typing import Any, Dict, List
from unittest.mock import Mock

import pytest

from claude_resource_manager.core.dependency_resolver import (
    DependencyError,
    DependencyResolver,
)
from claude_resource_manager.models.catalog import Catalog
from claude_resource_manager.models.resource import Resource

# ============================================================================
# FIXTURES - Test Data Builders
# ============================================================================


@pytest.fixture
def mock_catalog_loader():
    """Mock CatalogLoader for testing dependency resolution."""
    loader = Mock()
    loader.resources = {}
    loader.get_resource = Mock(return_value=None)
    loader.load_all_resources = Mock()
    return loader


@pytest.fixture
def sample_source() -> Dict[str, Any]:
    """Sample source data for creating test resources."""
    return {
        "repo": "test-repo",
        "path": "test/path.md",
        "url": "https://raw.githubusercontent.com/test/repo/main/test.md",
    }


def create_resource_data(
    resource_id: str,
    resource_type: str = "agent",
    required_deps: List[str] = None,
    recommended_deps: List[str] = None,
) -> Dict[str, Any]:
    """Helper to create resource data dictionary.

    Args:
        resource_id: Resource identifier
        resource_type: Type of resource (agent, command, etc.)
        required_deps: List of required dependency IDs
        recommended_deps: List of recommended dependency IDs

    Returns:
        Resource data dictionary ready for Resource(**data)
    """
    data = {
        "id": resource_id,
        "type": resource_type,
        "name": resource_id.title(),
        "description": f"Test resource {resource_id}",
        "summary": f"Summary for {resource_id}",
        "version": "v1.0.0",
        "file_type": ".md",
        "source": {
            "repo": "test-repo",
            "path": f"test/{resource_id}.md",
            "url": f"https://raw.githubusercontent.com/test/repo/main/{resource_id}.md",
        },
        "install_path": f"~/.claude/{resource_type}s/{resource_id}.md",
    }

    if required_deps or recommended_deps:
        data["dependencies"] = {
            "required": required_deps or [],
            "recommended": recommended_deps or [],
        }

    return data


def create_catalog_with_resources(resources: List[Dict[str, Any]]) -> Catalog:
    """Create a Catalog from resource data dictionaries.

    Args:
        resources: List of resource data dictionaries

    Returns:
        Catalog instance with resources organized by type
    """
    types_dict = {}

    for resource in resources:
        resource_type = resource["type"]
        if resource_type not in types_dict:
            types_dict[resource_type] = {
                "count": 0,
                "resources": [],
            }
        types_dict[resource_type]["count"] += 1
        types_dict[resource_type]["resources"].append(resource)

    return Catalog(
        total=len(resources),
        types=types_dict,
    )


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


def test_init_default_max_depth():
    """Test DependencyResolver initialization with default max_depth."""
    resolver = DependencyResolver()
    assert resolver.max_depth == 5


def test_init_custom_max_depth():
    """Test DependencyResolver initialization with custom max_depth."""
    resolver = DependencyResolver(max_depth=10)
    assert resolver.max_depth == 10


def test_init_invalid_max_depth_zero():
    """Test initialization fails with max_depth = 0."""
    with pytest.raises(ValueError, match="max_depth must be at least 1"):
        DependencyResolver(max_depth=0)


def test_init_invalid_max_depth_negative():
    """Test initialization fails with negative max_depth."""
    with pytest.raises(ValueError, match="max_depth must be at least 1"):
        DependencyResolver(max_depth=-1)


# ============================================================================
# RESOLVE() METHOD TESTS - Simple Cases
# ============================================================================


def test_resolve_single_resource_no_dependencies(mock_catalog_loader):
    """Test resolving a single resource with no dependencies."""
    # Arrange
    resolver = DependencyResolver()
    resource_data = create_resource_data("standalone-agent")
    catalog = create_catalog_with_resources([resource_data])

    mock_catalog_loader.get_resource.return_value = resource_data

    # Act
    result = resolver.resolve("standalone-agent", catalog, mock_catalog_loader)

    # Assert
    assert len(result) == 1
    assert result[0].id == "standalone-agent"
    mock_catalog_loader.get_resource.assert_called_once_with("standalone-agent", "agent")


def test_resolve_simple_chain_two_levels(mock_catalog_loader):
    """Test simple dependency chain: A→B."""
    # Arrange
    resolver = DependencyResolver()

    resource_b = create_resource_data("lib-b")
    resource_a = create_resource_data("agent-a", required_deps=["lib-b"])

    catalog = create_catalog_with_resources([resource_a, resource_b])

    def mock_get_resource(resource_id, resource_type):
        if resource_id == "agent-a":
            return resource_a
        elif resource_id == "lib-b":
            return resource_b
        return None

    mock_catalog_loader.get_resource.side_effect = mock_get_resource

    # Act
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader)

    # Assert
    assert len(result) == 2
    # Dependencies should come before dependents
    assert result[0].id == "lib-b"
    assert result[1].id == "agent-a"


def test_resolve_simple_chain_three_levels(mock_catalog_loader):
    """Test simple dependency chain: A→B→C."""
    # Arrange
    resolver = DependencyResolver()

    resource_c = create_resource_data("lib-c")
    resource_b = create_resource_data("lib-b", required_deps=["lib-c"])
    resource_a = create_resource_data("agent-a", required_deps=["lib-b"])

    catalog = create_catalog_with_resources([resource_a, resource_b, resource_c])

    def mock_get_resource(resource_id, resource_type):
        resources_map = {
            "agent-a": resource_a,
            "lib-b": resource_b,
            "lib-c": resource_c,
        }
        return resources_map.get(resource_id)

    mock_catalog_loader.get_resource.side_effect = mock_get_resource

    # Act
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader)

    # Assert
    assert len(result) == 3
    # Dependencies should come before dependents: C, B, A
    assert result[0].id == "lib-c"
    assert result[1].id == "lib-b"
    assert result[2].id == "agent-a"


def test_resolve_diamond_dependency(mock_catalog_loader):
    """Test diamond dependency: A→B,C; B→D; C→D."""
    # Arrange
    resolver = DependencyResolver()

    resource_d = create_resource_data("lib-d")
    resource_b = create_resource_data("lib-b", required_deps=["lib-d"])
    resource_c = create_resource_data("lib-c", required_deps=["lib-d"])
    resource_a = create_resource_data("agent-a", required_deps=["lib-b", "lib-c"])

    catalog = create_catalog_with_resources([resource_a, resource_b, resource_c, resource_d])

    def mock_get_resource(resource_id, resource_type):
        resources_map = {
            "agent-a": resource_a,
            "lib-b": resource_b,
            "lib-c": resource_c,
            "lib-d": resource_d,
        }
        return resources_map.get(resource_id)

    mock_catalog_loader.get_resource.side_effect = mock_get_resource

    # Act
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader)

    # Assert
    assert len(result) == 4
    # D should be first (no dependencies), then B and C, then A
    result_ids = [r.id for r in result]
    assert result_ids[0] == "lib-d"
    assert "lib-b" in result_ids
    assert "lib-c" in result_ids
    assert result_ids[-1] == "agent-a"
    # D should not be duplicated even though it's a shared dependency
    assert result_ids.count("lib-d") == 1


def test_resolve_deep_nesting_five_levels(mock_catalog_loader):
    """Test deep dependency chain with 5 levels (at max_depth)."""
    # Arrange
    resolver = DependencyResolver(max_depth=5)

    # Create chain: A→B→C→D→E
    resource_e = create_resource_data("lib-e")
    resource_d = create_resource_data("lib-d", required_deps=["lib-e"])
    resource_c = create_resource_data("lib-c", required_deps=["lib-d"])
    resource_b = create_resource_data("lib-b", required_deps=["lib-c"])
    resource_a = create_resource_data("agent-a", required_deps=["lib-b"])

    catalog = create_catalog_with_resources(
        [resource_a, resource_b, resource_c, resource_d, resource_e]
    )

    def mock_get_resource(resource_id, resource_type):
        resources_map = {
            "agent-a": resource_a,
            "lib-b": resource_b,
            "lib-c": resource_c,
            "lib-d": resource_d,
            "lib-e": resource_e,
        }
        return resources_map.get(resource_id)

    mock_catalog_loader.get_resource.side_effect = mock_get_resource

    # Act
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader)

    # Assert
    assert len(result) == 5
    result_ids = [r.id for r in result]
    assert result_ids == ["lib-e", "lib-d", "lib-c", "lib-b", "agent-a"]


def test_resolve_deep_nesting_exceeds_max_depth(mock_catalog_loader):
    """Test that exceeding max_depth raises DependencyError."""
    # Arrange
    resolver = DependencyResolver(max_depth=3)

    # Create chain deeper than max_depth: A→B→C→D→E (5 levels, max is 3)
    resource_e = create_resource_data("lib-e")
    resource_d = create_resource_data("lib-d", required_deps=["lib-e"])
    resource_c = create_resource_data("lib-c", required_deps=["lib-d"])
    resource_b = create_resource_data("lib-b", required_deps=["lib-c"])
    resource_a = create_resource_data("agent-a", required_deps=["lib-b"])

    catalog = create_catalog_with_resources(
        [resource_a, resource_b, resource_c, resource_d, resource_e]
    )

    def mock_get_resource(resource_id, resource_type):
        resources_map = {
            "agent-a": resource_a,
            "lib-b": resource_b,
            "lib-c": resource_c,
            "lib-d": resource_d,
            "lib-e": resource_e,
        }
        return resources_map.get(resource_id)

    mock_catalog_loader.get_resource.side_effect = mock_get_resource

    # Act & Assert
    with pytest.raises(DependencyError, match="Maximum dependency depth \\(3\\) exceeded"):
        resolver.resolve("agent-a", catalog, mock_catalog_loader)


# ============================================================================
# RESOLVE() METHOD TESTS - Error Cases
# ============================================================================


def test_resolve_resource_not_found_in_catalog(mock_catalog_loader):
    """Test resolving a resource not in catalog raises DependencyError."""
    # Arrange
    resolver = DependencyResolver()
    catalog = create_catalog_with_resources([])

    # Act & Assert
    with pytest.raises(DependencyError, match="Resource not found in catalog: nonexistent"):
        resolver.resolve("nonexistent", catalog, mock_catalog_loader)


def test_resolve_missing_required_dependency(mock_catalog_loader):
    """Test missing required dependency raises DependencyError."""
    # Arrange
    resolver = DependencyResolver()

    # Agent A requires lib-missing, which doesn't exist
    resource_a = create_resource_data("agent-a", required_deps=["lib-missing"])
    catalog = create_catalog_with_resources([resource_a])

    mock_catalog_loader.get_resource.return_value = resource_a

    # Act & Assert
    with pytest.raises(
        DependencyError, match="Required dependency 'lib-missing' not found in catalog"
    ):
        resolver.resolve("agent-a", catalog, mock_catalog_loader)


def test_resolve_dependency_data_not_loadable(mock_catalog_loader):
    """Test when dependency exists in catalog but can't be loaded."""
    # Arrange
    resolver = DependencyResolver()

    resource_b = create_resource_data("lib-b")
    resource_a = create_resource_data("agent-a", required_deps=["lib-b"])
    catalog = create_catalog_with_resources([resource_a, resource_b])

    # Mock: agent-a loads fine, but lib-b returns None
    def mock_get_resource(resource_id, resource_type):
        if resource_id == "agent-a":
            return resource_a
        return None  # lib-b can't be loaded

    mock_catalog_loader.get_resource.side_effect = mock_get_resource
    mock_catalog_loader.load_all_resources.return_value = None

    # Act & Assert
    with pytest.raises(DependencyError, match="Dependency not found: lib-b"):
        resolver.resolve("agent-a", catalog, mock_catalog_loader)


# ============================================================================
# RESOLVE() METHOD TESTS - Recommended Dependencies
# ============================================================================


def test_resolve_recommended_dependencies_excluded_by_default(mock_catalog_loader):
    """Test that recommended dependencies are excluded by default."""
    # Arrange
    resolver = DependencyResolver()

    resource_recommended = create_resource_data("lib-recommended")
    resource_a = create_resource_data(
        "agent-a",
        required_deps=["lib-required"],
        recommended_deps=["lib-recommended"],
    )
    resource_required = create_resource_data("lib-required")

    catalog = create_catalog_with_resources([resource_a, resource_required, resource_recommended])

    def mock_get_resource(resource_id, resource_type):
        resources_map = {
            "agent-a": resource_a,
            "lib-required": resource_required,
            "lib-recommended": resource_recommended,
        }
        return resources_map.get(resource_id)

    mock_catalog_loader.get_resource.side_effect = mock_get_resource

    # Act
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader)

    # Assert - only required dependency should be included
    assert len(result) == 2
    result_ids = [r.id for r in result]
    assert "lib-required" in result_ids
    assert "lib-recommended" not in result_ids
    assert "agent-a" in result_ids


def test_resolve_recommended_dependencies_included_when_requested(mock_catalog_loader):
    """Test that recommended dependencies are included when include_recommended=True."""
    # Arrange
    resolver = DependencyResolver()

    resource_recommended = create_resource_data("lib-recommended")
    resource_a = create_resource_data(
        "agent-a",
        required_deps=["lib-required"],
        recommended_deps=["lib-recommended"],
    )
    resource_required = create_resource_data("lib-required")

    catalog = create_catalog_with_resources([resource_a, resource_required, resource_recommended])

    def mock_get_resource(resource_id, resource_type):
        resources_map = {
            "agent-a": resource_a,
            "lib-required": resource_required,
            "lib-recommended": resource_recommended,
        }
        return resources_map.get(resource_id)

    mock_catalog_loader.get_resource.side_effect = mock_get_resource

    # Act
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader, include_recommended=True)

    # Assert - both required and recommended should be included
    assert len(result) == 3
    result_ids = [r.id for r in result]
    assert "lib-required" in result_ids
    assert "lib-recommended" in result_ids
    assert "agent-a" in result_ids


def test_resolve_missing_recommended_dependency_does_not_fail(mock_catalog_loader):
    """Test that missing recommended dependencies don't cause errors."""
    # Arrange
    resolver = DependencyResolver()

    resource_a = create_resource_data(
        "agent-a",
        recommended_deps=["lib-missing-recommended"],
    )

    catalog = create_catalog_with_resources([resource_a])

    mock_catalog_loader.get_resource.return_value = resource_a

    # Act - should not raise even though recommended dependency is missing
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader, include_recommended=True)

    # Assert
    assert len(result) == 1
    assert result[0].id == "agent-a"


# ============================================================================
# GET_INSTALL_ORDER() METHOD TESTS
# ============================================================================


def test_get_install_order_single_resource():
    """Test install order with single resource (no dependencies)."""
    # Arrange
    resolver = DependencyResolver()
    resource_data = create_resource_data("standalone")
    resource = Resource(**resource_data)

    # Act
    result = resolver.get_install_order([resource])

    # Assert
    assert len(result) == 1
    assert result[0].id == "standalone"


def test_get_install_order_simple_chain():
    """Test install order for simple chain A→B."""
    # Arrange
    resolver = DependencyResolver()

    resource_b_data = create_resource_data("lib-b")
    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)

    # Act
    result = resolver.get_install_order([resource_a, resource_b])

    # Assert - B must come before A
    assert len(result) == 2
    assert result[0].id == "lib-b"
    assert result[1].id == "agent-a"


def test_get_install_order_diamond_dependency():
    """Test install order for diamond: A→B,C; B→D; C→D."""
    # Arrange
    resolver = DependencyResolver()

    resource_d_data = create_resource_data("lib-d")
    resource_b_data = create_resource_data("lib-b", required_deps=["lib-d"])
    resource_c_data = create_resource_data("lib-c", required_deps=["lib-d"])
    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b", "lib-c"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)
    resource_c = Resource(**resource_c_data)
    resource_d = Resource(**resource_d_data)

    # Act
    result = resolver.get_install_order([resource_a, resource_b, resource_c, resource_d])

    # Assert
    assert len(result) == 4
    result_ids = [r.id for r in result]

    # D must come before B and C
    d_index = result_ids.index("lib-d")
    b_index = result_ids.index("lib-b")
    c_index = result_ids.index("lib-c")
    a_index = result_ids.index("agent-a")

    assert d_index < b_index
    assert d_index < c_index
    # B and C must come before A
    assert b_index < a_index
    assert c_index < a_index


def test_get_install_order_multiple_independent_resources():
    """Test install order with multiple independent resources (no dependencies between them)."""
    # Arrange
    resolver = DependencyResolver()

    resource_a = Resource(**create_resource_data("agent-a"))
    resource_b = Resource(**create_resource_data("agent-b"))
    resource_c = Resource(**create_resource_data("agent-c"))

    # Act
    result = resolver.get_install_order([resource_a, resource_b, resource_c])

    # Assert - all three should be in result, order doesn't matter for independent resources
    assert len(result) == 3
    result_ids = [r.id for r in result]
    assert "agent-a" in result_ids
    assert "agent-b" in result_ids
    assert "agent-c" in result_ids


def test_get_install_order_with_recommended_dependencies():
    """Test install order includes recommended dependencies if present in resource list."""
    # Arrange
    resolver = DependencyResolver()

    resource_rec_data = create_resource_data("lib-recommended")
    resource_a_data = create_resource_data(
        "agent-a",
        required_deps=["lib-required"],
        recommended_deps=["lib-recommended"],
    )
    resource_req_data = create_resource_data("lib-required")

    resource_a = Resource(**resource_a_data)
    resource_req = Resource(**resource_req_data)
    resource_rec = Resource(**resource_rec_data)

    # Act
    result = resolver.get_install_order([resource_a, resource_req, resource_rec])

    # Assert - both required and recommended should be before agent-a
    assert len(result) == 3
    result_ids = [r.id for r in result]

    req_index = result_ids.index("lib-required")
    rec_index = result_ids.index("lib-recommended")
    a_index = result_ids.index("agent-a")

    assert req_index < a_index
    assert rec_index < a_index


def test_get_install_order_ignores_external_dependencies():
    """Test that install order ignores dependencies not in the resource list."""
    # Arrange
    resolver = DependencyResolver()

    # Agent-a depends on lib-external, but lib-external is not in the list
    resource_a_data = create_resource_data("agent-a", required_deps=["lib-external"])
    resource_a = Resource(**resource_a_data)

    # Act - should work fine, just return agent-a
    result = resolver.get_install_order([resource_a])

    # Assert
    assert len(result) == 1
    assert result[0].id == "agent-a"


# ============================================================================
# GET_INSTALL_ORDER() METHOD TESTS - Circular Dependencies
# ============================================================================


def test_get_install_order_detects_circular_dependency_two_nodes():
    """Test circular dependency detection: A→B→A."""
    # Arrange
    resolver = DependencyResolver()

    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b"])
    resource_b_data = create_resource_data("lib-b", required_deps=["agent-a"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)

    # Act & Assert
    with pytest.raises(DependencyError, match="Circular dependencies detected"):
        resolver.get_install_order([resource_a, resource_b])


def test_get_install_order_detects_circular_dependency_three_nodes():
    """Test circular dependency detection: A→B→C→A."""
    # Arrange
    resolver = DependencyResolver()

    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b"])
    resource_b_data = create_resource_data("lib-b", required_deps=["lib-c"])
    resource_c_data = create_resource_data("lib-c", required_deps=["agent-a"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)
    resource_c = Resource(**resource_c_data)

    # Act & Assert
    with pytest.raises(DependencyError, match="Circular dependencies detected"):
        resolver.get_install_order([resource_a, resource_b, resource_c])


# ============================================================================
# DETECT_CYCLES() METHOD TESTS
# ============================================================================


def test_detect_cycles_no_cycle():
    """Test detect_cycles returns None when no cycles exist."""
    # Arrange
    resolver = DependencyResolver()

    resource_b_data = create_resource_data("lib-b")
    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)

    # Act
    result = resolver.detect_cycles([resource_a, resource_b])

    # Assert
    assert result is None


def test_detect_cycles_simple_two_node_cycle():
    """Test detect_cycles finds A→B→A cycle."""
    # Arrange
    resolver = DependencyResolver()

    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b"])
    resource_b_data = create_resource_data("lib-b", required_deps=["agent-a"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)

    # Act
    result = resolver.detect_cycles([resource_a, resource_b])

    # Assert
    assert result is not None
    assert len(result) == 3  # Cycle closed: [A, B, A] or [B, A, B]
    # First and last should be the same (cycle closed)
    assert result[0] == result[-1]


def test_detect_cycles_three_node_cycle():
    """Test detect_cycles finds A→B→C→A cycle."""
    # Arrange
    resolver = DependencyResolver()

    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b"])
    resource_b_data = create_resource_data("lib-b", required_deps=["lib-c"])
    resource_c_data = create_resource_data("lib-c", required_deps=["agent-a"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)
    resource_c = Resource(**resource_c_data)

    # Act
    result = resolver.detect_cycles([resource_a, resource_b, resource_c])

    # Assert
    assert result is not None
    assert len(result) == 4  # Cycle closed: [A, B, C, A]
    assert result[0] == result[-1]


def test_detect_cycles_self_reference():
    """Test that Pydantic validation prevents self-referencing dependencies.

    Note: This is a validation test - Pydantic should reject self-references.
    """
    # Arrange
    from pydantic import ValidationError

    # Create resource data with self-reference
    resource_a_data = {
        "id": "agent-a",
        "type": "agent",
        "name": "Agent A",
        "description": "Test",
        "summary": "Test",
        "version": "v1.0.0",
        "file_type": ".md",
        "source": {
            "repo": "test",
            "path": "test.md",
            "url": "https://raw.githubusercontent.com/test/repo/main/test.md",
        },
        "install_path": "~/.claude/agents/agent-a.md",
        "dependencies": {
            "required": ["agent-a"],  # Self-reference
            "recommended": [],
        },
    }

    # Act & Assert - Pydantic should reject self-referencing dependency
    with pytest.raises(ValidationError, match="cannot have self-referencing dependency"):
        Resource(**resource_a_data)


def test_detect_cycles_with_recommended_dependencies():
    """Test detect_cycles detects cycles in recommended dependencies too."""
    # Arrange
    resolver = DependencyResolver()

    # A→B (required), B→C (recommended), C→A (required) = cycle
    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b"])
    resource_b_data = create_resource_data("lib-b", recommended_deps=["lib-c"])
    resource_c_data = create_resource_data("lib-c", required_deps=["agent-a"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)
    resource_c = Resource(**resource_c_data)

    # Act
    result = resolver.detect_cycles([resource_a, resource_b, resource_c])

    # Assert - cycle should be detected even with recommended dependency
    assert result is not None
    assert len(result) >= 3  # At least 3 nodes (cycle + closing node)


def test_detect_cycles_diamond_dependency_no_cycle():
    """Test detect_cycles returns None for diamond dependency (no cycle)."""
    # Arrange
    resolver = DependencyResolver()

    # A→B,C; B→D; C→D (diamond, not a cycle)
    resource_d_data = create_resource_data("lib-d")
    resource_b_data = create_resource_data("lib-b", required_deps=["lib-d"])
    resource_c_data = create_resource_data("lib-c", required_deps=["lib-d"])
    resource_a_data = create_resource_data("agent-a", required_deps=["lib-b", "lib-c"])

    resource_a = Resource(**resource_a_data)
    resource_b = Resource(**resource_b_data)
    resource_c = Resource(**resource_c_data)
    resource_d = Resource(**resource_d_data)

    # Act
    result = resolver.detect_cycles([resource_a, resource_b, resource_c, resource_d])

    # Assert
    assert result is None


def test_detect_cycles_empty_list():
    """Test detect_cycles with empty resource list."""
    # Arrange
    resolver = DependencyResolver()

    # Act
    result = resolver.detect_cycles([])

    # Assert
    assert result is None


# ============================================================================
# EDGE CASES AND INTEGRATION TESTS
# ============================================================================


def test_resolve_avoids_duplicate_resources_in_result(mock_catalog_loader):
    """Test that resolve doesn't add duplicate resources to result."""
    # Arrange
    resolver = DependencyResolver()

    # Diamond: A→B,C; B→D; C→D
    # D should appear only once in result
    resource_d = create_resource_data("lib-d")
    resource_b = create_resource_data("lib-b", required_deps=["lib-d"])
    resource_c = create_resource_data("lib-c", required_deps=["lib-d"])
    resource_a = create_resource_data("agent-a", required_deps=["lib-b", "lib-c"])

    catalog = create_catalog_with_resources([resource_a, resource_b, resource_c, resource_d])

    def mock_get_resource(resource_id, resource_type):
        resources_map = {
            "agent-a": resource_a,
            "lib-b": resource_b,
            "lib-c": resource_c,
            "lib-d": resource_d,
        }
        return resources_map.get(resource_id)

    mock_catalog_loader.get_resource.side_effect = mock_get_resource

    # Act
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader)

    # Assert - no duplicates
    result_ids = [r.id for r in result]
    assert len(result_ids) == len(set(result_ids))  # No duplicates
    assert result_ids.count("lib-d") == 1


def test_resolve_calls_load_all_resources_when_dependency_not_found(mock_catalog_loader):
    """Test that resolve calls load_all_resources when dependency is not initially found."""
    # Arrange
    resolver = DependencyResolver()

    resource_b = create_resource_data("lib-b")
    resource_a = create_resource_data("agent-a", required_deps=["lib-b"])
    catalog = create_catalog_with_resources([resource_a, resource_b])

    call_count = 0

    def mock_get_resource(resource_id, resource_type):
        nonlocal call_count
        call_count += 1
        if resource_id == "agent-a":
            return resource_a
        # First call for lib-b returns None, second call (after load_all) returns data
        if resource_id == "lib-b":
            if call_count <= 2:
                return None
            return resource_b
        return None

    mock_catalog_loader.get_resource.side_effect = mock_get_resource
    mock_catalog_loader.resources = {}  # Initially empty

    def mock_load_all():
        mock_catalog_loader.resources = {"lib-b": resource_b}

    mock_catalog_loader.load_all_resources.side_effect = mock_load_all

    # Act
    result = resolver.resolve("agent-a", catalog, mock_catalog_loader)

    # Assert
    mock_catalog_loader.load_all_resources.assert_called_once()
    assert len(result) == 2


def test_get_install_order_empty_list():
    """Test get_install_order with empty resource list."""
    # Arrange
    resolver = DependencyResolver()

    # Act
    result = resolver.get_install_order([])

    # Assert
    assert result == []


def test_find_resource_type_finds_correct_type(mock_catalog_loader):
    """Test _find_resource_type helper method."""
    # Arrange
    resolver = DependencyResolver()

    resource_agent = create_resource_data("my-agent", resource_type="agent")
    resource_command = create_resource_data("my-command", resource_type="command")

    catalog = create_catalog_with_resources([resource_agent, resource_command])

    # Act
    agent_type = resolver._find_resource_type("my-agent", catalog)
    command_type = resolver._find_resource_type("my-command", catalog)
    nonexistent_type = resolver._find_resource_type("nonexistent", catalog)

    # Assert
    assert agent_type == "agent"
    assert command_type == "command"
    assert nonexistent_type is None
