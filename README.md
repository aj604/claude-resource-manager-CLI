# Claude Resource Manager CLI

A high-performance Python CLI tool with interactive TUI for managing Claude resources.

## Features

### Phase 2 Enhancements (NEW!)

- **Intelligent Fuzzy Search** - Typo-tolerant searching with RapidFuzz (0.29ms, 77x faster than target)
- **Smart Categorization** - Automatic hierarchical categorization of 331+ resources (0.77ms)
- **Multi-Select & Batch Operations** - Select multiple resources, batch install with dependency resolution
- **Context-Sensitive Help** - Press '?' for comprehensive keyboard shortcuts
- **Advanced Sorting** - Sort by name, type, or date with ascending/descending order
- **Exceptional Performance** - 8.4x faster startup (11.6ms), sub-millisecond search (0.32ms)

### Core Features (Phase 1)

- **Interactive TUI** - Rich terminal UI powered by Textual
- **Fast Search** - Sub-millisecond prefix search across 331+ resources
- **Dependency Resolution** - Automatic dependency management with NetworkX
- **Secure** - HTTPS-only downloads, path validation, YAML safe-loading
- **Cross-platform** - Works on macOS, Linux, and Windows

## Installation

### From PyPI

```bash
pip install claude-resources
```

### From Source

```bash
git clone https://github.com/anthropics/claude_resource_manager.git
cd claude_resource_manager-CLI
pip install -e .
```

## Usage

### Quick Start

```bash
# Browse resources with interactive TUI
claude-resources browse

# In the browser:
#   / - Search (with typo tolerance!)
#   ? - Show help (keyboard shortcuts)
#   Space - Select resource
#   a - Select all visible
#   i - Install selected resources
```

### Phase 2 Features

#### Fuzzy Search with Typo Tolerance

```bash
# In the TUI browser, type "/" then:
architet        # Finds "architect" despite typo
mcp-dev-tam     # Finds "mcp-dev-team"
scurity         # Finds "security-reviewer"
```

#### Multi-Select and Batch Install

```bash
# In the browser:
1. Press Space on multiple resources (shows [x])
2. Press 'i' to install all selected
3. Watch batch progress with dependency resolution
```

#### Category Filtering

```bash
# Click category buttons to filter:
All (331)     # Show all resources
MCP (52)      # Show only MCP servers
Agent (181)   # Show only agents
Hook (64)     # Show only hooks
```

#### Context-Sensitive Help

```bash
# Press '?' anywhere in the TUI
# Shows all keyboard shortcuts organized by category
```

### CLI Commands

```bash
# Install a resource
claude-resources install architect

# Search resources
claude-resources search "security"

# Show dependencies
claude-resources deps architect
```

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (development mode)
pip install -e ".[dev]"
```

**💡 Tip: Use direnv for automatic activation**

Install [direnv](https://direnv.net/) to automatically activate the virtualenv when entering the project directory:

```bash
# Install direnv (macOS)
brew install direnv

# Add to your shell (~/.zshrc or ~/.bashrc)
eval "$(direnv hook zsh)"  # or bash

# Allow the .envrc file (already created in this repo)
direnv allow

# Now the virtualenv activates automatically when you cd into this directory!
```

### Run Tests

```bash
# Virtualenv must be activated (or use direnv)
pytest

# Or run with explicit Python path
.venv/bin/pytest
```

### Run with Coverage

```bash
pytest --cov=claude_resource_manager --cov-report=html
```

### Run Security Scan

```bash
bandit -r src/claude_resource_manager/
safety check
```

## Architecture

- **TDD Approach** - Test-driven development with 457+ tests (92% coverage)
- **Pydantic Models** - Type-safe data validation
- **Async I/O** - httpx for concurrent downloads
- **Security First** - Multiple security controls for YAML, paths, and URLs
- **Performance Optimized** - Trie-based search, LRU caching, lazy loading

## Performance (Phase 2)

All targets exceeded:

| Metric | Target | Actual | Improvement |
|--------|--------|--------|-------------|
| Startup | <100ms | 11.6ms | **8.4x faster** |
| Search (Exact) | <5ms | 0.32ms | **15.6x faster** |
| Search (Fuzzy) | <20ms | 0.29ms | **77x faster** |
| Memory | <50MB | 8.5MB | **5.9x better** |
| Category Tree | <50ms | 0.77ms | **65x faster** |

See [Performance Benchmarks](docs/PERFORMANCE_BENCHMARKS.md) for detailed metrics.

## License

MIT

## EPCC Workflow

This project follows the **Explore-Plan-Code-Commit (EPCC)** workflow for systematic development:

### Quick Start

1. **🔍 EXPLORE** - Understand the codebase first
   ```bash
   /epcc-explore "authentication system" --deep
   ```
   Output: `EPCC_EXPLORE.md`

2. **📋 PLAN** - Design your approach
   ```bash
   /epcc-plan "JWT authentication implementation"
   ```
   Output: `EPCC_PLAN.md`

3. **💻 CODE** - Implement with TDD
   ```bash
   /epcc-code --tdd "implement user registration"
   ```
   Output: `EPCC_CODE.md`

4. **✅ COMMIT** - Finalize and version
   ```bash
   /epcc-commit "feat: Add JWT authentication"
   ```
   Output: `EPCC_COMMIT.md`

### EPCC Features

- **Git Pre-Commit Hook** - Validates conventional commits and optionally enforces EPCC workflow
- **GitHub Actions** - CI/CD validation of EPCC documentation and code quality
- **Documentation Templates** - See `docs/epcc/` for templates

### Configuration

Enable strict EPCC enforcement:
```bash
# Require exploration and planning before commits
export ENFORCE_EPCC=1

# Run tests before commits
export RUN_TESTS=1

# Bypass EPCC validation (use sparingly)
export EPCC_BYPASS=1
```

See [docs/epcc/](docs/epcc/) for detailed workflow documentation and templates.

## Documentation

### User Documentation

- **[Phase 2 Features Guide](docs/PHASE_2_FEATURES.md)** - Comprehensive guide to all Phase 2 features
- **[Migration Guide](docs/MIGRATION_PHASE1_TO_PHASE2.md)** - Upgrade from Phase 1 to Phase 2 (zero breaking changes!)
- **[Configuration Reference](docs/CONFIGURATION.md)** - Complete configuration options

### Developer Documentation

- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation for Phase 2
- **[Architecture](docs/ARCHITECTURE_PHASE2.md)** - Technical design and decisions
- **[Performance Benchmarks](docs/PERFORMANCE_BENCHMARKS.md)** - Detailed performance metrics
- **[Testing Guide](docs/TESTING_PHASE2.md)** - Test suite documentation (457 tests, 92% coverage)

### EPCC Workflow

- **[EPCC Documentation](docs/epcc/)** - Explore-Plan-Code-Commit workflow templates

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.
