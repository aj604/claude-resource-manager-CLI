"""Pydantic models for Claude resources.

This module defines the core data models for Claude resources including
Source, Dependency, and Resource models with comprehensive validation.
"""

import re
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Source(BaseModel):
    """Source location information for a resource.

    Attributes:
        repo: Repository name or identifier
        path: Path to the resource within the repository
        url: HTTPS URL to the resource (must be secure)
    """

    repo: str = Field(..., description="Repository name or identifier")
    path: str = Field(..., description="Path to resource in repository")
    url: str = Field(..., description="HTTPS URL to the resource")

    @field_validator("url")
    @classmethod
    def validate_https_url(cls, v: str) -> str:
        """Validate that URL uses HTTPS protocol.

        Args:
            v: URL string to validate

        Returns:
            Validated URL string

        Raises:
            ValueError: If URL doesn't start with https://
        """
        if not v.startswith("https://"):
            raise ValueError("URL must use HTTPS protocol for security")
        return v


class Dependency(BaseModel):
    """Dependency information for a resource.

    Attributes:
        required: List of required dependency resource IDs
        recommended: List of recommended dependency resource IDs
    """

    required: list[str] = Field(default_factory=list, description="Required dependencies")
    recommended: list[str] = Field(default_factory=list, description="Recommended dependencies")


class Resource(BaseModel):
    """Main resource model representing a Claude resource.

    Attributes:
        id: Unique identifier (lowercase, numbers, hyphens only)
        type: Resource type (agent, command, hook, template, mcp)
        name: Display name of the resource
        description: Detailed description of the resource
        summary: Brief summary of the resource
        version: Version string (e.g., v1.0.0)
        author: Resource author (optional)
        file_type: File extension (e.g., .md)
        source: Source location information
        install_path: Installation path
        metadata: Additional metadata (flexible dict)
        dependencies: Optional dependency information
    """

    model_config = ConfigDict(extra="allow")

    id: str = Field(..., description="Unique resource identifier")
    type: str = Field(..., description="Resource type")
    name: str = Field(..., description="Resource display name")
    description: str = Field(..., description="Detailed description")
    summary: str = Field(..., description="Brief summary")
    version: str = Field(..., description="Version string")
    author: Optional[str] = Field(None, description="Resource author")
    file_type: str = Field(..., description="File extension")
    source: Source = Field(..., description="Source location")
    install_path: str = Field(..., description="Installation path")
    metadata: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )
    dependencies: Optional[Dependency] = Field(None, description="Dependency information")

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID format.

        Args:
            v: ID string to validate

        Returns:
            Validated ID string

        Raises:
            ValueError: If ID is empty or contains invalid characters
        """
        if not v:
            raise ValueError("ID cannot be empty")

        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("ID must contain only lowercase letters, numbers, and hyphens")

        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate resource type.

        Args:
            v: Type string to validate

        Returns:
            Validated type string

        Raises:
            ValueError: If type is not in allowed list
        """
        allowed_types = ["agent", "command", "hook", "template", "mcp"]
        if v not in allowed_types:
            raise ValueError(f"Type must be one of {allowed_types}")

        return v

    @field_validator("dependencies")
    @classmethod
    def validate_no_self_reference(cls, v: Optional[Dependency], info) -> Optional[Dependency]:
        """Validate that resource doesn't depend on itself.

        Args:
            v: Dependency object to validate
            info: Validation context containing other field values

        Returns:
            Validated Dependency object

        Raises:
            ValueError: If resource has self-referencing dependency
        """
        if v is None:
            return v

        resource_id = info.data.get("id")
        if resource_id:
            if resource_id in v.required:
                raise ValueError(
                    "Resource cannot have self-referencing dependency (circular dependency)"
                )
            if resource_id in v.recommended:
                raise ValueError(
                    "Resource cannot have self-referencing dependency (circular dependency)"
                )

        return v
