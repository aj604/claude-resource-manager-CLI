# Contributing to Claude Resource Manager CLI

Thank you for contributing! This guide will help you get started with development.

## Table of Contents

- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [VHS Demo Generation](#vhs-demo-generation)
- [Code Quality](#code-quality)
- [Git Workflow](#git-workflow)
- [EPCC Workflow](#epcc-workflow)
- [Pull Request Guidelines](#pull-request-guidelines)

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- VHS (for demo generation, optional)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/anthropics/claude-resource-manager-CLI.git
cd claude-resource-manager-CLI

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

### Optional: direnv for Automatic Virtual Environment

Install [direnv](https://direnv.net/) to automatically activate the virtualenv:

```bash
# Install direnv (macOS)
brew install direnv

# Add to shell (~/.zshrc or ~/.bashrc)
eval "$(direnv hook zsh)"  # or bash

# Allow .envrc in this repo
direnv allow

# Virtual environment now activates automatically!
```

## Running Tests

### Quick Test Run

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/core/test_search_engine.py

# With coverage
pytest --cov=claude_resource_manager --cov-report=html
```

### Test Organization

- `tests/unit/` - Fast, isolated unit tests
- `tests/integration/` - Integration tests including VHS demos
- `tests/conftest.py` - Shared fixtures

### Running Tests in CI

Tests run automatically via GitHub Actions on every PR:

```bash
# Simulate CI environment locally
make ci-test  # Runs lint, typecheck, and tests
```

## VHS Demo Generation

VHS (Video Handshake) generates animated GIF documentation for the TUI.

### Local Demo Generation

#### Install VHS

```bash
# macOS
brew install vhs

# Linux
curl -sL https://github.com/charmbracelet/vhs/releases/download/v0.7.2/vhs_0.7.2_Linux_x86_64.tar.gz -o vhs.tar.gz
tar -xzf vhs.tar.gz
sudo mv vhs /usr/local/bin/

# Verify installation
vhs --version
```

#### Generate Demos

```bash
# Generate all demos (creates GIFs in demo/output/)
make demos

# Generate specific demo
make demo-quick-start
make demo-fuzzy-search
make demo-multi-select
make demo-categories
make demo-help-system

# Clean generated demos
make demo-clean
```

#### Demo Structure

```
demo/
├── quick-start.tape      # 30s comprehensive workflow
├── fuzzy-search.tape     # 20s fuzzy search demo
├── multi-select.tape     # 20s batch selection demo
├── categories.tape       # 20s category filtering demo
├── help-system.tape      # 20s help system demo
└── output/
    ├── quick-start.gif   # Generated GIFs (auto-committed on main)
    ├── fuzzy-search.gif
    ├── multi-select.gif
    ├── categories.gif
    └── help-system.gif
```

### CI/CD Automated Demo Generation

Demos are automatically generated via GitHub Actions when:

- TUI code changes (`src/claude_resource_manager/tui/**`)
- Tape files change (`demo/**/*.tape`)
- Manual workflow trigger

#### Workflow Features

1. **Security Scan** - Validates tape files for dangerous commands
2. **Parallel Generation** - All 5 demos generated in parallel (matrix strategy)
3. **Automatic Optimization** - GIFs >2.5MB optimized with gifsicle
4. **Validation** - Checks dimensions (1200x800), file sizes, animation frames
5. **Integration Tests** - Runs full VHS test suite
6. **Auto-Commit** - On main branch, commits GIFs back to repo
7. **PR Preview** - Comments on PRs with demo info and download links

#### Workflow Jobs

```yaml
security-scan          # Scan tape files for malicious patterns
├─ generate-demos     # Parallel generation (5 demos)
   ├─ validate-all    # Aggregate validation
      ├─ test-vhs     # Integration tests
         ├─ commit    # Commit to main (main branch only)
         └─ pr-preview # PR comment (PRs only)
```

#### Manual Workflow Trigger

```bash
# Via GitHub UI
Actions → Generate VHS Demos → Run workflow

# Via GitHub CLI
gh workflow run vhs-demos.yml
```

### Demo Quality Standards

- **Individual GIF Size:** < 2.0MB (warning at 2.5MB, optimized automatically)
- **Total Size:** < 10.0MB (all demos combined)
- **Dimensions:** 1200x800 pixels (consistent across all demos)
- **Duration:**
  - Quick Start: 25-35 seconds
  - Feature Demos: 15-25 seconds
- **Frame Rate:** Smooth animation (>1 frame required)

### Troubleshooting VHS Demos

#### Local Generation Fails

```bash
# Check VHS installation
vhs --version

# Check tape file syntax
vhs --validate demo/quick-start.tape

# Run with verbose output
vhs --debug demo/quick-start.tape

# Test CLI builds
pip install -e .
crm browse
```

#### CI Generation Fails

1. Check [GitHub Actions logs](../../actions/workflows/vhs-demos.yml)
2. Look for failed job (security-scan, generate-demos, validate-all, test-vhs)
3. Common issues:
   - **Security scan failure:** Dangerous pattern in tape file
   - **Generation timeout:** Demo takes >120 seconds
   - **File size exceeded:** GIF >2.5MB after optimization
   - **Dimension mismatch:** Not 1200x800 (check tape file `Set Width/Height`)
   - **Test failures:** VHS integration tests failing

#### File Size Issues

If GIFs exceed size limits:

```bash
# Manual optimization
gifsicle --lossy=80 -O3 demo/output/large-demo.gif -o demo/output/large-demo-opt.gif

# Reduce demo duration in tape file
# Reduce typing speed (increase TypingSpeed value)
# Remove unnecessary Sleep commands
```

### Modifying Demos

When editing `.tape` files:

1. **Test locally first:** `make demo-quick-start`
2. **Follow existing patterns:** See existing tape files for examples
3. **Maintain consistency:**
   - Width: 1200, Height: 800
   - Theme: "Dracula"
   - FontSize: 16
   - TypingSpeed: 50ms
4. **Add descriptive comments:** Explain each section
5. **Test in PR:** CI will validate and show preview

#### Tape File Syntax

```bash
# Configuration
Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 800
Set TypingSpeed 50ms
Set Theme "Dracula"

# Output path
Output demo/output/my-demo.gif

# Commands
Type "crm browse"      # Type text
Enter                  # Press Enter
Sleep 1s               # Wait 1 second
Space                  # Press Space
Escape                 # Press Escape
Ctrl+U                 # Press Ctrl+U
Tab                    # Press Tab
```

See [VHS documentation](https://github.com/charmbracelet/vhs) for full syntax reference.

## Code Quality

### Formatting

```bash
# Format code with black
black src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Run both
make format
```

### Linting

```bash
# Check linting
ruff check src/ tests/

# Check formatting
black --check src/ tests/

# Run both
make lint
```

### Type Checking

```bash
# Run mypy type checker
mypy src/

# Or via make
make typecheck
```

### Security Scanning

```bash
# Scan for security issues
bandit -r src/claude_resource_manager/

# Check dependency vulnerabilities
safety check
```

### All Quality Checks

```bash
# Run everything (lint, typecheck, test)
make ci-test
```

## Git Workflow

### Branch Protection

**⚠️ CRITICAL: Never commit directly to main!**

- All changes must go through pull requests
- Feature branches: `{user}/{feature-description}`
- Main branch requires PR review

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: Add fuzzy search to TUI
fix: Correct category filter logic
docs: Update VHS demo documentation
chore: Update dependencies
test: Add multi-select integration tests
refactor: Extract search logic to separate module
perf: Optimize category tree building
```

### Workflow Steps

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b {user}/{feature-name}

# 2. Make changes and commit
git add .
git commit -m "feat: Add new feature"

# 3. Push to remote
git push -u origin {user}/{feature-name}

# 4. Create pull request
gh pr create --title "Add new feature" --body "Description..."

# 5. Wait for review and CI checks
# 6. Merge via GitHub UI (squash or merge commit)
```

## EPCC Workflow

This project follows the **Explore-Plan-Code-Commit (EPCC)** workflow.

### Quick Reference

```bash
# 1. Explore codebase
/epcc-explore "search engine architecture" --deep

# 2. Plan implementation
/epcc-plan "Add advanced filtering"

# 3. Implement with TDD
/epcc-code --tdd "Implement filter logic"

# 4. Commit changes
/epcc-commit "feat: Add advanced filtering"
```

### EPCC Documentation

- `docs/epcc/` - Templates and guides
- `EPCC_*.md` files - Generated during workflow
- See main [README.md](README.md#epcc-workflow) for details

### Pre-Commit Hook

Installed automatically via `.git/hooks/pre-commit`:

- Validates conventional commit messages
- Optionally enforces EPCC workflow (`ENFORCE_EPCC=1`)
- Optionally runs tests (`RUN_TESTS=1`)
- Bypass with `EPCC_BYPASS=1` (use sparingly)

## Pull Request Guidelines

### Before Creating PR

- [ ] All tests pass locally (`pytest`)
- [ ] Code formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Documentation updated (if needed)
- [ ] VHS demos regenerated (if TUI changes)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] VHS demos regenerated (if TUI changed)
- [ ] Conventional commit messages
- [ ] No breaking changes (or documented)
```

### PR Review Process

1. **Automated Checks:**
   - GitHub Actions CI/CD
   - EPCC workflow validation
   - VHS demo generation (if applicable)
   - Security scans

2. **Code Review:**
   - At least one approving review required
   - Address review comments
   - Update PR as needed

3. **Merge:**
   - Squash and merge (default)
   - Delete branch after merge

### After PR Merged

- VHS demos auto-committed to main (if TUI changed)
- Documentation deployed automatically
- Package version may be bumped (automated)

## Getting Help

- **Issues:** [GitHub Issues](../../issues)
- **Discussions:** [GitHub Discussions](../../discussions)
- **Documentation:** See `docs/` directory
- **EPCC Workflow:** See `docs/epcc/`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
