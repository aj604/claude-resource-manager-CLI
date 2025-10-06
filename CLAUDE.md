# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Python Project Configuration

**Virtual Environment**: `.venv/` (already created)
- **Always use**: `.venv/bin/python3` and `.venv/bin/pytest` for Python commands
- **For bash commands**: Prefix with `source .venv/bin/activate &&` or use explicit paths
- **Example**: `source .venv/bin/activate && pytest tests/unit/`
- **Alternative**: `.venv/bin/pytest tests/unit/` (explicit path)

**Package Manager**: pip with `pyproject.toml`
- Install dependencies: `pip install -e ".[dev]"`
- All configuration in `pyproject.toml`
- No separate `requirements.txt` needed (legacy files may exist)

## Running Commands

### Correct Patterns:
```bash
# Pattern 1: Activate then run (preferred for multiple commands)
source .venv/bin/activate && pytest tests/unit/ && ruff check src/

# Pattern 2: Explicit virtualenv path (single command)
.venv/bin/pytest tests/unit/

# Pattern 3: Use python -m (ensures correct interpreter)
.venv/bin/python -m pytest tests/unit/
```

### Incorrect Patterns:
```bash
# ❌ Don't run pytest without virtualenv
pytest  # Error: command not found

# ❌ Don't use system Python
python3 -m pytest  # Uses wrong Python, missing dependencies
```

## Development Standards

### Code Quality
- **Type hints**: Required on all functions (mypy strict mode enabled)
- **Docstrings**: Google-style for all public APIs
- **Line length**: 100 characters (black + ruff)
- **Import sorting**: Handled by ruff

### Testing
- **Framework**: pytest with pytest-asyncio
- **Coverage**: Target >80% overall, >90% core modules
- **Run tests**: `.venv/bin/pytest` or `source .venv/bin/activate && pytest`
- **Coverage report**: `pytest --cov=claude_resource_manager --cov-report=html`

### Security
- **YAML**: Always use `yaml.safe_load()`, never `yaml.load()`
- **Paths**: Validate with `Path.resolve()` and `is_relative_to()`
- **URLs**: HTTPS only, validate domains
- **Input**: Pydantic models for all external data

## Project Structure

```
src/claude_resource_manager/
├── models/          # Pydantic data models
├── core/            # Business logic (CatalogLoader, SearchEngine, etc.)
├── utils/           # Utilities (security.py)
├── cli.py           # Click CLI interface
└── tui/             # Textual TUI screens
    ├── app.py       # Main TUI application
    └── screens/     # TUI screen components

tests/
├── unit/            # Unit tests mirroring src/ structure
└── conftest.py      # Shared pytest fixtures
```

## Common Tasks

### Run Tests
```bash
# All tests
source .venv/bin/activate && pytest

# Specific module
.venv/bin/pytest tests/unit/core/test_search_engine.py

# With coverage
.venv/bin/pytest --cov=claude_resource_manager --cov-report=term-missing
```

### VHS Demo Generation
```bash
# Install VHS (one-time setup)
brew install vhs  # macOS
# OR
curl -sL https://github.com/charmbracelet/vhs/releases/latest/download/vhs_Linux_x86_64.tar.gz | tar -xz
sudo mv vhs /usr/local/bin/  # Linux

# Generate all demos
make demos

# Generate specific demo
make demo-quick-start
make demo-fuzzy-search
make demo-multi-select
make demo-categories
make demo-help-system

# Clean demo output
make demo-clean

# Validate demos
.venv/bin/pytest tests/integration/test_vhs_integration.py -v
```

### Code Quality
```bash
# Format code
.venv/bin/black src/ tests/

# Lint code
.venv/bin/ruff check src/ tests/

# Type check
.venv/bin/mypy src/
```

### Security Scan
```bash
.venv/bin/bandit -r src/claude_resource_manager/
.venv/bin/safety check
```

## Performance Targets

- **Startup**: <100ms
- **Search (exact)**: <5ms
- **Search (fuzzy)**: <20ms
- **CatalogLoader**: <200ms for 331 resources
- **Memory**: <100MB with full catalog loaded

## Git Workflow

**⚠️ CRITICAL: Never commit directly to main!**
- **All work must be on feature branches** - Use `{user}/{feature-description}` format
- **All changes must go through PR** - Never push directly to main, always create a pull request
- **Branch protection**: Main branch requires PR review before merge

### Workflow Steps:
1. Create feature branch from main: `git checkout -b {user}/{feature-name}`
2. Make changes and commit to feature branch
3. Push feature branch: `git push -u origin {user}/{feature-name}`
4. Create PR using `gh pr create`
5. Wait for review/approval before merging

### Standards:
- **Commit messages**: Conventional commits format (feat:, fix:, chore:, etc.)
- **Pre-commit**: Run tests before committing (`pytest`)
- **No secrets**: Never commit `.env`, credentials, API keys

## Documentation

- **README.md**: User-facing installation and usage
- **EPCC_*.md**: Development process documentation (EPCC workflow)
- **Docstrings**: All public functions, classes, and modules
- **Type hints**: Function signatures document parameter types
- **VHS Demos**: Animated GIF demonstrations (see `demo/` and `docs/DEMOS.md`)

## VHS Demo Workflow

When updating TUI components:

1. **Make TUI changes** to the component
2. **Run local demo generation**: `make demos`
3. **Review GIFs** in `demo/output/` directory
4. **Commit changes** (CI will regenerate on merge)
5. **Demos auto-update** in README via CI/CD

### Demo Update Checklist

- [ ] Update relevant .tape file if workflow changes
- [ ] Generate demos locally: `make demos`
- [ ] Verify GIF file sizes (< 2MB each)
- [ ] Check animations are smooth and clear
- [ ] Commit .tape changes (GIFs auto-generated by CI)
- [ ] Update documentation if demo content changes

## Notes for AI Assistants

When executing commands in this repository:
1. ✅ **Always** prefix Python commands with `.venv/bin/` or `source .venv/bin/activate &&`
2. ✅ Check `pyproject.toml` for dependencies and configuration
3. ✅ Use TDD approach - tests should exist or be written first
4. ✅ Follow existing patterns in similar modules
5. ✅ Run tests after changes to verify nothing broke

Remember: This is a **Python project with a virtualenv**. The system Python lacks the dependencies!

## Parallel Subagent Workflow (Phase 2+)

**IMPORTANT**: For multi-component features, read `LESSONS_LEARNED_PHASE2.md` first!

### Efficient Agent Launch Pattern:
1. **Map dependencies** - Identify parallel vs sequential work
2. **Test-generators** (parallel) - Write behavior-focused tests, not implementation-prescriptive
3. **Implementation waves** - Core features → Integration → Polish
4. **Reviews at 70%** - Launch security/UX/docs when architecture clear, not at 100%

### Key Lessons:
- Test **behaviors** not implementation details (allows better UX without test rewrites)
- Visual state feedback is **P0** not polish (checkboxes, progress indicators)
- Documentation agent can run at 70% implementation (saves time)
- Agent handoffs need structured output (summary + next steps)

**See**: `LESSONS_LEARNED_PHASE2.md` for full details and time-saving patterns.
