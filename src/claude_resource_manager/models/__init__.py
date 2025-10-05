"""Claude Resource Manager - Pydantic Models.

This package contains all Pydantic models for resource validation and catalog management.
"""

from .catalog import Catalog, Category, ResourceIndex
from .resource import Dependency, Resource, Source

__all__ = ["Resource", "Source", "Dependency", "Catalog", "ResourceIndex", "Category"]
