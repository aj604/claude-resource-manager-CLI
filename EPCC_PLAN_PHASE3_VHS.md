# Phase 3 Implementation Plan: Polish, Accessibility & VHS Documentation

**Project:** Claude Resource Manager CLI - Phase 3
**Date:** October 5, 2025
**Phase:** PLAN (EPCC Workflow)
**Status:** Active Planning
**Methodology:** Test-Driven Development with Parallel Agent Workflow

---

## Executive Summary

Phase 3 combines essential polish, accessibility improvements, and professional VHS-based documentation to elevate the Claude Resource Manager from production-ready to production-excellent. This phase incorporates the VHS Documentation feature request while completing critical accessibility work and visual polish.

**Key Objectives:**
1. **VHS Documentation System** - Professional animated demos for onboarding and feature discovery
2. **Accessibility Compliance** - Achieve 100% WCAG 2.1 AA compliance (currently 78%)
3. **Visual Polish** - Complete checkbox column and multi-select UX
4. **Test Alignment** - Fix 15 UI tests to match one-key cycling sort UX

**Timeline:** 2-3 weeks (40-60 hours total)
**Approach:** TDD with parallel agent execution (based on Phase 2 lessons learned)
**Expected ROI:** 40% reduction in time-to-first-use, 60% improvement in feature discovery

---

## Feature Objectives

### 1. VHS Documentation System (Priority: HIGH)

#### What We're Building
A comprehensive terminal recording system using VHS (by Charm/Textual creators) to generate professional animated GIFs demonstrating all Phase 2 features. This will dramatically improve user onboarding and feature discoverability.

#### Why It's Needed
**Current Pain Points:**
- 100% text-based documentation (no visual context)
- Users don't see TUI before installing ("what does it look like?")
- Phase 2 features underutilized (fuzzy search, multi-select, categories)
- High cognitive load for first-time users

**Business Value:**
- **Industry Standard**: GitHub CLI, Stripe CLI, Charm's tools all use VHS demos
- **Reduced Friction**: Visual demos show real experience, not imagination
- **Better Onboarding**: 40% reduction in time-to-first-use (estimated)
- **Feature Discovery**: 60% improvement (users discover ? help, categories, etc.)
- **Professional Polish**: Matches industry-leading CLI documentation

#### Success Criteria
- [ ] 5 VHS `.tape` files created and tested (quick-start, fuzzy-search, multi-select, categories, help-system)
- [ ] All demos generate GIFs <2MB (GitHub-optimized)
- [ ] README.md updated with embedded demos above the fold
- [ ] CI/CD pipeline auto-regenerates demos on TUI changes
- [ ] Makefile targets for local demo generation
- [ ] Documentation quality: Demos feel natural (not too fast/slow)

#### Non-Goals
- ❌ Video tutorials or screen recordings (GIFs only)
- ❌ Interactive demos (static GIFs for GitHub display)
- ❌ Multiple language versions (English only for v1.0)
- ❌ Social media assets beyond repository preview (Phase 4)

---

### 2. Accessibility Compliance (Priority: HIGH)

#### What We're Building
Complete WCAG 2.1 AA compliance with screen reader support, color contrast verification, and enhanced error recovery.

#### Why It's Needed
**Current State:** 78% WCAG 2.1 AA compliance
**Gaps:**
- Screen reader announcements missing for state changes
- Color contrast not verified programmatically
- Error recovery could be more robust
- Keyboard traps possible in modal dialogs

**Business Value:**
- **Legal Compliance**: Many organizations require WCAG AA
- **Inclusive Design**: Accessible to all developers
- **Better UX for Everyone**: Improved error messages, keyboard navigation benefit all users

#### Success Criteria
- [ ] 100% WCAG 2.1 AA compliance verified
- [ ] Screen reader testing completed (VoiceOver on macOS, NVDA on Windows)
- [ ] Color contrast ratios >= 4.5:1 for all text
- [ ] Enhanced error recovery with user guidance
- [ ] No keyboard traps (Esc always exits modals)
- [ ] ARIA attributes where appropriate

---

### 3. Visual Polish & UX Refinements (Priority: MEDIUM)

#### What We're Building
Complete checkbox column implementation, visual selection indicators, and real-time update animations.

#### Why It's Needed
**Current State:** Multi-select works functionally but visual feedback is basic
**Issues from Phase 2:**
- Checkbox column deferred to Phase 3 (caused 2 test failures)
- Visual state changes need better feedback
- Selection count could be more prominent

**Business Value:**
- **User Confidence**: Clear visual feedback reduces errors
- **Professional Feel**: Polished UI matches quality of underlying implementation
- **Reduced Support**: Better visuals = fewer "how do I...?" questions

#### Success Criteria
- [ ] Checkbox column with visual indicators ([x] checked, [ ] unchecked)
- [ ] Selection count prominently displayed
- [ ] Real-time animations for state changes
- [ ] Consistent with Phase 2 design language

---

### 4. Test Alignment (Priority: HIGH)

#### What We're Building
Update 15 UI tests that expect menu-based sorting to work with superior one-key cycling UX.

#### Why It's Needed
**Current State:** 476/477 tests passing (99.79%)
**Issue:** Tests written before UX improvement assumed menu-based sort, but we built one-key cycling (better UX, but tests need updating)

**Lesson from Phase 2:** Test behaviors, not implementation details

#### Success Criteria
- [ ] All 477 tests passing (100%)
- [ ] Tests focus on behaviors (sort changes order) not implementation (specific keypresses)
- [ ] No regressions to existing functionality
- [ ] Test suite runs in <30 seconds

---

## Technical Approach

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3 COMPONENTS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  VHS Documentation Layer (NEW)                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ demo/*.tape files → VHS → GIFs → README.md / docs/        │  │
│  │ - quick-start.tape (30s overview)                          │  │
│  │ - fuzzy-search.tape (typo tolerance demo)                  │  │
│  │ - multi-select.tape (batch operations)                     │  │
│  │ - categories.tape (filtering demo)                         │  │
│  │ - help-system.tape (? modal demo)                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Accessibility Layer (ENHANCED)                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ TUI Components with ARIA + Screen Reader Support           │  │
│  │ - State change announcements                               │  │
│  │ - Color contrast validation                                │  │
│  │ - Enhanced error recovery                                  │  │
│  │ - Keyboard trap prevention                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Visual Polish Layer (ENHANCED)                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Multi-Select UI with Visual Feedback                       │  │
│  │ - Checkbox column ([x] indicators)                         │  │
│  │ - Selection count display                                  │  │
│  │ - Real-time update animations                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Phase 2 Foundation (STABLE)
                    - Fuzzy search (0.29ms)
                    - Category system (0.77ms)
                    - Multi-select core logic
                    - 457 tests, 92% coverage
```

### Design Decisions

| Decision | Option Chosen | Rationale | Trade-off Accepted |
|----------|--------------|-----------|-------------------|
| **Doc Tool** | VHS by Charm | Scriptable, CI-friendly, industry standard for Textual apps | Requires VHS installation for local demo generation |
| **Demo Format** | Animated GIF | Native GitHub support, auto-play, works everywhere | Larger files than static images (~2MB each) |
| **Accessibility Testing** | Manual + Automated | VoiceOver/NVDA + pytest checks | More comprehensive than automated-only |
| **Visual Polish** | Textual built-in components | Consistent with framework, well-tested | Less customizable than custom widgets |
| **Test Updates** | Behavior-focused assertions | Future-proof against UX improvements | Requires careful test redesign |
| **CI Integration** | GitHub Actions | Already in use, VHS supports headless mode | Linux-only for CI (macOS for local dev) |

### Data Flow

#### VHS Demo Generation Workflow

```
1. Developer Updates TUI Code
   └─> Commits to feature branch
       └─> CI detects changes in src/claude_resource_manager/tui/**

2. GitHub Actions Workflow Triggers
   └─> Install VHS in Ubuntu runner
       └─> Setup Python + install dependencies
           └─> Execute all .tape files in demo/

3. VHS Processes Each .tape File
   demo/quick-start.tape
   ├─> VHS launches headless terminal
   │   ├─> Executes scripted commands (Type, Sleep, Enter, etc.)
   │   └─> Captures terminal output frame-by-frame
   ├─> Generates GIF with specified dimensions (1200x800px)
   └─> Optimizes output (target <2MB)

4. Output & Deployment
   ├─> Generated GIFs placed in demo/output/
   ├─> CI uploads as build artifacts
   └─> If main branch: Auto-commit GIFs back to repo
       └─> README.md displays updated demos
```

#### Accessibility Enhancement Workflow

```
1. Screen Reader Announcement System
   User Action (e.g., select resource)
   └─> TUI updates model state
       └─> Textual generates DOM update
           └─> ARIA live region announces change
               └─> Screen reader speaks: "Resource selected: architect"

2. Color Contrast Validation (pytest)
   Test Suite Runs
   └─> Read theme configuration
       └─> Extract foreground/background colors
           └─> Calculate contrast ratios (WCAG formula)
               └─> Assert ratio >= 4.5:1 for normal text
                   └─> Assert ratio >= 3:1 for large text

3. Enhanced Error Recovery
   Error Occurs (e.g., network failure)
   └─> Catch exception with context
       └─> Display user-friendly message
           └─> Offer recovery options
               ├─> Retry operation
               ├─> Skip and continue
               └─> Cancel workflow
           └─> Log detailed error for debugging
```

---

## TDD Implementation Strategy (Based on Phase 2 Lessons)

### RED Phase: Write Tests FIRST (Week 1, Days 1-2)

**Objective:** Create comprehensive test specifications before any implementation

#### Test Generation with Parallel Agents (4 agents, ~2 hours)

Launch 4 test-generator agents in parallel:

1. **VHS Integration Tests** (test-generator #1)
   - Test `.tape` file execution succeeds
   - Test GIF output exists and is <2MB
   - Test GIF dimensions correct (1200x800)
   - Test demo timing feels natural (30s, 20s, etc.)
   - Estimated: 15 tests

2. **Accessibility Tests** (test-generator #2)
   - Screen reader announcement tests
   - Color contrast ratio tests (all themes)
   - Keyboard trap prevention tests
   - Error recovery workflow tests
   - Estimated: 25 tests

3. **Visual Polish Tests** (test-generator #3)
   - Checkbox column rendering tests
   - Selection state indicator tests
   - Animation timing tests
   - Multi-select visual feedback tests
   - Estimated: 20 tests

4. **Test Alignment Updates** (test-generator #4)
   - Refactor 15 sorting tests to be behavior-focused
   - Remove implementation-specific assertions
   - Add behavior contracts (sort changes order, not keypresses)
   - Estimated: 15 tests (updates to existing)

**Total Tests:** ~75 new/updated tests
**All tests should FAIL initially** (RED phase complete)

**Key Principle (from Phase 2):** Write behavior-focused tests, not implementation-specific
```python
# ❌ Too prescriptive (will break with UX changes)
def test_WHEN_s_then_1_THEN_sorts_by_name():
    app.press("s")
    app.press("1")
    assert first_item.name < second_item.name

# ✅ Behavior-focused (survives UX improvements)
def test_WHEN_sort_action_THEN_resources_ordered_by_name():
    app.trigger_sort_by_name()  # Abstract the "how"
    assert resources_sorted_by("name")  # Assert the "what"
```

---

### GREEN Phase: Make Tests Pass (Week 1 Day 3 - Week 2)

**Objective:** Implement features to make all tests pass (minimal working implementation)

#### Implementation Waves (3 waves, parallel within each wave)

**Wave 1: Core Features** (Days 3-5, parallel agents)

Launch 3 implementation agents in parallel (no dependencies):

1. **VHS Infrastructure** (implementation agent #1)
   - Create `demo/` directory structure
   - Write 5 `.tape` files (quick-start, fuzzy-search, multi-select, categories, help-system)
   - Create `demo/README.md` with generation instructions
   - Add Makefile targets (`make demos`, `make demo-quick-start`, etc.)
   - Estimated: 6 hours

2. **Accessibility Core** (implementation agent #2)
   - Add screen reader announcements (Textual ARIA attributes)
   - Implement color contrast validation utilities
   - Add keyboard trap prevention (Esc handler in all modals)
   - Estimated: 8 hours

3. **Visual Polish Core** (implementation agent #3)
   - Implement checkbox column in DataTable
   - Add selection count display widget
   - Create selection state indicators ([x] / [ ])
   - Estimated: 6 hours

**Wave 2: Integration Features** (Days 6-7, depends on Wave 1)

Launch 2 agents in parallel:

1. **CI/CD Integration** (implementation agent #4)
   - Create `.github/workflows/vhs-demos.yml`
   - Add VHS installation to CI
   - Configure auto-commit for generated GIFs
   - Test workflow on feature branch
   - Estimated: 4 hours

2. **Enhanced Error Recovery** (implementation agent #5)
   - Implement user-friendly error messages
   - Add retry/skip/cancel options
   - Create error recovery workflows
   - Estimated: 6 hours

**Wave 3: Polish & Documentation** (Week 2, depends on Waves 1-2)

Launch 2 agents in parallel:

1. **Documentation Integration** (documentation-agent)
   - Update README.md with embedded GIFs
   - Update docs/PHASE_2_FEATURES.md with feature demos
   - Create comprehensive demo/README.md
   - Update CLAUDE.md with VHS setup instructions
   - Estimated: 4 hours

2. **Test Alignment** (implementation agent #6)
   - Update 15 sorting tests to match behavior contracts
   - Remove implementation-specific assertions
   - Verify all 477 tests pass
   - Estimated: 2 hours

**All tests should PASS** (GREEN phase complete)

---

### REFACTOR Phase: Optimize & Review (Week 2-3)

**Objective:** Improve code quality, run parallel reviews, optimize performance

#### Review Agents (Parallel, after 70% implementation complete)

Launch 3 review agents in parallel:

1. **Security Review** (security-reviewer agent)
   - Audit VHS tape files for command injection risks
   - Review CI workflow for security best practices
   - Validate error messages don't leak sensitive info
   - Check accessibility features don't introduce XSS
   - Estimated: 2 hours

2. **UX Optimization** (ux-optimizer agent)
   - Verify all UI changes follow WCAG 2.1 AA
   - Test screen reader experience (VoiceOver/NVDA)
   - Validate color contrast ratios programmatically
   - Review keyboard navigation flows
   - Estimated: 3 hours

3. **Documentation Quality** (documentation-agent, if not already complete)
   - Verify all demos are accurate and up-to-date
   - Ensure README GIFs display correctly on GitHub
   - Check demo timing and clarity
   - Validate installation instructions
   - Estimated: 2 hours

#### Performance & Polish

- Optimize GIF file sizes (use gifsicle if >2MB)
- Refactor duplicate code
- Clean up test fixtures
- Final test suite run: All 477+ tests passing
- Estimated: 3 hours

**REFACTOR complete** → Ready for COMMIT phase

---

## Agent Dependency Graph & Parallel Execution Strategy

Based on Phase 2 lessons learned, here's the optimal agent execution strategy:

### Dependency Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT EXECUTION TIMELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│ RED PHASE (Days 1-2): Test Generation                           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│ │ test-gen #1 │ │ test-gen #2 │ │ test-gen #3 │ │ test-gen #4│ │
│ │ (VHS tests) │ │ (a11y tests)│ │ (visual)    │ │ (align)    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
│        ↓                ↓                ↓              ↓        │
│        └────────────────┴────────────────┴──────────────┘        │
│                            │                                     │
│                            ▼                                     │
│ GREEN PHASE - WAVE 1 (Days 3-5): Core Implementation            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│ │  impl #1    │ │  impl #2    │ │  impl #3                    ││
│ │ (VHS infra) │ │ (a11y core) │ │ (visual core)               ││
│ └─────────────┘ └─────────────┘ └─────────────────────────────┘│
│        ↓                ↓                      ↓                 │
│        └────────────────┴──────────────────────┘                 │
│                            │                                     │
│                            ▼                                     │
│ GREEN PHASE - WAVE 2 (Days 6-7): Integration                    │
│ ┌─────────────────────────────┐ ┌───────────────────────────┐  │
│ │  impl #4 (CI/CD)            │ │  impl #5 (error recovery) │  │
│ └─────────────────────────────┘ └───────────────────────────┘  │
│                ↓                              ↓                  │
│                └──────────────────────────────┘                  │
│                            │                                     │
│                            ▼                                     │
│ GREEN PHASE - WAVE 3 (Week 2): Polish & Docs                    │
│ ┌─────────────────────────────┐ ┌───────────────────────────┐  │
│ │  docs (README, demos)       │ │  impl #6 (test alignment) │  │
│ └─────────────────────────────┘ └───────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│ REFACTOR PHASE (Week 2-3): Review & Optimize                    │
│ ┌──────────────┐ ┌──────────────┐ ┌─────────────────────────┐  │
│ │ security     │ │ ux-optimizer │ │ final polish            │  │
│ └──────────────┘ └──────────────┘ └─────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

Legend:
│ = Sequential dependency
─ = Parallel (no dependency)
```

### Parallel Execution Commands

**RED Phase:**
```bash
# Launch all test-generators in parallel (single message, multiple Task calls)
- test-generator: "Write VHS integration tests (15 tests)"
- test-generator: "Write accessibility tests (25 tests)"
- test-generator: "Write visual polish tests (20 tests)"
- test-generator: "Update sorting tests to be behavior-focused (15 tests)"
```

**GREEN Phase - Wave 1:**
```bash
# Launch core implementers in parallel
- architect: "Implement VHS infrastructure (demo/ dir, .tape files, Makefile)"
- architect: "Implement accessibility core (screen reader, color contrast, keyboard)"
- architect: "Implement visual polish core (checkbox column, selection indicators)"
```

**GREEN Phase - Wave 2:**
```bash
# Launch integration implementers in parallel (after Wave 1)
- deployment-agent: "Implement CI/CD for VHS demos (.github/workflows/vhs-demos.yml)"
- architect: "Implement enhanced error recovery system"
```

**GREEN Phase - Wave 3:**
```bash
# Launch polish agents in parallel (after Waves 1-2)
- documentation-agent: "Update README and docs with VHS demos"
- architect: "Align 15 sorting tests with behavior contracts"
```

**REFACTOR Phase:**
```bash
# Launch reviewers in parallel (after 70% implementation)
- security-reviewer: "Audit VHS and accessibility for security"
- ux-optimizer: "Verify WCAG 2.1 AA compliance and UX quality"
- (documentation-agent already complete from Wave 3)
```

**Estimated Parallelism Speedup:** 3-4x (based on Phase 2 metrics)
**Sequential Estimate:** 60 hours
**With Parallel Agents:** 15-20 hours

---

## Implementation Task Breakdown

### Phase 3 Complete Task List

#### RED Phase: Test Generation (2 hours)

**Test-Generator Agents (4 parallel)**

- [ ] **VHS-001** (30 min): Generate VHS integration tests
  - Test `.tape` file execution
  - Test GIF generation and file size
  - Test demo timing validation
  - Dependencies: None | Priority: P0

- [ ] **A11Y-001** (45 min): Generate accessibility tests
  - Screen reader announcement tests
  - Color contrast validation tests
  - Keyboard trap prevention tests
  - Error recovery tests
  - Dependencies: None | Priority: P0

- [ ] **VIS-001** (30 min): Generate visual polish tests
  - Checkbox column rendering tests
  - Selection indicator tests
  - Animation timing tests
  - Dependencies: None | Priority: P0

- [ ] **TEST-001** (15 min): Update sorting tests
  - Refactor 15 tests to behavior-focused
  - Remove implementation-specific assertions
  - Dependencies: None | Priority: P0

**RED Phase Deliverable:** ~75 tests, all FAILING

---

#### GREEN Phase - Wave 1: Core Implementation (3 days)

**Implementation Agents (3 parallel)**

- [ ] **VHS-101** (6h): VHS infrastructure setup
  - Create `demo/` directory structure
  - Write 5 `.tape` files (quick-start, fuzzy-search, multi-select, categories, help)
  - Create `demo/README.md`
  - Add Makefile targets (`demos`, `demo-*`)
  - Dependencies: VHS-001 tests | Priority: P0

- [ ] **A11Y-101** (8h): Accessibility core implementation
  - Add screen reader announcements (Textual ARIA)
  - Implement color contrast validation
  - Add keyboard trap prevention
  - Update TUI components with accessibility attributes
  - Dependencies: A11Y-001 tests | Priority: P0

- [ ] **VIS-101** (6h): Visual polish core
  - Implement checkbox column in DataTable
  - Add selection count widget
  - Create selection indicators ([x] / [ ])
  - Dependencies: VIS-001 tests | Priority: P0

**Wave 1 Deliverable:** Core features implemented, tests starting to pass

---

#### GREEN Phase - Wave 2: Integration (2 days)

**Implementation Agents (2 parallel, depends on Wave 1)**

- [ ] **VHS-201** (4h): CI/CD integration
  - Create `.github/workflows/vhs-demos.yml`
  - Add VHS installation to Ubuntu runner
  - Configure demo generation on TUI changes
  - Set up auto-commit for GIFs (main branch only)
  - Dependencies: VHS-101 | Priority: P0

- [ ] **A11Y-201** (6h): Enhanced error recovery
  - Implement user-friendly error messages
  - Add retry/skip/cancel options
  - Create error recovery workflows
  - Test error scenarios
  - Dependencies: A11Y-101 | Priority: P1

**Wave 2 Deliverable:** Full integration, CI working, error handling robust

---

#### GREEN Phase - Wave 3: Polish & Docs (2 days)

**Agents (2 parallel, depends on Waves 1-2)**

- [ ] **DOC-301** (4h): Documentation integration
  - Update README.md with embedded GIFs (above fold)
  - Update docs/PHASE_2_FEATURES.md with feature demos
  - Create comprehensive demo/README.md
  - Update CLAUDE.md with VHS setup
  - Dependencies: VHS-101, VHS-201 | Priority: P0

- [ ] **TEST-301** (2h): Test alignment
  - Update 15 sorting tests to behavior contracts
  - Remove implementation-specific assertions
  - Verify all 477+ tests pass
  - Dependencies: TEST-001, GREEN Wave 1 | Priority: P0

**Wave 3 Deliverable:** Documentation complete, all tests passing (GREEN phase complete)

---

#### REFACTOR Phase: Review & Optimize (3-5 days)

**Review Agents (3 parallel, after 70% implementation)**

- [ ] **SEC-401** (2h): Security review
  - Audit `.tape` files for command injection
  - Review CI workflow security
  - Validate error messages (no info leakage)
  - Check accessibility features for XSS
  - Dependencies: GREEN Wave 2 | Priority: P0

- [ ] **UX-401** (3h): UX optimization
  - Verify WCAG 2.1 AA compliance
  - Test screen readers (VoiceOver, NVDA)
  - Validate color contrast ratios
  - Review keyboard navigation
  - Dependencies: GREEN Wave 2 | Priority: P0

- [ ] **OPT-401** (3h): Performance & polish
  - Optimize GIF file sizes (gifsicle)
  - Refactor duplicate code
  - Clean up test fixtures
  - Final test suite validation
  - Dependencies: GREEN Wave 3 | Priority: P1

**REFACTOR Deliverable:** Production-ready code, all reviews passed

---

## Risk Assessment

### Risk Matrix

| Risk | Probability | Impact | Score | Mitigation Strategy |
|------|-------------|--------|-------|-------------------|
| **R1: VHS installation complexity** | Medium | Medium | 9 | Provide comprehensive docs, support multiple install methods, CI auto-generates |
| **R2: Demo maintenance burden** | Low | High | 8 | CI auto-regenerates on changes, version-controlled .tape files |
| **R3: GIF file sizes too large** | Low | Medium | 6 | Target <2MB, optimize with gifsicle, use LoopOffset to reduce frames |
| **R4: Accessibility testing incomplete** | Medium | High | 12 | Manual testing (VoiceOver/NVDA) + automated pytest checks |
| **R5: CI performance impact** | Low | Low | 4 | Run demo workflow only on TUI changes, cache VHS binary |
| **R6: Test refactoring breaks functionality** | Low | Critical | 12 | Careful review, behavior-focused tests, full regression suite |
| **R7: Screen reader compatibility** | Medium | Medium | 9 | Test on multiple screen readers, use Textual best practices |
| **R8: Scope creep (Phase 4 features)** | Medium | Medium | 9 | Strict P0/P1/P2 triage, defer social assets to Phase 4 |

### Critical Risks & Mitigation

**R4: Accessibility testing incomplete** (Score: 12)
- **Mitigation:**
  - Manual testing on VoiceOver (macOS) and NVDA (Windows)
  - Automated color contrast tests in pytest
  - Accessibility audit checklist (WCAG 2.1 AA)
  - User testing with screen reader users

**R6: Test refactoring breaks functionality** (Score: 12)
- **Mitigation:**
  - Write new behavior-focused tests FIRST
  - Run full regression suite after each test update
  - Careful review of test changes
  - Keep implementation-specific tests temporarily, remove after validation

**R1: VHS installation complexity** (Score: 9)
- **Mitigation:**
  - Clear installation docs in demo/README.md
  - Support Homebrew (macOS), apt (Linux), binary downloads
  - CI generates demos (local generation optional)
  - Troubleshooting section for common issues

---

## Testing Strategy

### Test Coverage Targets

| Component | Target | Rationale |
|-----------|--------|-----------|
| **VHS Integration** | 90% | Critical for documentation quality |
| **Accessibility** | 95% | Legal/compliance requirement |
| **Visual Polish** | 85% | UI components, harder to test |
| **Overall Phase 3** | 93% | Raise from current 92% |

### Test Categories

#### VHS Integration Tests (15 tests)

**Unit Tests:**
- `.tape` file syntax validation
- GIF output file creation
- File size validation (<2MB)
- Dimensions validation (1200x800)
- Demo timing validation (30s, 20s, etc.)

**Integration Tests:**
- Makefile targets execute correctly
- CI workflow generates all demos
- Auto-commit pushes to repository
- README.md displays GIFs correctly

**Example Test:**
```python
def test_WHEN_quick_start_tape_executes_THEN_gif_generated():
    """VHS generates quick-start.gif from .tape file"""
    # Arrange
    tape_file = "demo/quick-start.tape"
    output_gif = "demo/output/quick-start.gif"

    # Act
    result = subprocess.run(["vhs", tape_file], capture_output=True)

    # Assert
    assert result.returncode == 0, "VHS execution should succeed"
    assert Path(output_gif).exists(), "GIF should be created"
    assert Path(output_gif).stat().st_size < 2 * 1024 * 1024, "GIF <2MB"
```

#### Accessibility Tests (25 tests)

**Screen Reader Tests:**
- State change announcements
- ARIA attributes correct
- Focus management
- Keyboard navigation

**Color Contrast Tests:**
- All themes meet WCAG AA (4.5:1)
- Large text meets 3:1 ratio
- Automated validation in pytest

**Error Recovery Tests:**
- User-friendly error messages
- Retry/skip/cancel options work
- No information leakage

**Example Test:**
```python
def test_WHEN_resource_selected_THEN_screen_reader_announces():
    """Screen reader announces resource selection"""
    # Arrange
    app = BrowserApp()

    # Act
    app.select_resource("architect")

    # Assert
    announcement = app.get_aria_live_region_text()
    assert "architect" in announcement.lower()
    assert "selected" in announcement.lower()
```

#### Visual Polish Tests (20 tests)

**Checkbox Column Tests:**
- Renders for all resources
- Shows checked/unchecked state
- Updates on selection toggle

**Selection Indicator Tests:**
- [x] shows when selected
- [ ] shows when unselected
- Count updates in real-time

**Example Test:**
```python
def test_WHEN_space_pressed_THEN_checkbox_shows_x():
    """Checkbox shows [x] when resource selected"""
    # Arrange
    app = BrowserApp()
    app.focus_resource("architect")

    # Act
    app.press("space")

    # Assert
    checkbox = app.get_checkbox_for_resource("architect")
    assert checkbox.text == "[x]", "Should show checked indicator"
```

#### Test Alignment Updates (15 tests)

**Refactored Tests (behavior-focused):**
```python
# Before (implementation-specific)
def test_WHEN_s_then_1_THEN_sorts_by_name():
    app.press("s")
    app.press("1")
    assert resources[0].name < resources[1].name

# After (behavior-focused)
def test_WHEN_sort_by_name_triggered_THEN_resources_alphabetically_ordered():
    app.trigger_sort_by_name()  # Abstract the "how"
    assert all(
        resources[i].name <= resources[i+1].name
        for i in range(len(resources)-1)
    )
```

---

## Success Metrics & Acceptance Criteria

### Functional Requirements

**VHS Documentation:**
- [ ] 5 `.tape` files created (quick-start, fuzzy-search, multi-select, categories, help)
- [ ] All demos execute successfully
- [ ] Generated GIFs <2MB each (GitHub-optimized)
- [ ] README.md updated with embedded GIFs above fold
- [ ] docs/PHASE_2_FEATURES.md updated with feature demos
- [ ] CI/CD workflow auto-generates demos on TUI changes
- [ ] Makefile includes `demos` target
- [ ] demo/README.md documents generation process

**Accessibility:**
- [ ] 100% WCAG 2.1 AA compliance verified
- [ ] Screen reader testing complete (VoiceOver + NVDA)
- [ ] Color contrast ratios >= 4.5:1 (normal text)
- [ ] Color contrast ratios >= 3:1 (large text)
- [ ] Enhanced error recovery with user guidance
- [ ] No keyboard traps (Esc exits all modals)

**Visual Polish:**
- [ ] Checkbox column implemented with [x]/[ ] indicators
- [ ] Selection count prominently displayed
- [ ] Real-time update animations
- [ ] Consistent with Phase 2 design

**Test Quality:**
- [ ] All 477+ tests passing (100%)
- [ ] 15 sorting tests refactored to behavior-focused
- [ ] No regressions to existing functionality
- [ ] Test suite coverage >= 93%

### Performance Metrics

- [ ] CI demo generation <5 minutes
- [ ] VHS startup time <2 seconds per demo
- [ ] Total GIF assets <10MB
- [ ] No performance regressions (all Phase 2 benchmarks still met)

### Quality Metrics

- [ ] Zero critical bugs in Phase 3 features
- [ ] Zero accessibility violations (automated scan)
- [ ] Zero security issues (bandit, safety checks pass)
- [ ] Documentation accuracy: 100% (demos match actual behavior)

### User Experience Metrics

**Estimated Improvements:**
- [ ] Time-to-first-use: 15 min → 9 min (40% reduction)
- [ ] Feature discovery: 40% → 80% (2x improvement)
- [ ] GitHub stars/week: 5 → 15 (3x increase, 1 month post-launch)
- [ ] Installation success rate: >99%

---

## Timeline & Milestones

### 3-Week Sprint Plan

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEEK 1: RED → GREEN (Wave 1)              │
├─────────────────────────────────────────────────────────────────┤
│ Mon-Tue: RED Phase (Test Generation)                            │
│   - Launch 4 test-generator agents in parallel                   │
│   - Generate ~75 tests (VHS, accessibility, visual, alignment)   │
│   - All tests FAILING (RED phase complete)                       │
│                                                                   │
│ Wed-Fri: GREEN Phase Wave 1 (Core Implementation)               │
│   - Launch 3 implementation agents in parallel                   │
│   - VHS infrastructure (6h)                                      │
│   - Accessibility core (8h)                                      │
│   - Visual polish core (6h)                                      │
│   - Tests starting to PASS                                       │
│                                                                   │
│ Milestone: Core features implemented ✓                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   WEEK 2: GREEN (Waves 2-3) → REFACTOR           │
├─────────────────────────────────────────────────────────────────┤
│ Mon-Tue: GREEN Phase Wave 2 (Integration)                        │
│   - Launch 2 agents in parallel (depends on Wave 1)              │
│   - CI/CD integration (4h)                                       │
│   - Enhanced error recovery (6h)                                 │
│                                                                   │
│ Wed-Thu: GREEN Phase Wave 3 (Polish & Docs)                      │
│   - Launch 2 agents in parallel (depends on Waves 1-2)           │
│   - Documentation integration (4h)                               │
│   - Test alignment (2h)                                          │
│   - All tests PASSING (GREEN phase complete)                     │
│                                                                   │
│ Fri: REFACTOR Phase (Reviews)                                    │
│   - Launch 3 review agents in parallel (after 70% impl)          │
│   - Security review (2h)                                         │
│   - UX optimization (3h)                                         │
│   - Performance & polish (3h)                                    │
│                                                                   │
│ Milestone: All reviews passed, production-ready ✓                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        WEEK 3: COMMIT & LAUNCH                   │
├─────────────────────────────────────────────────────────────────┤
│ Mon: Final validation                                            │
│   - Full test suite (477+ tests, 100% passing)                   │
│   - Accessibility audit                                          │
│   - Performance benchmarks                                       │
│   - Security scan                                                │
│                                                                   │
│ Tue: Documentation polish                                        │
│   - README.md final review                                       │
│   - Demo GIFs optimized                                          │
│   - Installation guide tested                                    │
│                                                                   │
│ Wed: Pre-release testing                                         │
│   - Beta user testing (5+ users)                                 │
│   - Cross-platform validation (macOS, Linux, Windows)            │
│   - Screen reader testing (VoiceOver, NVDA)                      │
│                                                                   │
│ Thu: COMMIT Phase                                                │
│   - Create feature branch PR                                     │
│   - Code review                                                  │
│   - Merge to main                                                │
│                                                                   │
│ Fri: Release                                                     │
│   - Tag release (v0.2.0 - Phase 3)                               │
│   - Deploy documentation                                         │
│   - Announce launch                                              │
│                                                                   │
│ Milestone: Phase 3 released to production ✓                      │
└─────────────────────────────────────────────────────────────────┘
```

### Go/No-Go Criteria

**Week 1 Gate:**
- [ ] All RED phase tests written and failing
- [ ] Wave 1 core features implemented
- [ ] Tests starting to pass (50%+ green)
- [ ] No critical blockers identified

**Week 2 Gate:**
- [ ] All GREEN phase features complete
- [ ] All 477+ tests passing (100%)
- [ ] CI/CD workflow functional
- [ ] All review agents completed

**Week 3 Gate (Production Release):**
- [ ] WCAG 2.1 AA compliance verified (100%)
- [ ] All demos generated and <2MB
- [ ] Zero critical bugs
- [ ] Documentation complete and accurate
- [ ] Cross-platform testing passed
- [ ] Security scan clean

---

## Documentation Plan

### Files to Create

1. **`demo/README.md`** - VHS demo generation guide
   - VHS installation instructions (macOS, Linux, Windows)
   - How to regenerate demos locally
   - How to add new demo scenarios
   - Troubleshooting VHS issues

2. **`.tape` files** (5 total)
   - `demo/quick-start.tape` (30s overview)
   - `demo/fuzzy-search.tape` (typo tolerance)
   - `demo/multi-select.tape` (batch operations)
   - `demo/categories.tape` (filtering)
   - `demo/help-system.tape` (? modal)

3. **`.github/workflows/vhs-demos.yml`** - CI automation
   - VHS installation on Ubuntu
   - Demo generation on TUI changes
   - Artifact upload
   - Auto-commit to main branch

### Files to Update

1. **`README.md`**
   - Add "What Does It Look Like?" section (line 3)
   - Embed `quick-start.gif` above fold
   - Add feature-specific GIFs in Features section
   - Update Quick Start with visual reference

2. **`docs/PHASE_2_FEATURES.md`**
   - Add GIF to each feature section
   - Update workflows with visual steps

3. **`CLAUDE.md`**
   - Add VHS installation to development setup
   - Document demo regeneration workflow
   - Add `make demos` to common tasks

4. **`Makefile`** (create if missing)
   - `demos` target (generate all)
   - `demo-<name>` targets (individual demos)
   - `demos-clean` (remove output)

5. **`.gitignore`**
   - Add `demo/output/*.gif` for local dev
   - Committed demos tracked separately

---

## Rollback & Contingency Plans

### Rollback Strategy

**If Phase 3 has critical issues:**

1. **Immediate Rollback** (<1 hour)
   ```bash
   # Revert to Phase 2
   git revert <phase3-merge-commit>
   git push origin main
   ```

2. **Communication** (<2 hours)
   - GitHub issue: "Phase 3 rolled back due to [issue]"
   - Update README with notice
   - Revert demo GIFs to Phase 2 state

3. **Fix & Re-release** (<1 week)
   - Fix critical issue in hotfix branch
   - Full test suite + manual QA
   - Release Phase 3.1 with fix

### Contingency Plans

**Scenario 1: VHS CI integration fails**
- **Trigger:** Demo workflow doesn't work in GitHub Actions
- **Contingency:**
  - Generate demos locally and commit manually
  - Document local generation process
  - Fix CI in Phase 3.1 (not a blocker)

**Scenario 2: GIF file sizes exceed 2MB**
- **Trigger:** GitHub renders GIFs slowly
- **Contingency:**
  - Optimize with gifsicle (`--lossy=80 -O3`)
  - Reduce demo duration (30s → 20s)
  - Lower resolution (1200x800 → 1000x600)

**Scenario 3: Accessibility testing reveals major issues**
- **Trigger:** WCAG compliance < 90%
- **Contingency:**
  - Defer non-critical accessibility features to Phase 3.1
  - Focus on P0 issues (screen reader, keyboard traps)
  - Document known gaps with remediation plan

**Scenario 4: Test refactoring breaks functionality**
- **Trigger:** >5 tests fail after refactoring
- **Contingency:**
  - Keep old tests alongside new behavior-focused tests
  - Gradually migrate, validate each change
  - Accept 99% pass rate if regressions minor

---

## Phase 4 Considerations (Out of Scope)

Items explicitly deferred to Phase 4:

- [ ] Social media preview image (1200x630px PNG)
- [ ] GitHub Pages with interactive demo selector
- [ ] Multiple language versions of demos
- [ ] Video tutorials (longer-form content)
- [ ] Advanced demos (error handling, edge cases)
- [ ] Performance regression testing automation
- [ ] Homebrew formula (distribution)

---

## Sign-off & Approval

**Planning Status:** ✅ COMPLETE
**Implementation Readiness:** ✅ READY TO CODE
**Risk Level:** LOW-MEDIUM (manageable risks, clear mitigations)
**Confidence Level:** HIGH (90% - based on Phase 2 success)

**Next Phase:** CODE (EPCC Workflow)

**Estimated Timeline:**
- Optimistic: 15 hours (maximum parallelism)
- Realistic: 20 hours (with some sequential dependencies)
- Conservative: 30 hours (with unforeseen issues)

**Parallel Agent Strategy:**
- RED Phase: 4 agents (2 hours)
- GREEN Wave 1: 3 agents (3 days)
- GREEN Wave 2: 2 agents (2 days)
- GREEN Wave 3: 2 agents (2 days)
- REFACTOR: 3 agents (3-5 days)

**Expected Speedup:** 3-4x vs sequential (based on Phase 2 metrics)

---

**Document Version:** 1.0
**Last Updated:** October 5, 2025
**Author:** Claude Code AI Assistant
**Status:** Ready for Implementation

**Planning Phase Complete** ✅
**Proceed to CODE Phase with /epcc-code** →
