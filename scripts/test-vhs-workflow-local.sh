#!/bin/bash
# Test VHS Workflow Locally
# Uses 'act' to simulate GitHub Actions locally
#
# Prerequisites: https://github.com/nektos/act
#   macOS: brew install act
#   Linux: See https://github.com/nektos/act#installation
#
# Usage: ./scripts/test-vhs-workflow-local.sh [job_name]
#   job_name: Optional, test specific job (security-scan, generate-demos, etc.)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

echo "🧪 VHS Workflow Local Testing"
echo "========================================"
echo ""

# Check for act
if ! command -v act &> /dev/null; then
    error "act is not installed"
    echo ""
    info "Install act to test GitHub Actions locally:"
    echo "  macOS:  brew install act"
    echo "  Linux:  curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    echo ""
    info "See: https://github.com/nektos/act"
    exit 1
fi

success "act is installed: $(act --version 2>&1 | head -n1)"
echo ""

# Get job name from argument or default to all
JOB_NAME="${1:-}"

if [ -z "$JOB_NAME" ]; then
    info "Testing full workflow (all jobs)"
    echo ""
    warning "Note: Full workflow may take 10-15 minutes"
    warning "Consider testing individual jobs first"
    echo ""
    info "Available jobs:"
    echo "  - security-scan"
    echo "  - generate-demos"
    echo "  - validate-all-demos"
    echo "  - test-vhs-integration"
    echo ""
    read -p "Continue with full workflow? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Cancelled. Run with job name to test specific job:"
        info "  ./scripts/test-vhs-workflow-local.sh security-scan"
        exit 0
    fi
fi

# Workflow file
WORKFLOW=".github/workflows/vhs-demos.yml"

if [ ! -f "$WORKFLOW" ]; then
    error "Workflow file not found: $WORKFLOW"
    exit 1
fi

success "Found workflow: $WORKFLOW"
echo ""

# Run act
info "Running act..."
echo ""

if [ -n "$JOB_NAME" ]; then
    info "Testing job: $JOB_NAME"
    echo ""
    act push \
        --job "$JOB_NAME" \
        --workflow "$WORKFLOW" \
        --verbose
else
    info "Testing all jobs"
    echo ""
    act push \
        --workflow "$WORKFLOW" \
        --verbose
fi

EXIT_CODE=$?

echo ""
echo "========================================"

if [ $EXIT_CODE -eq 0 ]; then
    success "Workflow test completed successfully!"
else
    error "Workflow test failed with exit code: $EXIT_CODE"
    echo ""
    info "Common issues:"
    echo "  1. Docker not running: Start Docker Desktop"
    echo "  2. Insufficient resources: Increase Docker memory limit"
    echo "  3. VHS not available: act runs in Ubuntu container"
    echo "  4. Missing secrets: act uses local .secrets file"
    echo ""
    info "For more help, see: https://github.com/nektos/act#known-issues"
fi

exit $EXIT_CODE
