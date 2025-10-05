# EPCC Workflow Documentation

This directory contains templates and documentation for the **Explore-Plan-Code-Commit (EPCC)** workflow.

## What is EPCC?

EPCC is Anthropic's recommended systematic approach to software development that ensures:

1. **🔍 EXPLORE** - Thorough understanding before action
2. **📋 PLAN** - Strategic design before implementation
3. **💻 CODE** - Disciplined implementation with quality
4. **✅ COMMIT** - Confident versioning with complete context

## Using the EPCC Workflow

### Phase 1: Explore

**Purpose:** Understand the codebase, requirements, and constraints

```bash
/epcc-explore "authentication system" --deep
```

**Generates:** `EPCC_EXPLORE.md` in your project root with:
- Project structure analysis
- Pattern identification
- Dependency mapping
- Similar implementations
- Constraints and risks

**Template:** [`EPCC_TEMPLATE_EXPLORE.md`](EPCC_TEMPLATE_EXPLORE.md)

### Phase 2: Plan

**Purpose:** Design the approach and break down the work

```bash
/epcc-plan "JWT authentication implementation"
```

**Generates:** `EPCC_PLAN.md` in your project root with:
- Implementation objectives
- Technical approach
- Task breakdown with estimates
- Risk assessment
- Testing strategy

**Template:** [`EPCC_TEMPLATE_PLAN.md`](EPCC_TEMPLATE_PLAN.md)

### Phase 3: Code

**Purpose:** Implement the solution with best practices

```bash
/epcc-code --tdd "implement user registration"
```

**Generates:** `EPCC_CODE.md` in your project root with:
- Implementation progress
- Code metrics and coverage
- Test results
- Key decisions documented
- Challenges and resolutions

**Template:** [`EPCC_TEMPLATE_CODE.md`](EPCC_TEMPLATE_CODE.md)

### Phase 4: Commit

**Purpose:** Review, test, and commit changes with confidence

```bash
/epcc-commit "feat: Add JWT authentication"
```

**Generates:** `EPCC_COMMIT.md` in your project root with:
- Complete change summary
- Testing and security validation
- Commit message (conventional commits format)
- Pull request description
- Deployment considerations

**Template:** [`EPCC_TEMPLATE_COMMIT.md`](EPCC_TEMPLATE_COMMIT.md)

## EPCC Automation

### Git Pre-Commit Hook

Located at `.git/hooks/pre-commit`

**Features:**
- ✅ Validates conventional commit message format
- ✅ Optional EPCC workflow enforcement (set `ENFORCE_EPCC=1`)
- ✅ Optional test execution before commit (set `RUN_TESTS=1`)
- ✅ Bypass capability for emergencies (set `EPCC_BYPASS=1`)

### GitHub Actions Workflow

Located at `.github/workflows/epcc-validation.yml`

**Validates:**
- ✅ EPCC documentation exists
- ✅ Commit message format
- ✅ Test coverage
- ✅ Code quality (ruff, mypy)
- ✅ Security (bandit)

## Best Practices

### 1. Always Explore First

```bash
# ❌ WRONG: Jump straight to coding
/epcc-code "implement feature"

# ✅ RIGHT: Explore first
/epcc-explore "existing patterns"
/epcc-plan "new feature"
/epcc-code "implement from plan"
```

### 2. Plan Before Implementing

```bash
# ❌ WRONG: Code without a plan
# (Start coding immediately)

# ✅ RIGHT: Plan systematically
/epcc-plan "OAuth support"
# Review EPCC_PLAN.md
/epcc-code "implement first task"
```

### 3. Incremental Implementation

```bash
# ❌ WRONG: Try to do everything at once
/epcc-code "rewrite entire backend"

# ✅ RIGHT: Work incrementally
/epcc-code "implement task 1 from plan"
# Test and verify
/epcc-code "implement task 2 from plan"
```

### 4. Meaningful Commits

```bash
# ❌ WRONG: Generic commit messages
git commit -m "updates"

# ✅ RIGHT: Use /epcc-commit for structured commits
/epcc-commit "feat(auth): Add JWT validation with refresh tokens"
```

## Environment Variables

```bash
# Enforce EPCC workflow (requires .epcc/exploration-complete and .epcc/plan-complete)
export ENFORCE_EPCC=1

# Run tests before allowing commits
export RUN_TESTS=1

# Bypass EPCC validation (use only for hotfixes/emergencies)
export EPCC_BYPASS=1
```

## Example Workflow

### Scenario: Adding a New Feature

```bash
# 1. EXPLORE - Understand existing patterns
/epcc-explore "shopping cart implementation" --deep
# → Creates EPCC_EXPLORE.md with analysis

# 2. PLAN - Design the enhancement
/epcc-plan "add saved items to shopping cart"
# → Creates EPCC_PLAN.md with tasks and timeline

# 3. CODE - Implement incrementally
/epcc-code --tdd "implement cart persistence layer"
# → Creates EPCC_CODE.md tracking progress
/epcc-code "implement UI components"
# → Updates EPCC_CODE.md with progress

# 4. COMMIT - Finalize with documentation
/epcc-commit "feat: Add persistent shopping cart"
# → Creates EPCC_COMMIT.md with PR-ready content
# → Creates properly formatted commit
# → Can generate PR from EPCC_COMMIT.md
```

### Scenario: Fixing a Bug

```bash
# 1. EXPLORE - Investigate root cause
/epcc-explore "login bug #456" --focus authentication

# 2. PLAN - Design the fix
/epcc-plan "fix session timeout handling"

# 3. CODE - Fix with tests
/epcc-code --tdd "add session timeout test and fix"

# 4. COMMIT - Document the fix
/epcc-commit "fix: Resolve login session timeout issue"
```

## Output Files

All EPCC commands generate markdown files in your project root:

- `EPCC_EXPLORE.md` - Exploration findings
- `EPCC_PLAN.md` - Implementation plan
- `EPCC_CODE.md` - Implementation progress
- `EPCC_COMMIT.md` - Commit documentation

**Note:** These files should be committed to your repository as they:
- Document the development process
- Serve as project knowledge base
- Help with code reviews
- Assist future developers

## Quick Reference

```
┌─────────────────────────────────────────────────┐
│              EPCC WORKFLOW                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. EXPLORE 🔍 → EPCC_EXPLORE.md              │
│     /epcc-explore "area" [--deep|--quick]      │
│                                                 │
│  2. PLAN 📋 → EPCC_PLAN.md                    │
│     /epcc-plan "feature"                       │
│                                                 │
│  3. CODE 💻 → EPCC_CODE.md                    │
│     /epcc-code [--tdd] "task"                  │
│                                                 │
│  4. COMMIT ✅ → EPCC_COMMIT.md                │
│     /epcc-commit "type: message"               │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Further Reading

- [EPCC Workflow Guide](https://github.com/anthropics/claude-code/docs/epcc-workflow-guide.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
