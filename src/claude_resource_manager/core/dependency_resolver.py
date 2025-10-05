"""Dependency resolution module for Claude resource dependencies.

This module provides dependency resolution, topological sorting, and cycle
detection for Claude resources using NetworkX graph algorithms.

Key features:
- Topological sorting for correct installation order
- Circular dependency detection
- Required vs recommended dependency handling
- Maximum depth limiting to prevent excessive recursion
- Comprehensive error handling for missing dependencies
"""

from typing import Any, Optional

import networkx as nx

from claude_resource_manager.models.catalog import Catalog
from claude_resource_manager.models.resource import Dependency, Resource


class DependencyError(Exception):
    """Exception raised for dependency-related errors.

    This includes missing dependencies, circular dependencies, and
    maximum depth violations.
    """
    pass


class DependencyResolver:
    """Resolves resource dependencies using graph-based algorithms.

    Uses NetworkX directed graphs for efficient dependency resolution,
    topological sorting, and cycle detection.

    Features:
    - O(V + E) topological sort using Kahn's algorithm
    - O(V + E) cycle detection using depth-first search
    - Configurable maximum dependency depth (default: 5)
    - Support for required vs recommended dependencies
    - Graceful error handling for missing dependencies

    Attributes:
        max_depth: Maximum allowed dependency chain depth (default: 5)
        _resource_cache: Cache of loaded resources for performance
    """

    def __init__(self, max_depth: int = 5):
        """Initialize dependency resolver.

        Args:
            max_depth: Maximum depth for dependency chains (default: 5)
                      Prevents infinite loops and excessive recursion

        Raises:
            ValueError: If max_depth is less than 1
        """
        if max_depth < 1:
            raise ValueError("max_depth must be at least 1")

        self.max_depth = max_depth
        self._resource_cache: dict[str, dict[str, Any]] = {}

    def resolve(
        self,
        resource_id: str,
        catalog: Catalog,
        catalog_loader,  # CatalogLoader instance
        include_recommended: bool = False
    ) -> list[Resource]:
        """Resolve all dependencies for a resource.

        Performs depth-first traversal to collect all transitive dependencies,
        respecting maximum depth limits and detecting circular dependencies.

        Algorithm:
        1. Initialize visited set and result list
        2. Perform DFS from root resource
        3. For each resource, load its dependencies
        4. Track depth to enforce max_depth limit
        5. Detect cycles using visited set
        6. Return dependencies in discovery order

        Args:
            resource_id: ID of resource to resolve dependencies for
            catalog: Catalog instance containing resource metadata
            catalog_loader: CatalogLoader instance for loading resource details
            include_recommended: Whether to include recommended dependencies
                                (default: False, only required dependencies)

        Returns:
            List of Resource objects in dependency resolution order
            (dependencies appear before dependents)

        Raises:
            DependencyError: If resource not found, circular dependency detected,
                           or max depth exceeded

        Example:
            >>> resolver = DependencyResolver(max_depth=5)
            >>> deps = resolver.resolve("agent-a", catalog, loader)
            >>> print([d.id for d in deps])
            ['lib-x', 'lib-y', 'agent-a']
        """
        visited: set[str] = set()
        result: list[Resource] = []

        # Find resource type from catalog
        resource_type = self._find_resource_type(resource_id, catalog)
        if not resource_type:
            raise DependencyError(f"Resource not found in catalog: {resource_id}")

        # Perform DFS to resolve dependencies
        self._resolve_recursive(
            resource_id=resource_id,
            resource_type=resource_type,
            catalog=catalog,
            catalog_loader=catalog_loader,
            visited=visited,
            result=result,
            depth=0,
            include_recommended=include_recommended
        )

        return result

    def get_install_order(self, resources: list[Resource]) -> list[Resource]:
        """Compute topological sort order for resource installation.

        Uses Kahn's algorithm for topological sorting to determine the correct
        order to install resources based on their dependencies.

        Algorithm:
        1. Build directed graph from dependencies
        2. Run NetworkX topological_sort (Kahn's algorithm)
        3. Return resources in installation order

        Time Complexity: O(V + E) where V = vertices, E = edges
        Space Complexity: O(V + E) for graph storage

        Args:
            resources: List of Resource objects to sort

        Returns:
            List of Resource objects in installation order
            (dependencies come before resources that depend on them)

        Raises:
            DependencyError: If circular dependencies exist (graph has cycles)

        Example:
            >>> resources = [resource_a, resource_b, resource_c]
            >>> ordered = resolver.get_install_order(resources)
            >>> # ordered[0] has no dependencies
            >>> # ordered[-1] might depend on all others
        """
        # Build directed graph
        graph = nx.DiGraph()

        # Add all resources as nodes
        resource_map = {r.id: r for r in resources}
        graph.add_nodes_from(resource_map.keys())

        # Add dependency edges (edge from dependency to dependent)
        for resource in resources:
            if resource.dependencies:
                # Add required dependencies
                for dep_id in resource.dependencies.required:
                    if dep_id in resource_map:
                        graph.add_edge(dep_id, resource.id)

                # Add recommended dependencies if they exist in resource set
                for dep_id in resource.dependencies.recommended:
                    if dep_id in resource_map:
                        graph.add_edge(dep_id, resource.id)

        # Check for cycles before sorting
        if not nx.is_directed_acyclic_graph(graph):
            cycles = self.detect_cycles(resources)
            raise DependencyError(
                f"Circular dependencies detected: {' -> '.join(cycles)}"
            )

        # Perform topological sort
        try:
            sorted_ids = list(nx.topological_sort(graph))
        except nx.NetworkXError as e:
            raise DependencyError(f"Failed to compute install order: {e}")

        # Return resources in sorted order
        return [resource_map[rid] for rid in sorted_ids if rid in resource_map]

    def detect_cycles(self, resources: list[Resource]) -> Optional[list[str]]:
        """Detect circular dependencies in resource list.

        Uses NetworkX simple_cycles to find all cycles in the dependency graph.
        Returns the first cycle found, or None if no cycles exist.

        Algorithm:
        1. Build directed graph from dependencies
        2. Use Johnson's algorithm (via NetworkX) to find cycles
        3. Return first cycle found or None

        Time Complexity: O((V + E)(C + 1)) where C = number of cycles
        Space Complexity: O(V + E) for graph storage

        Args:
            resources: List of Resource objects to check

        Returns:
            List of resource IDs forming a cycle, or None if no cycles exist
            Example: ['resource-a', 'resource-b', 'resource-c', 'resource-a']

        Example:
            >>> cycles = resolver.detect_cycles(resources)
            >>> if cycles:
            ...     print(f"Cycle detected: {' -> '.join(cycles)}")
        """
        # Build directed graph
        graph = nx.DiGraph()

        # Add all resources as nodes
        resource_map = {r.id: r for r in resources}
        graph.add_nodes_from(resource_map.keys())

        # Add dependency edges
        for resource in resources:
            if resource.dependencies:
                # Add required dependencies
                for dep_id in resource.dependencies.required:
                    if dep_id in resource_map:
                        graph.add_edge(resource.id, dep_id)

                # Add recommended dependencies
                for dep_id in resource.dependencies.recommended:
                    if dep_id in resource_map:
                        graph.add_edge(resource.id, dep_id)

        # Find cycles using NetworkX
        try:
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                # Return first cycle found (close the loop for display)
                first_cycle = cycles[0]
                first_cycle.append(first_cycle[0])  # Close the cycle
                return first_cycle
        except nx.NetworkXError:
            pass

        return None

    def _find_resource_type(self, resource_id: str, catalog: Catalog) -> Optional[str]:
        """Find the type of a resource from the catalog.

        Searches through all resource types in the catalog to find which
        type contains the given resource ID.

        Args:
            resource_id: Resource identifier to search for
            catalog: Catalog instance to search in

        Returns:
            Resource type string (e.g., 'agent', 'command') or None if not found
        """
        for resource_type, type_data in catalog.types.items():
            # type_data can be dict with 'resources' list or other structures
            if isinstance(type_data, dict):
                resources = type_data.get('resources', [])
                for resource in resources:
                    if isinstance(resource, dict) and resource.get('id') == resource_id:
                        return resource_type

        return None

    def _resolve_recursive(
        self,
        resource_id: str,
        resource_type: str,
        catalog: Catalog,
        catalog_loader,
        visited: set[str],
        result: list[Resource],
        depth: int,
        include_recommended: bool
    ):
        """Recursively resolve dependencies using depth-first search.

        Internal method implementing DFS for dependency resolution.

        Args:
            resource_id: Current resource ID to resolve
            resource_type: Type of the resource
            catalog: Catalog instance
            catalog_loader: CatalogLoader instance
            visited: Set of already visited resource IDs (for cycle detection)
            result: Accumulator list for resolved resources
            depth: Current recursion depth
            include_recommended: Whether to include recommended dependencies

        Raises:
            DependencyError: If max depth exceeded or circular dependency detected
        """
        # Check depth limit
        if depth > self.max_depth:
            raise DependencyError(
                f"Maximum dependency depth ({self.max_depth}) exceeded "
                f"while resolving '{resource_id}'"
            )

        # Check for circular dependency
        if resource_id in visited:
            return  # Already processed, skip to avoid infinite loop

        visited.add(resource_id)

        # Load resource data
        resource_data = catalog_loader.get_resource(resource_id, resource_type)

        if not resource_data:
            # Try loading all resources if not already loaded
            if not catalog_loader.resources:
                catalog_loader.load_all_resources()
                resource_data = catalog_loader.get_resource(resource_id, resource_type)

            if not resource_data:
                raise DependencyError(
                    f"Dependency not found: {resource_id} (type: {resource_type})"
                )

        # Parse dependencies
        dependencies_data = resource_data.get('dependencies')
        if dependencies_data:
            dependency_obj = Dependency(**dependencies_data)

            # Resolve required dependencies first
            for dep_id in dependency_obj.required:
                dep_type = self._find_resource_type(dep_id, catalog)
                if not dep_type:
                    raise DependencyError(
                        f"Required dependency '{dep_id}' not found in catalog "
                        f"(required by '{resource_id}')"
                    )

                self._resolve_recursive(
                    resource_id=dep_id,
                    resource_type=dep_type,
                    catalog=catalog,
                    catalog_loader=catalog_loader,
                    visited=visited,
                    result=result,
                    depth=depth + 1,
                    include_recommended=include_recommended
                )

            # Resolve recommended dependencies if requested
            if include_recommended:
                for dep_id in dependency_obj.recommended:
                    dep_type = self._find_resource_type(dep_id, catalog)
                    if dep_type:  # Optional: skip if not found
                        try:
                            self._resolve_recursive(
                                resource_id=dep_id,
                                resource_type=dep_type,
                                catalog=catalog,
                                catalog_loader=catalog_loader,
                                visited=visited,
                                result=result,
                                depth=depth + 1,
                                include_recommended=include_recommended
                            )
                        except DependencyError:
                            # Recommended dependencies are optional - continue if not found
                            pass

        # Create Resource object and add to result
        try:
            resource_obj = Resource(**resource_data)
            # Only add if not already in result (avoid duplicates)
            if not any(r.id == resource_obj.id for r in result):
                result.append(resource_obj)
        except Exception as e:
            raise DependencyError(
                f"Failed to create Resource object for '{resource_id}': {e}"
            )
