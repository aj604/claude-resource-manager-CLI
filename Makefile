# Makefile for Claude Resource Manager CLI
# Includes VHS demo generation targets and development tasks

.PHONY: help
help:
	@echo "Claude Resource Manager CLI - Make Targets"
	@echo ""
	@echo "Demo Generation:"
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

.PHONY: demos
demos:
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
demo-quick-start:
	@echo "Generating quick-start demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/quick-start.tape && echo "✅ quick-start.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-fuzzy-search
demo-fuzzy-search:
	@echo "Generating fuzzy-search demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/fuzzy-search.tape && echo "✅ fuzzy-search.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-multi-select
demo-multi-select:
	@echo "Generating multi-select demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/multi-select.tape && echo "✅ multi-select.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-categories
demo-categories:
	@echo "Generating categories demo..."
	@mkdir -p demo/output
	@if command -v vhs >/dev/null 2>&1; then \
		vhs demo/categories.tape && echo "✅ categories.gif generated"; \
	else \
		echo "❌ VHS not installed. Install with: brew install vhs"; \
		exit 1; \
	fi

.PHONY: demo-help-system
demo-help-system:
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