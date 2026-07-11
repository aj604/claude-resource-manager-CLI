"""Pydantic models for Claude resource catalog and indexing.

This module defines models for categorizing and indexing Claude resources,
including Category, ResourceIndex, and Catalog models.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Category(BaseModel):
    """Category information for prefix-based resource categorization.

    Attributes:
        primary: Primary category (e.g., 'mcp', 'agent')
        secondary: Secondary subcategory (e.g., 'dev-team', 'qa-team')
        tags: List of category tags
    """

    primary: str = Field(..., description="Primary category")
    secondary: Optional[str] = Field(None, description="Secondary subcategory")
    tags: list[str] = Field(default_factory=list, description="Category tags")

    @classmethod
    def from_resource_id(cls, resource_id: str) -> "Category":
        """Extract category from resource ID using prefix pattern.

        Pattern: {category}-{subcategory}-{name} or {name}
        For example: "mcp-dev-team-architect" -> primary="mcp", secondary="dev-team"

        Args:
            resource_id: Resource identifier to parse

        Returns:
            Category object extracted from the ID
        """
        parts = resource_id.split("-")

        if len(parts) == 1:
            # Single word ID - use as primary or 'general'
            return cls(primary=parts[0], tags=[parts[0]])
        elif len(parts) >= 3:
            # Pattern: {category}-{subcategory}-{name} (e.g., mcp-dev-team-architect)
            # Extract primary (first part) and secondary (middle parts before last)
            primary = parts[0]
            # Join all parts except first and last to form subcategory
            # e.g., ["mcp", "dev", "team", "architect"] -> secondary = "dev-team"
            secondary = "-".join(parts[1:-1])
            tags = [primary, secondary]
            return cls(primary=primary, secondary=secondary, tags=tags)
        elif len(parts) == 2:
            # Simple two-part ID: {category}-{name}
            primary = parts[0]
            secondary = parts[1]
            tags = [primary, secondary]
            return cls(primary=primary, secondary=secondary, tags=tags)

        return cls(primary="general", tags=["general"])


class CategoryNode(BaseModel):
    """Node in category tree with subcategories.

    Attributes:
        subcategories: List of subcategory names
    """

    subcategories: list[str] = Field(default_factory=list, description="Subcategories")


class CategoryTree(BaseModel):
    """Hierarchical category tree for organizing resources.

    Attributes:
        categories: Dictionary mapping primary categories to CategoryNode objects
    """

    categories: dict[str, CategoryNode] = Field(
        default_factory=dict, description="Category hierarchy"
    )

    @classmethod
    def from_resource_ids(cls, resource_ids: list[str]) -> "CategoryTree":
        """Build category tree from list of resource IDs.

        Args:
            resource_ids: List of resource identifiers

        Returns:
            CategoryTree with hierarchical structure
        """
        tree = cls()

        for resource_id in resource_ids:
            category = Category.from_resource_id(resource_id)

            if category.primary not in tree.categories:
                tree.categories[category.primary] = CategoryNode()

            if (
                category.secondary
                and category.secondary not in tree.categories[category.primary].subcategories
            ):
                tree.categories[category.primary].subcategories.append(category.secondary)

        return tree


class ResourceIndex(BaseModel):
    """Index of resources for a specific type.

    Attributes:
        resources: List of resource summary objects
        count: Number of resources (must match list length)
    """

    resources: list[dict[str, Any]] = Field(
        default_factory=list, description="List of resource summaries"
    )
    count: int = Field(..., description="Number of resources")

    @model_validator(mode="after")
    def validate_count_matches_resources(self) -> "ResourceIndex":
        """Validate that count matches the number of resources.

        Returns:
            Self if validation passes

        Raises:
            ValueError: If count doesn't match resources length
        """
        if self.count != len(self.resources):
            raise ValueError(
                f"Count ({self.count}) does not match number of resources ({len(self.resources)})"
            )
        return self

    @model_validator(mode="after")
    def validate_no_duplicate_ids(self) -> "ResourceIndex":
        """Validate that there are no duplicate resource IDs.

        Returns:
            Self if validation passes

        Raises:
            ValueError: If duplicate IDs are found
        """
        ids = [r.get("id") for r in self.resources if "id" in r]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate resource IDs found in index")
        return self


class Catalog(BaseModel):
    """Main catalog model containing all resource types.

    Attributes:
        total: Total number of resources across all types
        types: Dictionary mapping resource types to their indices
        resources: Optional list of resource dictionaries (for simple/demo catalogs)
        version: Optional catalog version string
    """

    total: int = Field(..., description="Total number of resources")
    types: dict[str, dict[str, Any]] = Field(..., description="Resource types with counts")
    resources: Optional[list[dict[str, Any]]] = Field(
        None, description="Optional embedded resource list (for demo catalogs)"
    )
    version: Optional[str] = Field(None, description="Catalog version")

    @field_validator("types")
    @classmethod
    def validate_type_keys(cls, v: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Validate that all type keys are valid resource types.

        Args:
            v: Types dictionary to validate

        Returns:
            Validated types dictionary

        Raises:
            ValueError: If invalid type keys are found
        """
        allowed_types = ["agent", "command", "hook", "template", "mcp"]
        invalid_types = [t for t in v.keys() if t not in allowed_types]

        if invalid_types:
            raise ValueError(
                f"Invalid type keys found: {invalid_types}. Must be one of {allowed_types}"
            )

        return v
