"""Category Engine - prefix-based automatic categorization system.

This module provides automatic categorization of resources based on their ID prefixes.
Supports hierarchical category trees with efficient filtering and statistics.

Performance targets:
- Tree building: <50ms for 331 resources
- Cache hit: 2x faster than first build
- Memory: <5MB for tree structure
"""

from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


class Category(BaseModel):
    """Category extracted from resource ID prefix.

    Attributes:
        primary: Main category (e.g., "mcp")
        secondary: Optional subcategory (e.g., "dev-team")
        resource_name: Final resource name (e.g., "architect")
        full_path: Complete hierarchy path
    """

    primary: str = Field(..., description="Primary category")
    secondary: Optional[str] = Field(None, description="Secondary category/subcategory")
    resource_name: str = Field(..., description="Resource name")
    full_path: list[str] = Field(default_factory=list, description="Full category path")


class CategoryNode:
    """Node in the category tree hierarchy.

    Represents a single category or subcategory with its children and resources.
    """

    def __init__(self, name: str, parent: Optional["CategoryNode"] = None):
        """Initialize category node.

        Args:
            name: Category name
            parent: Parent category node (None for root)
        """
        self.name = name
        self.parent = parent
        self.children: dict[str, CategoryNode] = {}
        self.resources: list[dict[str, Any]] = []

    def add_child(self, name: str) -> "CategoryNode":
        """Add or get child category node.

        Args:
            name: Child category name

        Returns:
            Child CategoryNode instance
        """
        if name not in self.children:
            self.children[name] = CategoryNode(name, parent=self)
        return self.children[name]

    def add_resource(self, resource: dict[str, Any]) -> None:
        """Add resource to this category node.

        Args:
            resource: Resource dictionary
        """
        self.resources.append(resource)

    def get_all_resources(self) -> list[dict[str, Any]]:
        """Get all resources in this category and subcategories.

        Returns:
            List of all resources recursively
        """
        all_resources = list(self.resources)
        for child in self.children.values():
            all_resources.extend(child.get_all_resources())
        return all_resources

    def count_resources(self) -> int:
        """Count total resources in this category and subcategories.

        Returns:
            Total resource count
        """
        count = len(self.resources)
        for child in self.children.values():
            count += child.count_resources()
        return count


class CategoryStatistics(BaseModel):
    """Statistics about category distribution.

    Attributes:
        total_resources: Total number of resources
        total_categories: Number of top-level categories
        category_counts: Resource count per category
        category_percentages: Percentage distribution per category
    """

    total_resources: int = Field(..., description="Total resource count")
    total_categories: int = Field(..., description="Number of top-level categories")
    category_counts: dict[str, int] = Field(..., description="Resource count per category")
    category_percentages: dict[str, float] = Field(..., description="Percentage per category")


class CategoryTree:
    """Hierarchical category tree with filtering and statistics.

    Provides efficient category-based filtering and traversal of resources.
    """

    def __init__(self) -> None:
        """Initialize empty category tree."""
        self.root = CategoryNode("root")
        self.categories: list[CategoryNode] = []
        self.max_depth: int = 1
        self._category_map: dict[str, CategoryNode] = {}

    def add_resource(self, category: Category, resource: dict[str, Any]) -> None:
        """Add resource to tree based on its category.

        Args:
            category: Extracted category information
            resource: Resource dictionary to add
        """
        # Get or create primary category node
        if category.primary not in self._category_map:
            node = self.root.add_child(category.primary)
            self._category_map[category.primary] = node
            self.categories.append(node)
        else:
            node = self._category_map[category.primary]

        # Track depth
        depth = 1

        # Add secondary category if exists
        if category.secondary:
            key = f"{category.primary}.{category.secondary}"
            if key not in self._category_map:
                node = node.add_child(category.secondary)
                self._category_map[key] = node
            else:
                node = self._category_map[key]
            depth = 2

        # Add remaining path elements
        if len(category.full_path) > 2:
            for i, part in enumerate(category.full_path[2:], start=2):
                key = ".".join(category.full_path[: i + 1])
                if key not in self._category_map:
                    node = node.add_child(part)
                    self._category_map[key] = node
                else:
                    node = self._category_map[key]
                depth = i + 1

        # Update max depth
        self.max_depth = max(self.max_depth, depth)

        # Add resource to leaf node
        node.add_resource(resource)

    def get_category_count(self, name: str) -> int:
        """Get resource count for a category.

        Args:
            name: Category name

        Returns:
            Number of resources in category (including subcategories)
        """
        if name in self._category_map:
            return self._category_map[name].count_resources()
        return 0

    def get_sorted_categories(self) -> list[CategoryNode]:
        """Get categories sorted alphabetically.

        Returns:
            Alphabetically sorted list of category nodes
        """
        return sorted(self.categories, key=lambda c: c.name)

    def traverse(self, callback: Callable[[CategoryNode], None]) -> None:
        """Traverse tree and apply callback to each node.

        Args:
            callback: Function to call on each node
        """

        def _traverse_recursive(node: CategoryNode) -> None:
            callback(node)
            for child in node.children.values():
                _traverse_recursive(child)

        for category in self.categories:
            _traverse_recursive(category)

    def find_by_path(self, path: list[str]) -> Optional[CategoryNode]:
        """Find node by category path.

        Args:
            path: Category path list (e.g., ["mcp", "dev-team"])

        Returns:
            CategoryNode if found, None otherwise
        """
        key = ".".join(path)
        return self._category_map.get(key)

    def filter_by_category(self, name: str) -> list[dict[str, Any]]:
        """Filter resources by primary category.

        Args:
            name: Category name

        Returns:
            List of resources in that category
        """
        if name in self._category_map:
            return self._category_map[name].get_all_resources()
        return []

    def filter_by_path(self, path: list[str]) -> list[dict[str, Any]]:
        """Filter resources by category path.

        Args:
            path: Category path (e.g., ["mcp", "dev-team"])

        Returns:
            List of resources matching path
        """
        node = self.find_by_path(path)
        if node:
            return node.get_all_resources()
        return []

    def filter_by_category_and_type(
        self, category: str, resource_type: str
    ) -> list[dict[str, Any]]:
        """Filter resources by category and type.

        Args:
            category: Category name
            resource_type: Resource type (agent, mcp, etc.)

        Returns:
            List of resources matching both criteria
        """
        resources = self.filter_by_category(category)
        return [r for r in resources if r.get("type") == resource_type]

    def get_statistics(self) -> CategoryStatistics:
        """Get category statistics.

        Returns:
            CategoryStatistics with counts and percentages
        """
        total = sum(cat.count_resources() for cat in self.categories)
        counts = {cat.name: cat.count_resources() for cat in self.categories}
        percentages = {
            cat.name: (cat.count_resources() / total * 100) if total > 0 else 0
            for cat in self.categories
        }

        return CategoryStatistics(
            total_resources=total,
            total_categories=len(self.categories),
            category_counts=counts,
            category_percentages=percentages,
        )

    def get_category(self, name: str) -> Optional[CategoryNode]:
        """Get category node by name.

        Args:
            name: Category name

        Returns:
            CategoryNode if found, None otherwise
        """
        return self._category_map.get(name)


class CategoryEngine:
    """Engine for extracting categories and building hierarchical trees.

    Provides fast category extraction from resource IDs and efficient tree building
    with caching for performance.
    """

    def __init__(self, lazy_load: bool = False):
        """Initialize category engine.

        Args:
            lazy_load: Enable lazy loading of categories (default: False)
        """
        self.lazy_load = lazy_load
        self._cached_tree: Optional[CategoryTree] = None
        self._cache_key: Optional[int] = None

    def extract_category(self, resource_id: str) -> Category:
        """Extract category from resource ID.

        Parses hyphenated resource IDs into hierarchical categories.

        Examples:
            "mcp-architect" -> Category(primary="mcp", resource_name="architect")
            "mcp-dev-team-architect" -> Category(primary="mcp", secondary="dev-team", ...)
            "architect" -> Category(primary="general", resource_name="architect")

        Args:
            resource_id: Resource identifier to parse

        Returns:
            Category object with extracted hierarchy
        """
        # Normalize to lowercase
        normalized_id = resource_id.lower()

        # Split by hyphens
        parts = normalized_id.split("-")

        # Single word -> general category
        if len(parts) == 1:
            return Category(
                primary="general",
                secondary=None,
                resource_name=parts[0],
                full_path=["general", parts[0]],
            )

        # Two parts -> simple category-name
        if len(parts) == 2:
            return Category(
                primary=parts[0],
                secondary=None,
                resource_name=parts[1],
                full_path=[parts[0], parts[1]],
            )

        # Three or more parts -> hierarchical category
        # For 3 parts: primary-secondary-name
        # For 4+ parts: Need heuristic to decide grouping

        primary = parts[0]

        if len(parts) == 3:
            # Simple case: primary-secondary-name
            secondary = parts[1]
            resource_name = parts[2]
            full_path = [primary, secondary, resource_name]
        else:
            # 4+ parts: Use heuristic to group into 3-level hierarchy
            # Heuristic: If parts[1] is short (<=6 chars), likely just first part of secondary
            # so group middle parts together as secondary category
            # Otherwise, parts[1] is full secondary, combine remaining as resource name

            if len(parts[1]) <= 6:
                # Short first secondary part: group middle as secondary
                # e.g., "mcp-dev-team-architect" -> ["mcp", "dev-team", "architect"]
                secondary = "-".join(parts[1:-1])
                resource_name = parts[-1]
                full_path = [primary, secondary, resource_name]
            else:
                # Long secondary: keep it single, combine last parts as resource name
                # e.g., "ai-specialists-prompt-engineer" -> ["ai", "specialists", "prompt-engineer"]
                secondary = parts[1]
                resource_name = "-".join(parts[2:])
                full_path = [primary, secondary, resource_name]

        return Category(
            primary=primary,
            secondary=secondary,
            resource_name=resource_name,
            full_path=full_path,
        )

    def build_tree(self, resources: list[dict[str, Any]]) -> CategoryTree:
        """Build category tree from resources.

        Uses caching to avoid rebuilding for identical resource lists.

        Args:
            resources: List of resource dictionaries

        Returns:
            CategoryTree with all resources organized by category
        """
        # Check cache
        cache_key = id(resources)
        if self._cached_tree is not None and self._cache_key == cache_key:
            return self._cached_tree

        # Build new tree
        tree = CategoryTree()

        for resource in resources:
            resource_id = resource.get("id", "")
            if not resource_id:
                continue

            category = self.extract_category(resource_id)
            tree.add_resource(category, resource)

        # Cache the result
        self._cached_tree = tree
        self._cache_key = cache_key

        return tree

    def invalidate_cache(self) -> None:
        """Invalidate cached category tree.

        Forces next build_tree() call to create a fresh tree.
        """
        self._cached_tree = None
        self._cache_key = None
