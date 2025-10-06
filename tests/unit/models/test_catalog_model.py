"""Tests for Catalog and Index Pydantic models.

These tests follow TDD - they will FAIL until models are implemented.
"""

from typing import Any, Dict

import pytest
from pydantic import ValidationError


class TestCatalogModel:
    """Tests for Catalog Pydantic model."""

    def test_WHEN_valid_catalog_THEN_model_created(self, sample_catalog_index: Dict[str, Any]):
        """
        GIVEN: Valid catalog index data
        WHEN: Catalog model is created
        THEN: Model is successfully instantiated
        """
        from claude_resource_manager.models.catalog import Catalog

        catalog = Catalog(**sample_catalog_index)

        assert catalog.total == 331
        assert len(catalog.types) == 5

    def test_WHEN_331_resources_THEN_index_counts_correct(
        self, sample_catalog_index: Dict[str, Any]
    ):
        """
        GIVEN: Catalog with 331 resources
        WHEN: Catalog model is created
        THEN: Resource counts by type are correct
        """
        from claude_resource_manager.models.catalog import Catalog

        catalog = Catalog(**sample_catalog_index)

        assert catalog.types["agent"]["count"] == 181
        assert catalog.types["command"]["count"] == 18
        assert catalog.types["hook"]["count"] == 64
        assert catalog.types["template"]["count"] == 16
        assert catalog.types["mcp"]["count"] == 52

    def test_WHEN_invalid_type_key_THEN_validation_error(
        self, sample_catalog_index: Dict[str, Any]
    ):
        """
        GIVEN: Catalog data with invalid type key
        WHEN: Catalog model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.catalog import Catalog

        sample_catalog_index["types"]["invalid_type"] = {"count": 10}

        with pytest.raises(ValidationError):
            Catalog(**sample_catalog_index)

    def test_WHEN_missing_total_field_THEN_validation_error(
        self, sample_catalog_index: Dict[str, Any]
    ):
        """
        GIVEN: Catalog data missing total field
        WHEN: Catalog model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.catalog import Catalog

        del sample_catalog_index["total"]

        with pytest.raises(ValidationError):
            Catalog(**sample_catalog_index)

    def test_WHEN_catalog_to_dict_THEN_serialization_correct(
        self, sample_catalog_index: Dict[str, Any]
    ):
        """
        GIVEN: Valid Catalog model
        WHEN: Model is converted to dict
        THEN: Serialization preserves structure
        """
        from claude_resource_manager.models.catalog import Catalog

        catalog = Catalog(**sample_catalog_index)
        catalog_dict = catalog.model_dump()

        assert catalog_dict["total"] == 331
        assert "types" in catalog_dict


class TestResourceIndex:
    """Tests for ResourceIndex model (per-type index)."""

    def test_WHEN_valid_resource_index_THEN_model_created(self):
        """
        GIVEN: Valid resource index data for a type
        WHEN: ResourceIndex model is created
        THEN: Model is successfully instantiated
        """
        from claude_resource_manager.models.catalog import ResourceIndex

        index_data = {
            "resources": [
                {"id": "architect", "name": "architect", "summary": "System design"},
                {"id": "security", "name": "security", "summary": "Security review"},
            ],
            "count": 2,
        }

        index = ResourceIndex(**index_data)

        assert index.count == 2
        assert len(index.resources) == 2

    def test_WHEN_count_mismatch_THEN_validation_error(self):
        """
        GIVEN: Resource index where count doesn't match resources length
        WHEN: ResourceIndex model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.catalog import ResourceIndex

        index_data = {
            "resources": [
                {"id": "architect", "name": "architect", "summary": "System design"},
            ],
            "count": 5,  # Mismatch!
        }

        with pytest.raises(ValidationError):
            ResourceIndex(**index_data)

    def test_WHEN_duplicate_resource_ids_THEN_validation_error(self):
        """
        GIVEN: Resource index with duplicate IDs
        WHEN: ResourceIndex model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.catalog import ResourceIndex

        index_data = {
            "resources": [
                {"id": "architect", "name": "architect", "summary": "System design"},
                {"id": "architect", "name": "architect-v2", "summary": "Duplicate ID"},
            ],
            "count": 2,
        }

        with pytest.raises(ValidationError) as exc_info:
            ResourceIndex(**index_data)

        assert "duplicate" in str(exc_info.value).lower()

    def test_WHEN_empty_resource_list_THEN_count_zero(self):
        """
        GIVEN: Resource index with no resources
        WHEN: ResourceIndex model is created
        THEN: Count is 0 and resources is empty
        """
        from claude_resource_manager.models.catalog import ResourceIndex

        index_data = {"resources": [], "count": 0}

        index = ResourceIndex(**index_data)

        assert index.count == 0
        assert index.resources == []


class TestCategory:
    """Tests for Category model (prefix-based categorization)."""

    def test_WHEN_valid_category_THEN_model_created(self):
        """
        GIVEN: Valid category data
        WHEN: Category model is created
        THEN: Model is successfully instantiated
        """
        from claude_resource_manager.models.catalog import Category

        category_data = {
            "primary": "mcp",
            "secondary": "dev-team",
            "tags": ["mcp", "development"],
        }

        category = Category(**category_data)

        assert category.primary == "mcp"
        assert category.secondary == "dev-team"

    def test_WHEN_category_from_id_THEN_extracted_correctly(self):
        """
        GIVEN: Resource ID with prefix pattern
        WHEN: Category is extracted from ID
        THEN: Category hierarchy is correct
        """
        from claude_resource_manager.models.catalog import Category

        # Pattern: {category}-{subcategory}-{name}
        resource_id = "mcp-dev-team-architect"

        category = Category.from_resource_id(resource_id)

        assert category.primary == "mcp"
        assert category.secondary == "dev-team"

    def test_WHEN_single_word_id_THEN_general_category(self):
        """
        GIVEN: Resource ID with no prefix (single word)
        WHEN: Category is extracted
        THEN: General category is used
        """
        from claude_resource_manager.models.catalog import Category

        resource_id = "architect"

        category = Category.from_resource_id(resource_id)

        assert category.primary == "general" or category.primary == "architect"

    def test_WHEN_category_tree_built_THEN_hierarchy_correct(self):
        """
        GIVEN: Multiple resources with prefix patterns
        WHEN: Category tree is built
        THEN: Hierarchical structure is correct
        """
        from claude_resource_manager.models.catalog import CategoryTree

        resource_ids = [
            "mcp-dev-team-architect",
            "mcp-dev-team-coder",
            "mcp-qa-team-tester",
            "database-postgres-expert",
        ]

        tree = CategoryTree.from_resource_ids(resource_ids)

        assert "mcp" in tree.categories
        assert len(tree.categories["mcp"].subcategories) == 2  # dev-team, qa-team
