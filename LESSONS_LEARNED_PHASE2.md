# Phase 2 Lessons Learned - Parallel Subagent Efficiency

**Date**: 2025-10-05
**Context**: TDD with parallel subagents (4 test-generators, 3 implementers, 3 reviewers)

---

## 🎯 What Worked Exceptionally Well

1. **TDD with parallel test-generators** - Writing all tests first (RED phase) before any implementation provided crystal-clear specifications. 4 parallel agents created 125 tests in ~1 hour.

2. **Performance-first benchmarks** - Having pytest-benchmark tests from day 1 caught regressions immediately and guided optimization priorities.

3. **Security review in parallel** - Running security-reviewer agent alongside implementation (not after) would catch issues earlier when cheaper to fix.

---

## ⚠️ Efficiency Improvements for Future Phases

### 1. Map Agent Dependencies Before Launch
**Issue**: Launched all agents in parallel, but some had dependencies (e.g., documentation needs implementation complete).
**Fix**: Create dependency graph first:
```
test-gen (parallel) → impl agents (parallel) → review agents (parallel)
```
**Time Saved**: ~30 mins of waiting/re-runs

### 2. Test Specs Should Focus on Behavior, Not Implementation
**Issue**: 15 tests failed because they expected menu-based sorting, but we built superior one-key cycling.
**Fix**: Write tests like:
```python
# ❌ Too prescriptive
test_WHEN_s_then_1_THEN_sorts_by_name()  # Assumes menu

# ✅ Behavior-focused
test_WHEN_sort_action_THEN_changes_order()  # Accepts any sort UX
```
**Time Saved**: ~2 hours of test refactoring

### 3. Avoid Over-Testing
**Issue**: Generated 125 tests when ~80 would suffice. Some tests were redundant (e.g., testing same edge case multiple ways).
**Fix**: Before test generation, define coverage targets per component. Quality > quantity.
**Time Saved**: ~1 hour of test writing/maintenance

### 4. Run Documentation Agent Earlier
**Issue**: Documentation agent ran at end when implementation complete. Could run in parallel with later impl agents.
**Fix**: Launch documentation-agent after core features done (70% complete), not 100%.
**Time Saved**: ~30 mins (doc generation overlaps with polish work)

### 5. Agent Handoff Protocol
**Issue**: When agent completes, next agent had to re-read context to understand what was done.
**Fix**: Each agent should output:
- Summary of changes (files modified, key decisions)
- Blocking issues for next agent
- Recommended next steps

**Time Saved**: ~20 mins per agent transition

### 6. Checkbox Column Should Have Been P0
**Issue**: Deferred checkbox visual to Phase 3, but it caused 2 test failures and user confusion.
**Fix**: Visual feedback for state changes is P0, not polish. Include in initial implementation.
**Time Saved**: No re-work in Phase 3

---

## 📋 Recommended Agent Launch Pattern

For future phases, use this pattern:

```bash
# Step 1: Map dependencies
1. Review EPCC_PLAN.md
2. Identify which features can be built in parallel
3. Create dependency graph

# Step 2: Test generation (parallel)
Launch test-generator agents for independent components
Wait for all to complete before implementation

# Step 3: Implementation (waves)
Wave 1: Core features (parallel agents for independent features)
Wave 2: Integration features (depends on Wave 1)
Wave 3: Polish & UX (depends on Waves 1-2)

# Step 4: Review & docs (parallel, after 70% impl complete)
Launch security-reviewer + ux-optimizer + documentation-agent
Can overlap with Wave 3 implementation

# Step 5: Final integration
Verify all tests pass, address review findings
```

**Estimated Time Savings**: ~3-4 hours per major phase

---

## 🔑 Key Principles

1. **Parallel where possible, sequential where necessary** - Don't force parallelism if there are dependencies.

2. **Test behaviors, not implementation details** - Allows better UX without test refactoring.

3. **Visual feedback is P0** - If user state changes, they must see it immediately (not polish).

4. **Documentation at 70%, not 100%** - Start docs when architecture is clear, not when code is perfect.

5. **Agent handoffs need structure** - Summary output format for next agent to consume.

---

## 📊 Phase 2 Efficiency Metrics

- **Actual time**: ~6 hours (with parallel agents)
- **Estimated sequential**: ~20 hours
- **Parallelism speedup**: 3.3x
- **With improvements above**: Could be 4-5x (4-5 hours total)

---

**For Claude Code**: Read this before starting Phase 3 or similar multi-component implementations. Apply the "Agent Launch Pattern" above for maximum efficiency.
