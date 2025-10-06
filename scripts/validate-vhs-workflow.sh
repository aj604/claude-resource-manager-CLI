#!/bin/bash
# VHS Workflow Validation Script
# Validates GitHub Actions workflow and demo infrastructure
#
# Usage: ./scripts/validate-vhs-workflow.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Use virtualenv Python if available
if [ -f ".venv/bin/python3" ]; then
    PYTHON=".venv/bin/python3"
else
    PYTHON="python3"
fi

echo "🔍 VHS Workflow Validation"
echo "=" | tr '=' '=' | head -c 60; echo

# ============================================================================
# Colors for output
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() { echo -e "${GREEN}✅ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
info() { echo "ℹ️  $1"; }

# ============================================================================
# Check Dependencies
# ============================================================================
echo ""
echo "📦 Checking dependencies..."

# Check Python
if command -v $PYTHON &> /dev/null; then
    success "Python 3 installed: $($PYTHON --version)"
    if [ "$PYTHON" = ".venv/bin/python3" ]; then
        info "Using virtualenv Python"
    fi
else
    error "Python 3 not installed"
    exit 1
fi

# Check VHS (optional)
if command -v vhs &> /dev/null; then
    success "VHS installed: $(vhs --version 2>&1 | head -n1)"
else
    warning "VHS not installed (optional for local testing)"
    info "Install with: brew install vhs"
fi

# Check yamllint (optional)
if command -v yamllint &> /dev/null; then
    success "yamllint installed"
else
    warning "yamllint not installed (optional)"
    info "Install with: pip install yamllint"
fi

# ============================================================================
# Validate Workflow File
# ============================================================================
echo ""
echo "📄 Validating workflow file..."

WORKFLOW_FILE=".github/workflows/vhs-demos.yml"

if [ ! -f "$WORKFLOW_FILE" ]; then
    error "Workflow file not found: $WORKFLOW_FILE"
    exit 1
fi

success "Workflow file exists: $WORKFLOW_FILE"

# Check YAML syntax with yamllint if available
if command -v yamllint &> /dev/null; then
    if yamllint -d relaxed "$WORKFLOW_FILE"; then
        success "YAML syntax valid"
    else
        error "YAML syntax errors found"
        exit 1
    fi
fi

# Validate workflow structure with Python
$PYTHON << 'EOF'
import yaml
import sys
from pathlib import Path

workflow_file = Path('.github/workflows/vhs-demos.yml')

try:
    with open(workflow_file) as f:
        workflow = yaml.safe_load(f)

    # Check required top-level keys
    # Note: 'on' is a boolean in YAML, so it may be parsed as True
    required_keys = ['name', 'jobs']
    for key in required_keys:
        if key not in workflow:
            print(f'❌ Missing required key: {key}')
            sys.exit(1)

    # Check 'on' key (may be True boolean or 'on' string)
    if 'on' not in workflow and True not in workflow:
        print('❌ Missing required key: on (workflow triggers)')
        sys.exit(1)

    # Check jobs exist
    expected_jobs = [
        'security-scan',
        'generate-demos',
        'validate-all-demos',
        'test-vhs-integration',
        'commit-demos',
        'pr-preview',
        'notify-failure'
    ]

    for job in expected_jobs:
        if job not in workflow['jobs']:
            print(f'⚠️  Missing job: {job}')

    # Check matrix strategy for generate-demos
    if 'generate-demos' in workflow['jobs']:
        job = workflow['jobs']['generate-demos']
        if 'strategy' in job and 'matrix' in job['strategy']:
            demos = job['strategy']['matrix'].get('demo', [])
            expected_demos = [
                'quick-start',
                'fuzzy-search',
                'multi-select',
                'categories',
                'help-system'
            ]
            if set(demos) == set(expected_demos):
                print('✅ Matrix strategy includes all demos')
            else:
                print(f'⚠️  Matrix demos mismatch: {demos}')

    print('✅ Workflow structure valid')

except yaml.YAMLError as e:
    print(f'❌ YAML parsing error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Validation error: {e}')
    sys.exit(1)
EOF

# ============================================================================
# Validate Demo Infrastructure
# ============================================================================
echo ""
echo "🎬 Validating demo infrastructure..."

# Check demo directory
if [ -d "demo" ]; then
    success "Demo directory exists"
else
    error "Demo directory not found"
    exit 1
fi

# Check output directory
if [ -d "demo/output" ]; then
    success "Demo output directory exists"
else
    warning "Demo output directory missing (will be created)"
    mkdir -p demo/output
fi

# Check tape files
EXPECTED_TAPES=("quick-start" "fuzzy-search" "multi-select" "categories" "help-system")
MISSING_TAPES=()

for tape in "${EXPECTED_TAPES[@]}"; do
    if [ -f "demo/${tape}.tape" ]; then
        success "Tape file found: ${tape}.tape"
    else
        error "Tape file missing: ${tape}.tape"
        MISSING_TAPES+=("$tape")
    fi
done

if [ ${#MISSING_TAPES[@]} -gt 0 ]; then
    error "Missing ${#MISSING_TAPES[@]} tape file(s)"
    exit 1
fi

# ============================================================================
# Validate Tape File Syntax
# ============================================================================
echo ""
echo "🔍 Validating tape file syntax..."

for tape_file in demo/*.tape; do
    tape_name=$(basename "$tape_file")

    # Check required directives
    if ! grep -q "^Set Width" "$tape_file"; then
        error "$tape_name: Missing 'Set Width' directive"
        exit 1
    fi

    if ! grep -q "^Set Height" "$tape_file"; then
        error "$tape_name: Missing 'Set Height' directive"
        exit 1
    fi

    if ! grep -q "^Output" "$tape_file"; then
        error "$tape_name: Missing 'Output' directive"
        exit 1
    fi

    # Check dimensions (should be 1200x800)
    width=$(grep "^Set Width" "$tape_file" | awk '{print $3}')
    height=$(grep "^Set Height" "$tape_file" | awk '{print $3}')

    if [ "$width" != "1200" ] || [ "$height" != "800" ]; then
        warning "$tape_name: Non-standard dimensions (${width}x${height}), expected 1200x800"
    fi

    success "$tape_name: Syntax valid"
done

# ============================================================================
# Security Scan
# ============================================================================
echo ""
echo "🔒 Running security scan on tape files..."

$PYTHON << 'EOF'
from pathlib import Path
import re
import sys

dangerous_patterns = {
    r'\$\(': 'Command substitution detected',
    r'`[^`]*`': 'Backtick command execution',
    r'rm\s+-rf\s+/': 'Dangerous deletion command',
    r'sudo\s+': 'Privilege escalation attempt',
    r'curl\s+.*\|\s*sh': 'Remote code execution pattern',
    r'wget\s+.*\|\s*sh': 'Remote code execution pattern',
    r'chmod\s+777': 'Insecure permissions',
    r'eval\s+': 'Eval command detected',
}

warnings = []
errors = []

for tape in Path('demo').glob('*.tape'):
    content = tape.read_text()

    for pattern, description in dangerous_patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            if any(x in pattern for x in ['rm -rf /', 'curl.*|.*sh', 'eval']):
                errors.append(f'{tape.name}: {description}')
            else:
                warnings.append(f'{tape.name}: {description}')

if warnings:
    for w in warnings:
        print(f'⚠️  {w}')

if errors:
    print('\n🚨 Critical security issues found:')
    for e in errors:
        print(f'❌ {e}')
    sys.exit(1)

print('✅ Security scan passed')
EOF

# ============================================================================
# Check Integration Tests
# ============================================================================
echo ""
echo "🧪 Checking VHS integration tests..."

TEST_FILE="tests/integration/test_vhs_integration.py"

if [ -f "$TEST_FILE" ]; then
    success "VHS integration tests found"

    # Count test cases
    test_count=$(grep -c "def test_" "$TEST_FILE" || echo "0")
    info "Found $test_count test cases"
else
    error "VHS integration tests not found: $TEST_FILE"
    exit 1
fi

# ============================================================================
# Check Makefile Targets
# ============================================================================
echo ""
echo "🔧 Checking Makefile targets..."

if [ -f "Makefile" ]; then
    required_targets=("demos" "demo-clean")

    for target in "${required_targets[@]}"; do
        if grep -q "^\.PHONY: $target" Makefile && grep -q "^$target:" Makefile; then
            success "Makefile target exists: $target"
        else
            error "Makefile target missing: $target"
            exit 1
        fi
    done
else
    error "Makefile not found"
    exit 1
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "=" | tr '=' '=' | head -c 60; echo
echo "📊 Validation Summary"
echo "=" | tr '=' '=' | head -c 60; echo
echo ""
success "Workflow file: .github/workflows/vhs-demos.yml"
success "Tape files: ${#EXPECTED_TAPES[@]} files validated"
success "Integration tests: $TEST_FILE"
success "Makefile targets: demos, demo-clean"
echo ""

if command -v vhs &> /dev/null; then
    info "Ready for local demo generation: make demos"
else
    warning "Install VHS to test locally: brew install vhs"
fi

echo ""
success "✨ All validations passed!"
echo ""
