"""Shared pytest fixtures for Claude Resource Manager tests."""

# Make SecurityError available globally for tests via builtins
# This allows tests to use SecurityError without explicit import
import builtins
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock

import pytest

from claude_resource_manager.utils.security import SecurityError as _SecurityError

builtins.SecurityError = _SecurityError


@pytest.fixture
def sample_resource_data() -> Dict[str, Any]:
    """Sample resource data for testing."""
    return {
        "id": "architect",
        "type": "agent",
        "name": "architect",
        "description": "System architecture design specialist",
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
        },
    }


@pytest.fixture
def sample_dependency_data() -> Dict[str, Any]:
    """Sample dependency data for testing."""
    return {
        "required": ["security-reviewer", "code-archaeologist"],
        "recommended": ["test-generator"],
    }


@pytest.fixture
def sample_resource_with_deps(sample_resource_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sample resource with dependencies."""
    data = sample_resource_data.copy()
    data["dependencies"] = {
        "required": ["security-reviewer"],
        "recommended": ["test-generator"],
    }
    return data


@pytest.fixture
def sample_catalog_index() -> Dict[str, Any]:
    """Sample catalog index data."""
    return {
        "total": 331,
        "types": {
            "agent": {"count": 181, "description": "AI specialists"},
            "command": {"count": 18, "description": "Slash commands"},
            "hook": {"count": 64, "description": "Lifecycle hooks"},
            "template": {"count": 16, "description": "Project templates"},
            "mcp": {"count": 52, "description": "MCP integrations"},
        },
    }


@pytest.fixture
def mock_catalog_331_resources() -> List[Dict[str, Any]]:
    """Mock catalog with 331 resources for performance testing."""
    resources = []

    # Create 181 agents
    for i in range(181):
        resources.append(
            {
                "id": f"agent-{i:03d}",
                "type": "agent",
                "name": f"Agent {i}",
                "description": f"Test agent {i}",
                "version": "v1.0.0",
            }
        )

    # Create 52 MCPs
    for i in range(52):
        resources.append(
            {
                "id": f"mcp-{i:03d}",
                "type": "mcp",
                "name": f"MCP {i}",
                "description": f"Test MCP {i}",
                "version": "v1.0.0",
            }
        )

    # Create 64 hooks
    for i in range(64):
        resources.append(
            {
                "id": f"hook-{i:03d}",
                "type": "hook",
                "name": f"Hook {i}",
                "description": f"Test hook {i}",
                "version": "v1.0.0",
            }
        )

    # Create 18 commands
    for i in range(18):
        resources.append(
            {
                "id": f"command-{i:03d}",
                "type": "command",
                "name": f"Command {i}",
                "description": f"Test command {i}",
                "version": "v1.0.0",
            }
        )

    # Create 16 templates
    for i in range(16):
        resources.append(
            {
                "id": f"template-{i:03d}",
                "type": "template",
                "name": f"Template {i}",
                "description": f"Test template {i}",
                "version": "v1.0.0",
            }
        )

    return resources


@pytest.fixture
def temp_catalog_dir(tmp_path: Path) -> Path:
    """Create temporary catalog directory structure."""
    catalog_dir = tmp_path / "catalog"
    catalog_dir.mkdir()

    # Create type directories (both singular and plural for compatibility)
    for resource_type in [
        "agents",
        "commands",
        "hooks",
        "templates",
        "mcps",
        "agent",
        "command",
        "hook",
        "template",
        "mcp",
    ]:
        (catalog_dir / resource_type).mkdir()

    return catalog_dir


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Mock httpx AsyncClient for testing downloads."""
    # Create response mock with proper attributes
    response = Mock()
    response.status_code = 200
    response.content = b"# Test Resource\nMock content"
    response.raise_for_status = Mock()

    # Create client mock that works with async context manager
    client = AsyncMock()
    client.get = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


@pytest.fixture
def temp_install_dir(tmp_path: Path) -> Path:
    """Create temporary installation directory (~/.claude)."""
    install_dir = tmp_path / ".claude"
    install_dir.mkdir()

    for resource_type in ["agents", "commands", "hooks", "templates", "mcps"]:
        (install_dir / resource_type).mkdir()

    return install_dir


@pytest.fixture
def yaml_bomb_content() -> str:
    """YAML bomb for security testing - deeply nested structure."""
    return """
a: &a ["lol", "lol", "lol", "lol", "lol", "lol", "lol", "lol", "lol"]
b: &b [*a, *a, *a, *a, *a, *a, *a, *a, *a]
c: &c [*b, *b, *b, *b, *b, *b, *b, *b, *b]
d: &d [*c, *c, *c, *c, *c, *c, *c, *c, *c]
e: &e [*d, *d, *d, *d, *d, *d, *d, *d, *d]
f: &f [*e, *e, *e, *e, *e, *e, *e, *e, *e]
"""


@pytest.fixture
def path_traversal_attempts() -> List[str]:
    """Common path traversal attack vectors."""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "../../.ssh/id_rsa",
        "./../../../root/.bashrc",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
        "..%252f..%252f..%252fetc%252fpasswd",  # Double URL encoded
        "\x00/etc/passwd",  # Null byte injection
    ]


@pytest.fixture
def unsafe_urls() -> List[str]:
    """Unsafe URLs for security testing."""
    return [
        "http://evil.com/malware.sh",  # HTTP instead of HTTPS
        "https://evil.com/malware.sh",  # Untrusted domain
        "file:///etc/passwd",  # File scheme
        "ftp://ftp.evil.com/",  # FTP scheme
        "http://127.0.0.1:8000/",  # Localhost
        "https://192.168.1.1/",  # Private IP
        "javascript:alert('XSS')",  # JavaScript scheme
    ]


@pytest.fixture
def safe_github_urls() -> List[str]:
    """Safe GitHub raw URLs for testing."""
    return [
        "https://raw.githubusercontent.com/org/repo/main/file.md",
        "https://raw.githubusercontent.com/user/project/master/resource.yaml",
        "https://raw.githubusercontent.com/test/test/v1.0.0/agent.md",
    ]


# TUI-specific fixtures (with aliases for backward compatibility)
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
        "total_size": 1024 * 15,
    })
    resolver.check_circular = Mock(return_value=None)
    return resolver


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
            "description": "Generates comprehensive test suites",
            "version": "v1.0.0",
        },
        {
            "id": "git-commit",
            "type": "command",
            "name": "Git Commit",
            "description": "Creates semantic git commits",
            "version": "v1.0.0",
        },
    ]


@pytest.fixture
def sample_resource():
    """Single sample resource with full metadata for testing."""
    return {
        "id": "architect",
        "type": "agent",
        "name": "Architect",
        "description": "System architecture design specialist",
        "version": "v1.0.0",
        "metadata": {
            "tools": ["Read", "Write", "Edit"],
            "model": "opus",
        },
        "dependencies": {
            "required": ["security-reviewer"],
            "recommended": ["test-generator"],
        },
    }


@pytest.fixture
def dependency_tree_data():
    """Sample dependency tree data."""
    return {
        "root": "architect",
        "required": ["security-reviewer", "code-archaeologist"],
        "recommended": ["test-generator"],
        "install_order": ["code-archaeologist", "security-reviewer", "architect"],
        "total_size": 1024 * 20,
        "tree": {
            "architect": {
                "required": ["security-reviewer"],
                "recommended": ["test-generator"],
            },
            "security-reviewer": {
                "required": ["code-archaeologist"],
                "recommended": [],
            },
        },
    }
