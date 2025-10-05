"""Shared fixtures for TUI tests."""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock
import pytest
from textual.pilot import Pilot


@pytest.fixture
def mock_catalog_loader():
    """Mock CatalogLoader for TUI tests."""
    loader = Mock()
    loader.load_index = AsyncMock(return_value={
        "total": 331,
        "types": {
            "agent": {"count": 181, "description": "AI specialists"},
            "command": {"count": 18, "description": "Slash commands"},
            "hook": {"count": 64, "description": "Lifecycle hooks"},
            "template": {"count": 16, "description": "Project templates"},
            "mcp": {"count": 52, "description": "MCP integrations"},
        },
    })
    loader.load_resources = AsyncMock(return_value=[
        {
            "id": "architect",
            "type": "agent",
            "name": "Architect",
            "description": "System architecture design specialist",
            "summary": "Designs scalable system architectures",
            "version": "v1.0.0",
            "author": "Test Author",
            "file_type": ".md",
            "install_path": "~/.claude/agents/architect.md",
        },
        {
            "id": "security-reviewer",
            "type": "agent",
            "name": "Security Reviewer",
            "description": "Security audit specialist",
            "summary": "Reviews code for security vulnerabilities",
            "version": "v1.0.0",
            "author": "Test Author",
            "file_type": ".md",
            "install_path": "~/.claude/agents/security-reviewer.md",
        },
    ])
    return loader


@pytest.fixture
def mock_search_engine():
    """Mock SearchEngine for TUI tests."""
    engine = Mock()
    engine.search = Mock(return_value=[
        {
            "id": "architect",
            "type": "agent",
            "name": "Architect",
            "description": "System architecture design specialist",
            "summary": "Designs scalable system architectures",
            "version": "v1.0.0",
            "score": 95,
        },
    ])
    engine.search_smart = Mock(return_value=[
        {
            "id": "architect",
            "type": "agent",
            "name": "Architect",
            "description": "System architecture design specialist",
            "summary": "Designs scalable system architectures",
            "version": "v1.0.0",
            "score": 95,
        },
    ])
    return engine


@pytest.fixture
def mock_dependency_resolver():
    """Mock DependencyResolver for TUI tests."""
    resolver = Mock()
    resolver.resolve = Mock(return_value={
        "root": "architect",
        "required": ["security-reviewer", "code-archaeologist"],
        "recommended": ["test-generator"],
        "install_order": ["security-reviewer", "code-archaeologist", "architect"],
        "total_size": 1024 * 15,  # 15 KB
    })
    resolver.check_circular = Mock(return_value=None)
    return resolver


@pytest.fixture
def sample_resource():
    """Sample resource for testing."""
    return {
        "id": "architect",
        "type": "agent",
        "name": "Architect",
        "description": "System architecture design specialist with focus on scalability",
        "summary": "Designs scalable system architectures",
        "version": "v1.0.0",
        "author": "Test Author",
        "file_type": ".md",
        "source": {
            "repo": "test-repo",
            "path": "agents/architect.md",
            "url": "https://raw.githubusercontent.com/test/repo/main/agents/architect.md",
        },
        "install_path": "~/.claude/agents/architect.md",
        "metadata": {
            "tools": ["Read", "Write", "Edit"],
            "model": "opus",
            "tags": ["architecture", "design", "system"],
        },
        "dependencies": {
            "required": ["security-reviewer"],
            "recommended": ["test-generator"],
        },
    }


@pytest.fixture
def sample_resources_list():
    """List of sample resources for browser testing."""
    return [
        {
            "id": "architect",
            "type": "agent",
            "name": "Architect",
            "description": "System architecture design specialist",
            "version": "v1.0.0",
        },
        {
            "id": "security-reviewer",
            "type": "agent",
            "name": "Security Reviewer",
            "description": "Security audit specialist",
            "version": "v1.0.0",
        },
        {
            "id": "test-generator",
            "type": "agent",
            "name": "Test Generator",
            "description": "Automated test generation",
            "version": "v1.0.0",
        },
        {
            "id": "git-commit",
            "type": "command",
            "name": "Git Commit",
            "description": "Smart git commit helper",
            "version": "v1.0.0",
        },
        {
            "id": "pre-commit",
            "type": "hook",
            "name": "Pre-Commit",
            "description": "Pre-commit validation hook",
            "version": "v1.0.0",
        },
    ]


@pytest.fixture
def dependency_tree_data():
    """Sample dependency tree data."""
    return {
        "root": "architect",
        "required": ["security-reviewer", "code-archaeologist"],
        "recommended": ["test-generator"],
        "install_order": ["code-archaeologist", "security-reviewer", "architect"],
        "total_size": 1024 * 20,  # 20 KB
        "tree": {
            "architect": {
                "required": ["security-reviewer"],
                "recommended": ["test-generator"],
            },
            "security-reviewer": {
                "required": ["code-archaeologist"],
                "recommended": [],
            },
            "code-archaeologist": {
                "required": [],
                "recommended": [],
            },
            "test-generator": {
                "required": [],
                "recommended": [],
            },
        },
    }


@pytest.fixture
def mock_installer():
    """Mock Installer for TUI tests."""
    installer = AsyncMock()
    installer.install = AsyncMock(return_value={
        "success": True,
        "installed": ["code-archaeologist", "security-reviewer", "architect"],
        "failed": [],
        "skipped": [],
    })
    installer.download_resource = AsyncMock(return_value=b"# Test Resource\nMock content")
    return installer


@pytest.fixture
async def pilot_app(app):
    """Create Pilot for async app testing.

    This fixture should be used with apps that need pilot control.
    """
    async with app.run_test() as pilot:
        yield pilot
