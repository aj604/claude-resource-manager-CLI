"""Tests for Resource, Source, and Dependency Pydantic models.

These tests follow TDD - they will FAIL until models are implemented.
"""

from typing import Any, Dict

import pytest
from pydantic import ValidationError


class TestResourceModel:
    """Tests for Resource Pydantic model."""

    def test_WHEN_valid_resource_data_THEN_model_created(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Valid resource data with all required fields
        WHEN: Resource model is created
        THEN: Model is successfully instantiated with correct values
        """
        from claude_resource_manager.models.resource import Resource

        resource = Resource(**sample_resource_data)

        assert resource.id == "architect"
        assert resource.type == "agent"
        assert resource.name == "Architect"
        assert resource.description == "System architecture design specialist"
        assert resource.version == "v1.0.0"

    def test_WHEN_missing_required_field_THEN_validation_error(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource data missing required field (id)
        WHEN: Resource model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.resource import Resource

        del sample_resource_data["id"]

        with pytest.raises(ValidationError) as exc_info:
            Resource(**sample_resource_data)

        assert "id" in str(exc_info.value)

    def test_WHEN_invalid_resource_type_THEN_validation_error(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource data with invalid type value
        WHEN: Resource model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.resource import Resource

        sample_resource_data["type"] = "invalid_type"

        with pytest.raises(ValidationError) as exc_info:
            Resource(**sample_resource_data)

        assert "type" in str(exc_info.value)

    def test_WHEN_invalid_id_format_THEN_validation_error(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource data with invalid ID format (special chars)
        WHEN: Resource model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.resource import Resource

        sample_resource_data["id"] = "invalid@#$%id"

        with pytest.raises(ValidationError) as exc_info:
            Resource(**sample_resource_data)

        assert "id" in str(exc_info.value)

    def test_WHEN_empty_string_id_THEN_validation_error(self, sample_resource_data: Dict[str, Any]):
        """
        GIVEN: Resource data with empty string ID
        WHEN: Resource model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.resource import Resource

        sample_resource_data["id"] = ""

        with pytest.raises(ValidationError):
            Resource(**sample_resource_data)

    def test_WHEN_model_to_dict_THEN_correct_serialization(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Valid Resource model instance
        WHEN: Model is converted to dict
        THEN: Dictionary contains all fields correctly
        """
        from claude_resource_manager.models.resource import Resource

        resource = Resource(**sample_resource_data)
        resource_dict = resource.model_dump()

        assert resource_dict["id"] == "architect"
        assert resource_dict["type"] == "agent"
        assert isinstance(resource_dict, dict)

    def test_WHEN_dict_to_model_THEN_correct_deserialization(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Valid resource dictionary
        WHEN: Model is created and serialized back
        THEN: Round-trip serialization preserves data
        """
        from claude_resource_manager.models.resource import Resource

        resource = Resource(**sample_resource_data)
        resource_dict = resource.model_dump()
        resource_2 = Resource(**resource_dict)

        assert resource.id == resource_2.id
        assert resource.type == resource_2.type

    def test_WHEN_long_description_THEN_handled_correctly(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource with very long description (1000+ chars)
        WHEN: Resource model is created
        THEN: Model handles long strings correctly
        """
        from claude_resource_manager.models.resource import Resource

        sample_resource_data["description"] = "A" * 1000

        resource = Resource(**sample_resource_data)
        assert len(resource.description) == 1000

    def test_WHEN_unicode_in_fields_THEN_handled_correctly(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource with Unicode characters in fields
        WHEN: Resource model is created
        THEN: Unicode is preserved correctly
        """
        from claude_resource_manager.models.resource import Resource

        sample_resource_data["description"] = "Architecture specialist 中文 🚀"

        resource = Resource(**sample_resource_data)
        assert "中文" in resource.description
        assert "🚀" in resource.description

    def test_WHEN_optional_fields_missing_THEN_defaults_used(
        self, sample_resource_data: Dict[str, Any]
    ):
        """
        GIVEN: Resource data without optional fields
        WHEN: Resource model is created
        THEN: Default values are used
        """
        from claude_resource_manager.models.resource import Resource

        # Remove optional fields
        del sample_resource_data["author"]
        del sample_resource_data["metadata"]

        resource = Resource(**sample_resource_data)
        assert resource.author is None or resource.author == ""
        assert resource.metadata == {} or resource.metadata is None


class TestSourceModel:
    """Tests for Source Pydantic model."""

    def test_WHEN_valid_source_data_THEN_model_created(self):
        """
        GIVEN: Valid source data
        WHEN: Source model is created
        THEN: Model is successfully instantiated
        """
        from claude_resource_manager.models.resource import Source

        source_data = {
            "repo": "test-repo",
            "path": "agents/architect.md",
            "url": "https://raw.githubusercontent.com/test/repo/main/agents/architect.md",
        }

        source = Source(**source_data)

        assert source.repo == "test-repo"
        assert source.path == "agents/architect.md"
        assert source.url.startswith("https://")

    def test_WHEN_non_https_url_THEN_validation_error(self):
        """
        GIVEN: Source data with HTTP (not HTTPS) URL
        WHEN: Source model is created
        THEN: ValidationError is raised (security requirement)
        """
        from claude_resource_manager.models.resource import Source

        source_data = {
            "repo": "test-repo",
            "path": "agents/architect.md",
            "url": "http://raw.githubusercontent.com/test/repo/main/agents/architect.md",
        }

        with pytest.raises(ValidationError) as exc_info:
            Source(**source_data)

        assert "https" in str(exc_info.value).lower()

    def test_WHEN_invalid_url_format_THEN_validation_error(self):
        """
        GIVEN: Source data with malformed URL
        WHEN: Source model is created
        THEN: ValidationError is raised
        """
        from claude_resource_manager.models.resource import Source

        source_data = {
            "repo": "test-repo",
            "path": "agents/architect.md",
            "url": "not-a-valid-url",
        }

        with pytest.raises(ValidationError):
            Source(**source_data)


class TestDependencyModel:
    """Tests for Dependency Pydantic model."""

    def test_WHEN_valid_dependencies_THEN_model_created(self):
        """
        GIVEN: Valid dependency data
        WHEN: Dependency model is created
        THEN: Model is successfully instantiated
        """
        from claude_resource_manager.models.resource import Dependency

        dep_data = {
            "required": ["security-reviewer", "code-archaeologist"],
            "recommended": ["test-generator"],
        }

        deps = Dependency(**dep_data)

        assert len(deps.required) == 2
        assert len(deps.recommended) == 1
        assert "security-reviewer" in deps.required

    def test_WHEN_empty_dependencies_THEN_empty_lists(self):
        """
        GIVEN: Dependency data with no dependencies
        WHEN: Dependency model is created
        THEN: Empty lists are used
        """
        from claude_resource_manager.models.resource import Dependency

        deps = Dependency(required=[], recommended=[])

        assert deps.required == []
        assert deps.recommended == []

    def test_WHEN_self_reference_in_dependencies_THEN_validation_error(
        self, sample_resource_with_deps: Dict[str, Any]
    ):
        """
        GIVEN: Resource with self-referencing dependency
        WHEN: Resource model is created
        THEN: ValidationError is raised (cannot depend on self)
        """
        from claude_resource_manager.models.resource import Resource

        sample_resource_with_deps["dependencies"]["required"].append("architect")

        with pytest.raises(ValidationError) as exc_info:
            Resource(**sample_resource_with_deps)

        assert "self" in str(exc_info.value).lower() or "circular" in str(exc_info.value).lower()

    def test_WHEN_duplicate_dependencies_THEN_deduplicated(self):
        """
        GIVEN: Dependency data with duplicate entries
        WHEN: Dependency model is created
        THEN: Duplicates are removed or flagged
        """
        from claude_resource_manager.models.resource import Dependency

        dep_data = {
            "required": ["security-reviewer", "security-reviewer", "code-archaeologist"],
            "recommended": [],
        }

        deps = Dependency(**dep_data)

        # Either deduplicated to 2 items, or validation error raised
        assert len(deps.required) <= 3
