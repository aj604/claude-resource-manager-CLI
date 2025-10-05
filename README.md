# Claude Resource Manager CLI

A high-performance Python CLI tool with interactive TUI for managing Claude resources.

## Features

- **Interactive TUI** - Rich terminal UI powered by Textual
- **Fast Search** - Sub-5ms fuzzy search across 331+ resources using RapidFuzz
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

### Browse Resources

```bash
claude-resources browse
```

### Install a Resource

```bash
claude-resources install architect
```

### Search Resources

```bash
claude-resources search "security"
```

### Show Dependencies

```bash
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

- **TDD Approach** - Test-driven development with 150+ tests
- **Pydantic Models** - Type-safe data validation
- **Async I/O** - httpx for concurrent downloads
- **Security First** - Multiple security controls for YAML, paths, and URLs

## Performance Targets

- Startup: <100ms
- Search (exact): <5ms
- Search (fuzzy): <20ms
- Memory: <50MB for 331 resources

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.
