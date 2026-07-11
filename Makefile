# Makefile for Claude Resource Manager CLI
# Includes VHS demo generation targets and development tasks

.PHONY: help
help:
	@echo "Claude Resource Manager CLI - Make Targets"
	@echo ""
	@echo "Demo Generation:"
	@echo "  make demo-preflight  - Validate demo environment (auto-run by demo targets)"
	@echo "  make demos           - Generate all VHS demo GIFs"
	@echo "  make demo-clean      - Clean generated demo GIFs"
	@echo "  make demo-quick-start - Generate quick-start demo"
	@echo "  make demo-fuzzy-search - Generate fuzzy-search demo"
	@echo "  make demo-multi-select - Generate multi-select demo"
	@echo "  make demo-categories - Generate categories demo"
	@echo "  make demo-help-system - Generate help-system demo"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-vhs       - Run VHS integration tests"
	@echo "  make format         - Format code with black and ruff"
	@echo "  make lint           - Run linting checks"
	@echo "  make typecheck      - Run type checking with mypy"
	@echo "  make coverage       - Generate test coverage report"
	@echo "  make install        - Install package in development mode"
	@echo "  make clean          - Clean build artifacts and caches"

# ============================================================================
# VHS Demo Generation Targets
# ============================================================================

.PHONY: demo-preflight
demo-preflight:
	@echo "Validating demo environment..."
	@test -d .venv || (echo "❌ Virtual environment not found. Run: python -m venv .venv && .venv/bin/pip install -e ." && exit 1)
	@test -f .venv/bin/crm || (echo "❌ crm not installed. Run: .venv/bin/pip install -e ." && exit 1)
	@mkdir -p ~/.claude/registry/catalog
	@# Only create demo catalog if none exists (won't overwrite existing catalogs)
	@if [ ! -f ~/.claude/registry/catalog/index.yaml ]; then \
		echo "Creating demo catalog with sample resources..."; \
		printf '%s\n' \
		'catalog:' \
		'  version: "1.0.0"' \
		'  total: 15' \
		'  types:' \
		'    agent:' \
		'      count: 6' \
		'      description: "AI specialists"' \
		'    command:' \
		'      count: 3' \
		'      description: "Slash commands"' \
		'    hook:' \
		'      count: 3' \
		'      description: "Lifecycle hooks"' \
		'    template:' \
		'      count: 2' \
		'      description: "Project templates"' \
		'    mcp:' \
		'      count: 1' \
		'      description: "MCP integrations"' \
		'  resources:' \
		'    - id: "architect"' \
		'      type: "agent"' \
		'      name: "Architect"' \
		'      description: "System architecture design specialist"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "security-reviewer"' \
		'      type: "agent"' \
		'      name: "Security Reviewer"' \
		'      description: "Security vulnerability detection and remediation"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "test-generator"' \
		'      type: "agent"' \
		'      name: "Test Generator"' \
		'      description: "TDD test suite generation specialist"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "code-archaeologist"' \
		'      type: "agent"' \
		'      name: "Code Archaeologist"' \
		'      description: "Legacy code reverse-engineering specialist"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "documentation-agent"' \
		'      type: "agent"' \
		'      name: "Documentation Agent"' \
		'      description: "Technical documentation specialist"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "ux-optimizer"' \
		'      type: "agent"' \
		'      name: "UX Optimizer"' \
		'      description: "User experience optimization specialist"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "resource-manager"' \
		'      type: "command"' \
		'      name: "Resource Manager"' \
		'      description: "Manage Claude Code resources"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "epcc-commit"' \
		'      type: "command"' \
		'      name: "EPCC Commit"' \
		'      description: "Commit phase of EPCC workflow"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "epcc-explore"' \
		'      type: "command"' \
		'      name: "EPCC Explore"' \
		'      description: "Explore phase of EPCC workflow"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "pre-commit-hook"' \
		'      type: "hook"' \
		'      name: "Pre-Commit Hook"' \
		'      description: "Run tests before commit"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "post-merge-hook"' \
		'      type: "hook"' \
		'      name: "Post-Merge Hook"' \
		'      description: "Update dependencies after merge"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "prompt-submit-hook"' \
		'      type: "hook"' \
		'      name: "Prompt Submit Hook"' \
		'      description: "Validate prompts before submission"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "python-project"' \
		'      type: "template"' \
		'      name: "Python Project"' \
		'      description: "Modern Python project with pytest and black"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "typescript-library"' \
		'      type: "template"' \
		'      name: "TypeScript Library"' \
		'      description: "TypeScript library with Jest and ESLint"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		'    - id: "filesystem-mcp"' \
		'      type: "mcp"' \
		'      name: "Filesystem MCP"' \
		'      description: "Local filesystem access integration"' \
		'      version: "v1.0.0"' \
		'      author: "Claude Resources"' \
		> ~/.claude/registry/catalog/index.yaml; \
	else \
		echo "Using existing catalog at ~/.claude/registry/catalog/index.yaml"; \
	fi
	@echo "✅ Demo environment validated"

.PHONY: demos
demos: demo-preflight
	@echo "Generating VHS demos..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/quick-start.tape && echo "✅ quick-start.gif generated"; \
		vhs demo/fuzzy-search.tape && echo "✅ fuzzy-search.gif generated"; \
		vhs demo/multi-select.tape && echo "✅ multi-select.gif generated"; \
		vhs demo/categories.tape && echo "✅ categories.gif generated"; \
		vhs demo/help-system.tape && echo "✅ help-system.gif generated"; \
		echo ""; \
		echo "✅ All demos generated in demo/output/"; \
		ls -lh demo/output/*.gif 2>/dev/null || echo "Note: GIF files will be created after VHS processing"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-clean
demo-clean:
	@echo "Cleaning VHS demo output..."
	@rm -f demo/output/*.gif
	@echo "✅ Demo output cleaned"

.PHONY: demo-quick-start
demo-quick-start: demo-preflight
	@echo "Generating quick-start demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/quick-start.tape && echo "✅ quick-start.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-fuzzy-search
demo-fuzzy-search: demo-preflight
	@echo "Generating fuzzy-search demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/fuzzy-search.tape && echo "✅ fuzzy-search.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-multi-select
demo-multi-select: demo-preflight
	@echo "Generating multi-select demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/multi-select.tape && echo "✅ multi-select.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-categories
demo-categories: demo-preflight
	@echo "Generating categories demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/categories.tape && echo "✅ categories.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-help-system
demo-help-system: demo-preflight
	@echo "Generating help-system demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/help-system.tape && echo "✅ help-system.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

# ============================================================================
# Development Targets
# ============================================================================

.PHONY: test
test:
	@echo "Running all tests..."
	@.venv/bin/pytest tests/ -v

.PHONY: test-unit
test-unit:
	@echo "Running unit tests..."
	@.venv/bin/pytest tests/unit/ -v

.PHONY: test-integration
test-integration:
	@echo "Running integration tests..."
	@.venv/bin/pytest tests/integration/ -v

.PHONY: test-vhs
test-vhs:
	@echo "Running VHS integration tests..."
	@.venv/bin/pytest tests/integration/test_vhs_integration.py -v

.PHONY: format
format:
	@echo "Formatting code..."
	@.venv/bin/black src/ tests/
	@.venv/bin/ruff check --fix src/ tests/

.PHONY: lint
lint:
	@echo "Running linting checks..."
	@.venv/bin/ruff check src/ tests/
	@.venv/bin/black --check src/ tests/

.PHONY: typecheck
typecheck:
	@echo "Running type checking..."
	@.venv/bin/mypy src/

.PHONY: coverage
coverage:
	@echo "Generating coverage report..."
	@.venv/bin/pytest --cov=claude_resource_manager --cov-report=html --cov-report=term-missing

.PHONY: install
install:
	@echo "Installing package in development mode..."
	@.venv/bin/pip install -e ".[dev]"

.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	@rm -rf htmlcov/ .coverage
	@echo "✅ Clean complete"

# ============================================================================
# CI/CD Targets (for future GitHub Actions integration)
# ============================================================================

.PHONY: ci-test
ci-test: lint typecheck test
	@echo "✅ CI tests passed"

.PHONY: ci-demos
ci-demos: demos
	@echo "Checking demo file sizes..."
	@for gif in demo/output/*.gif; do \
		if [ -f "$$gif" ]; then \
			size=$$(stat -f%z "$$gif" 2>/dev/null || stat -c%s "$$gif" 2>/dev/null); \
			size_mb=$$(echo "scale=2; $$size / 1048576" | bc); \
			echo "$$gif: $${size_mb}MB"; \
			if [ "$$(echo "$$size_mb > 2" | bc)" -eq 1 ]; then \
				echo "❌ Warning: $$gif exceeds 2MB limit"; \
			fi; \
		fi; \
	done

# Default target
.DEFAULT_GOAL := help