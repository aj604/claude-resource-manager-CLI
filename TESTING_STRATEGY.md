# Claude Resource Manager CLI - Testing Strategy

**Document Version:** 1.0.0
**Date:** October 4, 2025
**Role:** QualityGuard - Senior QA Engineer
**Status:** PLANNING ONLY - No Implementation

---

## Executive Summary

This testing strategy provides a comprehensive quality assurance framework for the Claude Resource Manager CLI, a greenfield Go application with complex components including TUI interactions, dependency graphs, file I/O, and GitHub API integration. The strategy emphasizes early testing through TDD, strong unit test coverage, and targeted integration testing for critical paths.

**Key Testing Challenges:**
- TUI interaction testing (Bubble Tea framework)
- Dependency graph edge cases (cycles, deep nesting, diamond dependencies)
- File system mocking across platforms (macOS, Linux, Windows)
- GitHub API mocking for catalog sync
- Cross-platform compatibility validation
- Performance benchmarking (<10ms startup, <1ms search)
- Scale testing (331 resources scaling to 10,000+)

**Strategic Approach:**
- Test-Driven Development (TDD) from day 1 (greenfield advantage)
- 70% unit / 25% integration / 5% E2E test pyramid
- Component-level coverage targets: 85-95%
- Automated performance benchmarks in CI/CD
- Platform-specific test matrices
- Mock-heavy approach for external dependencies

---

## 1. Test Pyramid Distribution

### 1.1 Overall Test Distribution

```
         /\
        /  \  5%     E2E Tests (Critical User Workflows)
       /----\        - Full TUI navigation flows
      /      \       - End-to-end installation workflows
     / 25%    \      - Cross-platform smoke tests
    /----------\
   /            \    Integration Tests (Component Interactions)
  /              \   - Catalog loader + dependency resolver
 /      70%       \  - Installer + file system operations
/------------------\ - TUI components + business logic

                     Unit Tests (Isolated Components)
                     - Pure functions and business logic
                     - Data structures and algorithms
                     - Edge cases and error handling
```

**Rationale:**
- **70% Unit Tests:** Go's excellent testing stdlib makes unit testing fast and easy. Pure functions (dependency resolver, categorizer, parsers) are ideal for comprehensive unit coverage
- **25% Integration Tests:** Critical for validating component boundaries (catalog → resolver → installer pipeline)
- **5% E2E Tests:** Expensive to maintain, brittle in TUI context. Focus on 3-5 critical user journeys only

### 1.2 Test Count Targets

```yaml
Total Test Target: 500-600 tests

By Layer:
  Unit:        350-420 tests (70%)
  Integration: 125-150 tests (25%)
  E2E:         25-30 tests   (5%)

By Component:
  Catalog Loader:      80-100 tests
  Dependency Resolver: 100-120 tests
  Category Engine:     60-80 tests
  Installer:           80-100 tests
  TUI Components:      60-80 tests
  CLI Commands:        40-50 tests
  Utilities:           30-40 tests
  Integration:         125-150 tests
  E2E:                 25-30 tests
```

---

## 2. Test Scenarios by Component

### 2.1 Catalog Loader (`internal/registry/loader.go`)

**Coverage Target:** 90%

#### Unit Tests (60 tests)

**Happy Path (12 tests):**
```yaml
Test_LoadMainIndex_Success:
  Input: Valid index.yaml with 331 resources
  Expected: Loaded index with correct counts by type

Test_LoadTypeIndex_Agents_Success:
  Input: Valid agents/index.yaml
  Expected: All 181 agent metadata objects loaded

Test_LoadResourceMetadata_Single_Success:
  Input: Valid resource YAML with all fields
  Expected: Resource struct fully populated

Test_LoadResourceMetadata_MinimalFields:
  Input: YAML with only required fields
  Expected: Defaults applied for optional fields

Test_ParseYAML_AllResourceTypes:
  For each: agents, commands, hooks, templates, mcps
  Expected: Type-specific fields parsed correctly

Test_BuildResourceIndex_HashMap:
  Input: 331 resources
  Expected: O(1) lookup by ID

Test_BuildCategoryTrie_PrefixTree:
  Input: Resources with prefix patterns
  Expected: Navigable tree structure
```

**Error Handling (18 tests):**
```yaml
Test_LoadMainIndex_FileNotFound:
  Expected: Descriptive error "index.yaml not found at path X"

Test_LoadMainIndex_MalformedYAML:
  Input: Invalid YAML syntax
  Expected: Parse error with line number

Test_LoadMainIndex_MissingRequiredField:
  For each required field (id, type, name)
  Expected: Validation error with field name

Test_LoadResourceMetadata_InvalidType:
  Input: type: "invalid"
  Expected: Error listing valid types

Test_LoadResourceMetadata_EmptyID:
  Expected: Validation error

Test_LoadResourceMetadata_DuplicateID:
  Expected: Error with conflicting resource IDs

Test_LoadCatalog_PartialFailure:
  Input: 10 resources, 2 malformed
  Expected: Load 8 valid, log 2 errors, continue

Test_LoadCatalog_PermissionDenied:
  Input: Catalog directory without read permissions
  Expected: Clear permission error message

Test_LoadCatalog_EmptyCatalog:
  Expected: Warning logged, empty index returned
```

**Edge Cases (15 tests):**
```yaml
Test_LoadResourceMetadata_UnicodeInFields:
  Input: Resource with emoji, Chinese characters
  Expected: Correctly preserved

Test_LoadResourceMetadata_VeryLongDescription:
  Input: 10,000 character description
  Expected: No truncation, handled gracefully

Test_LoadResourceMetadata_SpecialCharsInID:
  Input: ID with hyphens, underscores, numbers
  Expected: Valid

Test_LoadCatalog_MaxResources:
  Input: 10,000 resources
  Expected: Loads within memory limits (<500MB)

Test_LoadCatalog_DeepNestedPaths:
  Input: Resources 10 directories deep
  Expected: All loaded correctly

Test_LoadResourceMetadata_MixedLineEndings:
  Input: YAML with \n, \r\n, \r
  Expected: Parsed correctly

Test_LoadResourceMetadata_TrailingWhitespace:
  Expected: Trimmed automatically

Test_ParseDependencies_EmptyArray:
  Expected: Empty dependency list

Test_ParseDependencies_SingleDep:
  Expected: One dependency

Test_ParseDependencies_MultipleDeps:
  Expected: All dependencies preserved

Test_ParseMetadata_CustomFields:
  Input: Resource with unknown fields
  Expected: Preserved in metadata map

Test_LoadCatalog_ConcurrentAccess:
  Input: Multiple goroutines loading catalog
  Expected: Thread-safe, no race conditions

Test_LoadIndex_CachedReload:
  Expected: Cache invalidation works

Test_LoadCatalog_SymlinkedDirectory:
  Input: Catalog path is symlink
  Expected: Follows symlink, loads correctly

Test_LoadCatalog_RelativeVsAbsolutePaths:
  Expected: Both path types work
```

**Performance Benchmarks (15 tests):**
```yaml
Benchmark_LoadMainIndex:
  Target: <10ms for index.yaml

Benchmark_LoadTypeIndex_Agents:
  Target: <20ms for 181 agents index

Benchmark_LoadAllResourceMetadata:
  Target: <200ms for 331 resources (cold)
  Target: <50ms (warm cache)

Benchmark_LoadCatalog_10K_Resources:
  Target: <2s for 10,000 resources

Benchmark_BuildResourceIndex_HashMap:
  Target: <100ms for 331 resources

Benchmark_LookupByID:
  Target: <1ms (O(1) hash lookup)

Benchmark_MemoryUsage_331Resources:
  Target: <50MB total memory

Benchmark_MemoryUsage_10KResources:
  Target: <500MB total memory

Benchmark_ConcurrentLoads:
  Input: 10 concurrent catalog loads
  Target: No memory leaks, <500ms total

Benchmark_ParseYAML_ComplexResource:
  Target: <1ms per resource

Benchmark_ParseYAML_MinimalResource:
  Target: <0.5ms per resource
```

---

### 2.2 Dependency Resolver (`internal/installer/dependency.go`)

**Coverage Target:** 95% (critical business logic)

#### Unit Tests (90 tests)

**Core Algorithm (25 tests):**
```yaml
Test_ResolveDependencies_NoDeps:
  Input: Resource with empty dependencies
  Expected: [resource] (single item)

Test_ResolveDependencies_SingleLevel:
  Input: A → B
  Expected: [B, A] (topological order)

Test_ResolveDependencies_TwoLevels:
  Input: A → B → C
  Expected: [C, B, A]

Test_ResolveDependencies_Diamond:
  Input: A → B, A → C, B → D, C → D
  Expected: [D, B, C, A] or [D, C, B, A] (both valid)

Test_ResolveDependencies_MultipleDeps:
  Input: A → [B, C, D]
  Expected: [B, C, D, A] (order preserves insertion)

Test_ResolveDependencies_DeepNesting:
  Input: A → B → C → D → E → F (6 levels)
  Expected: [F, E, D, C, B, A]

Test_ResolveDependencies_Wide:
  Input: A → [B1, B2, ..., B20] (20 siblings)
  Expected: All B* before A

Test_ResolveDependencies_Complex:
  Input: 50 resources, mixed depths, shared deps
  Expected: Valid topological order

Test_TopologicalSort_StableOrder:
  Input: Same graph, multiple runs
  Expected: Deterministic output

Test_TopologicalSort_Kahn:
  Verify: Kahn's algorithm implementation correct

Test_TopologicalSort_DFS:
  Verify: DFS-based algorithm (alternative) correct

Test_BuildDependencyGraph_Adjacency:
  Expected: Correct adjacency list representation

Test_BuildDependencyGraph_InDegrees:
  Expected: Correct in-degree counts

Test_DetectCycles_None:
  Input: Acyclic graph
  Expected: No cycles detected

Test_ResolveTransitiveDeps_Auto:
  Input: A → B, user requests A
  Expected: Install plan includes B
```

**Cycle Detection (20 tests):**
```yaml
Test_DetectCycles_SelfReference:
  Input: A → A
  Expected: Error "circular dependency: A → A"

Test_DetectCycles_TwoNode:
  Input: A → B → A
  Expected: Error with cycle path "A → B → A"

Test_DetectCycles_ThreeNode:
  Input: A → B → C → A
  Expected: Cycle detected

Test_DetectCycles_DiamondWithCycle:
  Input: A → B → D, A → C → D, D → A
  Expected: Cycle "A → B → D → A"

Test_DetectCycles_MultipleCycles:
  Input: A → B → A, C → D → C
  Expected: All cycles reported

Test_DetectCycles_LongCycle:
  Input: A → B → ... → Z → A (26 nodes)
  Expected: Cycle detected

Test_DetectCycles_DeepButAcyclic:
  Input: 100 nodes in chain (no cycle)
  Expected: No cycle detected

Test_DetectCycles_ComplexGraph:
  Input: 50 nodes, 1 hidden cycle
  Expected: Cycle found and reported

Test_ValidateDependencies_MissingDep:
  Input: A → B, but B not in catalog
  Expected: Error "dependency 'B' not found"

Test_ValidateDependencies_CrossTypeOK:
  Input: agent → command (cross-type dep)
  Expected: Allowed

Test_ValidateDependencies_InvalidID:
  Input: Dependency ID with invalid characters
  Expected: Validation error
```

**Error Handling (15 tests):**
```yaml
Test_ResolveDependencies_EmptyCatalog:
  Expected: Error "catalog is empty"

Test_ResolveDependencies_NullInput:
  Expected: Error handled gracefully

Test_ResolveDependencies_MalformedDepsField:
  Input: dependencies: "string" (should be array)
  Expected: Parse error

Test_ResolveDependencies_TooManyDeps:
  Input: Resource with 1000 dependencies
  Expected: Warning or limit enforcement

Test_ResolveDependencies_RecursionLimit:
  Input: 1000-level deep chain
  Expected: Stack overflow prevention

Test_ResolveMultipleResources_PartialFailure:
  Input: [A (valid), B (missing deps)]
  Expected: Install A, error for B

Test_CircularDep_UserFriendlyError:
  Expected: Error message shows full cycle path

Test_CircularDep_SuggestResolution:
  Expected: Error suggests removing specific dep
```

**Edge Cases (30 tests):**
```yaml
Test_ResolveDependencies_EmptyDepsArray:
  Input: dependencies: []
  Expected: No dependencies

Test_ResolveDependencies_NullDepsArray:
  Input: dependencies: null
  Expected: Treated as empty

Test_ResolveDependencies_DuplicateDeps:
  Input: dependencies: [B, B, B]
  Expected: Deduped to [B]

Test_ResolveDependencies_SameDepTwice:
  Input: A → B, C → B (B appears twice)
  Expected: B installed once

Test_ResolveDependencies_OptionalDeps:
  Input: Resource with optionalDependencies
  Expected: Best-effort install, no error if missing

Test_ResolveDependencies_ConflictingVersions:
  Input: A → B@1.0, C → B@2.0
  Expected: Error or version resolution strategy

Test_ResolveDependencies_WildcardDep:
  Input: dependencies: ["mcp-*"]
  Expected: Resolves to all matching IDs

Test_ResolveDependencies_CategoryDep:
  Input: Depend on category "database-*"
  Expected: All resources in category

Test_ResolveDependencies_OptionalNotFound:
  Input: optionalDependencies: [missing]
  Expected: Warning logged, install continues
```

**Performance Benchmarks:**
```yaml
Benchmark_ResolveDependencies_Shallow_5Deps:
  Target: <1ms

Benchmark_ResolveDependencies_Deep_10Levels:
  Target: <5ms

Benchmark_ResolveDependencies_Wide_100Deps:
  Target: <10ms

Benchmark_ResolveDependencies_Complex_331Resources:
  Target: <50ms

Benchmark_ResolveDependencies_Massive_10KResources:
  Target: <500ms

Benchmark_DetectCycles_LargeCyclicGraph:
  Input: 1000 nodes with cycle
  Target: <100ms

Benchmark_MemoryUsage_DependencyGraph:
  Input: 331 resources with deps
  Target: <10MB
```

---

### 2.3 Category Engine (`internal/registry/categorizer.go`)

**Coverage Target:** 90%

#### Unit Tests (70 tests)

**Prefix Parsing (25 tests):**
```yaml
Test_ParsePrefix_SingleHyphen:
  Input: "database-postgres"
  Expected: category="database", subcategory="postgres"

Test_ParsePrefix_DoubleHyphen:
  Input: "mcp-dev-team-architect"
  Expected: category="mcp-dev-team", subcategory="architect"

Test_ParsePrefix_NoHyphen:
  Input: "standalone"
  Expected: category="uncategorized", subcategory=""

Test_ParsePrefix_TrailingHyphen:
  Input: "database-"
  Expected: category="database", subcategory=""

Test_ParsePrefix_LeadingHyphen:
  Input: "-orphan"
  Expected: category="uncategorized"

Test_ParsePrefix_MultipleHyphens:
  Input: "ai-specialists-prompt-engineer"
  Expected: category="ai-specialists", subcategory="prompt-engineer"

Test_ExtractCategory_AllAgentPrefixes:
  For each: obsidian-*, development-*, programming-*
  Expected: Correct category extracted

Test_ExtractCategory_AllMCPPrefixes:
  For each: devtools-*, browser_automation-*, deepgraph-*
  Expected: Correct category
```

**Tree Building (20 tests):**
```yaml
Test_BuildCategoryTree_Flat:
  Input: All resources same category
  Expected: Single root node with 331 children

Test_BuildCategoryTree_TwoLevel:
  Input: 30 categories, 2-10 resources each
  Expected: 30 category nodes

Test_BuildCategoryTree_ThreeLevel:
  Input: Categories with subcategories
  Expected: Nested tree structure

Test_BuildCategoryTree_Empty:
  Input: No resources
  Expected: Empty tree

Test_BuildCategoryTree_SingleResource:
  Expected: Root → Category → Resource

Test_NavigateTree_ToCategory:
  Input: Navigate to "database"
  Expected: All database-* resources

Test_NavigateTree_ToSubcategory:
  Input: Navigate to "mcp-dev-team"
  Expected: All mcp-dev-team-* resources

Test_NavigateTree_BreadcrumbTrail:
  Expected: Path history maintained

Test_CountResourcesByCategory:
  Expected: Matches actual counts

Test_ListCategories_Sorted:
  Expected: Alphabetical order
```

**Auto-Categorization (25 tests):**
```yaml
Test_AutoCategorize_NewResource_WithPrefix:
  Input: Resource "database-mysql"
  Expected: category="database"

Test_AutoCategorize_NewResource_NoPrefix:
  Input: Resource "standalone-tool"
  Expected: category="uncategorized"

Test_AutoCategorize_InferFromDescription:
  Input: description contains "database"
  Expected: Suggested category="database"

Test_AutoCategorize_InferFromTags:
  Input: tags: [database, sql]
  Expected: Suggested category="database"

Test_AutoCategorize_ConflictingSignals:
  Input: prefix="web", tags=[database]
  Expected: Prefix wins

Test_RenameCategory_UpdateAllResources:
  Input: Rename "database" → "data-stores"
  Expected: All database-* resources updated

Test_MergeCategories:
  Input: Merge "ai" into "ai-specialists"
  Expected: Tree restructured

Test_SplitCategory:
  Input: Split "development" into "frontend", "backend"
  Expected: Resources redistributed

Test_MoveResource_BetweenCategories:
  Expected: Tree updated correctly
```

---

### 2.4 Installer (`internal/installer/install.go`)

**Coverage Target:** 90%

#### Unit Tests (80 tests)

**File Operations (30 tests):**
```yaml
Test_Install_SingleResource_Success:
  Input: Valid resource, writable directory
  Expected: File created at install_path

Test_Install_WithDependencies:
  Input: Resource A → B
  Expected: B installed before A

Test_Install_CreateDirectories:
  Input: install_path with nested dirs
  Expected: Directories created recursively

Test_Install_OverwriteExisting_Prompt:
  Input: File already exists
  Expected: User prompted for overwrite

Test_Install_OverwriteExisting_Force:
  Input: --force flag
  Expected: Overwrites without prompt

Test_Install_BackupExisting:
  Input: --backup flag
  Expected: Existing file renamed to .bak

Test_Install_DryRun:
  Input: --dry-run flag
  Expected: No files written, plan printed

Test_Uninstall_SingleResource:
  Expected: File removed

Test_Uninstall_WithDependents:
  Input: Uninstall B, but A depends on B
  Expected: Warning or error

Test_Uninstall_Force_IgnoreDependents:
  Expected: Removes even with dependents

Test_SetPermissions_Unix:
  Expected: chmod 644 for files

Test_SetPermissions_Windows:
  Expected: Appropriate Windows ACLs

Test_Install_SymlinkSupport:
  Input: install_path is symlink
  Expected: Follows symlink

Test_Install_RelativePath:
  Input: install_path="./agents/foo"
  Expected: Resolved to absolute path

Test_Install_HomeDirectory:
  Input: install_path="~/.claude/agents/foo"
  Expected: ~ expanded correctly

Test_Install_VerifyChecksum:
  Input: Resource with SHA256 checksum
  Expected: Downloaded content verified

Test_Install_CorruptedDownload:
  Input: Download fails checksum
  Expected: Error, file not installed

Test_Install_AtomicWrite:
  Expected: Temp file → rename (atomic)

Test_Install_CleanupOnFailure:
  Input: Install fails mid-process
  Expected: Partial files removed
```

**Network Operations (20 tests):**
```yaml
Test_Download_Success:
  Input: Valid GitHub raw URL
  Expected: Content downloaded

Test_Download_404NotFound:
  Expected: Clear error message

Test_Download_NetworkTimeout:
  Input: Slow/hanging server
  Expected: Timeout after 30s

Test_Download_RetryOn5xx:
  Input: 503 Service Unavailable
  Expected: 3 retries with backoff

Test_Download_LargeFile:
  Input: 10MB resource file
  Expected: Progress indicator, success

Test_Download_RateLimited:
  Input: GitHub rate limit hit
  Expected: Wait and retry

Test_Download_InvalidURL:
  Expected: Validation error

Test_Download_HTTPSRequired:
  Input: http:// URL
  Expected: Warning or error

Test_Download_Concurrent:
  Input: Install 10 resources in parallel
  Expected: Connection pooling, no errors

Test_Download_PartialContent:
  Input: Resume partial download
  Expected: Range requests used
```

**State Management (30 tests):**
```yaml
Test_TrackInstalled_Metadata:
  Expected: Installed resources tracked

Test_TrackInstalled_Version:
  Expected: Version number stored

Test_TrackInstalled_InstallDate:
  Expected: Timestamp recorded

Test_ListInstalled:
  Expected: All installed resources shown

Test_SearchInstalled_ByName:
  Expected: Fuzzy search works

Test_SearchInstalled_ByType:
  Input: type=agent
  Expected: Only agents shown

Test_UpdateResource_NewerVersion:
  Expected: Update offered

Test_UpdateResource_AlreadyLatest:
  Expected: "Already up to date"

Test_UpdateAll:
  Expected: All outdated resources updated

Test_Rollback_ToPreviousVersion:
  Expected: Previous version restored

Test_InstallState_Persistence:
  Expected: State survives CLI restart

Test_InstallState_Corruption:
  Input: Corrupted state file
  Expected: Rebuilt from filesystem

Test_InstallState_Migration:
  Input: Old state format
  Expected: Migrated to new format
```

---

### 2.5 TUI Components (`internal/tui/browser.go`)

**Coverage Target:** 75% (TUI harder to test)

#### Unit Tests (60 tests)

**Bubble Tea Model Tests (25 tests):**
```yaml
Test_BrowserModel_Init:
  Expected: Model initialized with defaults

Test_BrowserModel_UpdateMsg_KeyDown:
  Input: tea.KeyMsg{Type: tea.KeyDown}
  Expected: Selection moves down

Test_BrowserModel_UpdateMsg_KeyUp:
  Expected: Selection moves up

Test_BrowserModel_UpdateMsg_KeyEnter:
  Expected: Item selected/expanded

Test_BrowserModel_UpdateMsg_KeyEsc:
  Expected: Navigate back/cancel

Test_BrowserModel_UpdateMsg_SearchMode:
  Input: '/' key
  Expected: Search input activated

Test_BrowserModel_UpdateMsg_FilterResults:
  Input: Type "database"
  Expected: Filtered list shown

Test_BrowserModel_View_RenderList:
  Expected: Valid string output

Test_BrowserModel_View_Pagination:
  Input: 100 items, viewport shows 20
  Expected: Scroll indicator shown

Test_BrowserModel_View_SelectedHighlight:
  Expected: Selected item has cursor

Test_BrowserModel_Navigation_CategoryTree:
  Expected: Navigate into/out of categories

Test_BrowserModel_Navigation_Breadcrumbs:
  Expected: Path shown correctly

Test_BrowserModel_Selection_Install:
  Input: Select resource, press 'i'
  Expected: Install command triggered

Test_BrowserModel_Selection_ViewDetails:
  Input: Press 'd'
  Expected: Detail view shown

Test_BrowserModel_MultiSelect:
  Input: Press space on 3 items
  Expected: 3 items marked
```

**Rendering Tests (20 tests):**
```yaml
Test_RenderResourceList_Empty:
  Expected: "No resources found" message

Test_RenderResourceList_Single:
  Expected: Single item formatted

Test_RenderResourceList_Multiple:
  Expected: All items with consistent spacing

Test_RenderResourceList_LongNames:
  Input: 100-char resource name
  Expected: Truncated with ellipsis

Test_RenderResourceDetail_AllFields:
  Expected: All metadata shown

Test_RenderResourceDetail_MissingFields:
  Expected: Optional fields omitted gracefully

Test_RenderDependencyTree_Visual:
  Expected: ASCII tree diagram

Test_RenderInstallPlan_OrderedList:
  Expected: Install order shown

Test_RenderProgress_Indicator:
  Expected: Spinner/progress bar

Test_RenderError_UserFriendly:
  Expected: Error formatted clearly

Test_ColorScheme_Default:
  Expected: Consistent colors applied

Test_ColorScheme_NoColor:
  Input: NO_COLOR env var
  Expected: Plain text output

Test_Layout_WindowResize:
  Input: Terminal resize event
  Expected: Layout adjusts

Test_Layout_SmallTerminal:
  Input: 40x20 terminal
  Expected: Degraded layout, no crash
```

**Interaction Tests (15 tests):**
```yaml
Test_KeyBinding_Help:
  Input: '?' key
  Expected: Help screen shown

Test_KeyBinding_Quit:
  Input: 'q' key
  Expected: Exit program

Test_KeyBinding_Search:
  Input: '/' key
  Expected: Search mode activated

Test_KeyBinding_Install:
  Input: 'i' key
  Expected: Installation starts

Test_KeyBinding_ViewDeps:
  Input: 'D' key
  Expected: Dependency tree shown

Test_Search_Incremental:
  Input: Type "dat" → "data"
  Expected: Results update live

Test_Search_CaseSensitive:
  Expected: Case-insensitive by default

Test_Search_Fuzzy:
  Input: "dbpg"
  Expected: Matches "database-postgres"

Test_Navigation_VimKeys:
  Input: j/k/h/l
  Expected: Vim-style navigation

Test_Navigation_ArrowKeys:
  Expected: Arrow keys work
```

---

### 2.6 CLI Commands (`cmd/*.go`)

**Coverage Target:** 85%

#### Unit Tests (40 tests)

**Command Parsing (15 tests):**
```yaml
Test_ListCommand_NoArgs:
  Input: crm list
  Expected: All resources listed

Test_ListCommand_TypeFilter:
  Input: crm list --type=agent
  Expected: Only agents listed

Test_ListCommand_CategoryFilter:
  Input: crm list --category=database
  Expected: Only database resources

Test_SearchCommand_Query:
  Input: crm search "postgres"
  Expected: Matching resources

Test_SearchCommand_FuzzyMatch:
  Input: crm search "dbpg"
  Expected: Fuzzy matches included

Test_InstallCommand_SingleResource:
  Input: crm install database-postgres
  Expected: Resource installed

Test_InstallCommand_MultipleResources:
  Input: crm install res1 res2 res3
  Expected: All installed

Test_InstallCommand_WithDeps:
  Input: crm install --with-deps res1
  Expected: Dependencies auto-installed

Test_InstallCommand_DryRun:
  Input: crm install --dry-run res1
  Expected: Plan printed, no install

Test_BrowseCommand_Interactive:
  Input: crm browse
  Expected: TUI launched

Test_InfoCommand_ResourceID:
  Input: crm info database-postgres
  Expected: Detailed info shown

Test_InfoCommand_InvalidID:
  Input: crm info nonexistent
  Expected: Error "resource not found"

Test_UpdateCommand_All:
  Input: crm update
  Expected: All resources updated

Test_UninstallCommand:
  Input: crm uninstall res1
  Expected: Resource removed

Test_HelpCommand:
  Input: crm --help
  Expected: Help text shown
```

**Flag Parsing (15 tests):**
```yaml
Test_GlobalFlag_Verbose:
  Input: crm --verbose list
  Expected: Debug output enabled

Test_GlobalFlag_Quiet:
  Input: crm --quiet install res1
  Expected: Minimal output

Test_GlobalFlag_NoColor:
  Input: crm --no-color list
  Expected: Plain text output

Test_GlobalFlag_ConfigPath:
  Input: crm --config=/custom/path list
  Expected: Custom config loaded

Test_Flag_Type_ValidValue:
  Input: --type=agent
  Expected: Valid

Test_Flag_Type_InvalidValue:
  Input: --type=invalid
  Expected: Error with valid types listed

Test_Flag_Force_Boolean:
  Input: --force
  Expected: force=true

Test_Flag_OutputFormat_JSON:
  Input: --output=json
  Expected: JSON output

Test_Flag_OutputFormat_YAML:
  Input: --output=yaml
  Expected: YAML output

Test_Flag_OutputFormat_Table:
  Input: --output=table
  Expected: Table output

Test_ShortFlag_Equivalence:
  Input: -v vs --verbose
  Expected: Both work identically

Test_CombinedShortFlags:
  Input: -vf (verbose + force)
  Expected: Both flags set

Test_FlagConflicts:
  Input: --quiet --verbose
  Expected: Error or quiet wins

Test_RequiredFlag_Missing:
  Input: Command requiring --type, not provided
  Expected: Error message

Test_UnknownFlag:
  Input: --unknown-flag
  Expected: Error suggestion
```

**Output Formatting (10 tests):**
```yaml
Test_OutputJSON_SingleResource:
  Expected: Valid JSON object

Test_OutputJSON_MultipleResources:
  Expected: Valid JSON array

Test_OutputYAML_Valid:
  Expected: Valid YAML syntax

Test_OutputTable_Alignment:
  Expected: Columns aligned

Test_OutputTable_Truncation:
  Input: Long values
  Expected: Truncated with ellipsis

Test_OutputTable_EmptyResult:
  Expected: "No results" message

Test_OutputHuman_Colorized:
  Expected: ANSI colors applied

Test_OutputHuman_Plain:
  Input: NO_COLOR env var
  Expected: No ANSI codes

Test_ErrorOutput_Stderr:
  Expected: Errors written to stderr

Test_SuccessOutput_Stdout:
  Expected: Results written to stdout
```

---

## 3. Integration Tests

**Coverage Target:** 25% of total tests

### 3.1 Component Integration Tests (100 tests)

**Catalog → Dependency → Installer Pipeline (30 tests):**
```yaml
Test_FullInstallFlow_WithDeps:
  Steps:
    1. Load catalog
    2. Resolve dependencies for resource A
    3. Download resources in order
    4. Install to filesystem
    5. Update install state
  Expected: All steps succeed, state consistent

Test_FullInstallFlow_MissingDep:
  Expected: Error before any installation

Test_FullInstallFlow_NetworkFailure:
  Input: Network drops during download
  Expected: Graceful failure, cleanup

Test_FullInstallFlow_DiskFull:
  Input: Disk full during install
  Expected: Error, rollback

Test_SearchAndInstall:
  Steps:
    1. Search for "database"
    2. Select "database-postgres"
    3. Resolve deps
    4. Install
  Expected: End-to-end success

Test_BrowseAndInstall_TUI:
  Steps:
    1. Launch browser
    2. Navigate to category
    3. Select resource
    4. Trigger install
  Expected: Installation completes

Test_UpdateWorkflow:
  Steps:
    1. Install resource v1.0
    2. Catalog updated to v1.1
    3. Run update command
    4. Verify v1.1 installed
  Expected: Update successful

Test_UninstallWithDependents:
  Steps:
    1. Install A → B
    2. Uninstall B
  Expected: Warning shown, user confirms

Test_InstallAll_Category:
  Input: Install all "database-*" resources
  Expected: All installed in correct order

Test_ConcurrentInstalls:
  Input: Install 5 resources in parallel
  Expected: No conflicts, all succeed
```

**TUI → Business Logic Integration (25 tests):**
```yaml
Test_TUI_LoadCatalog:
  Expected: Catalog loaded and displayed

Test_TUI_NavigateCategories:
  Steps: Navigate tree, verify data matches

Test_TUI_Search_Filter:
  Input: Type search query
  Expected: Results match business logic

Test_TUI_InstallFromBrowser:
  Expected: Installer invoked correctly

Test_TUI_ViewDependencies:
  Expected: Dep tree matches resolver output

Test_TUI_MultiSelect_Install:
  Steps: Select 3 resources, install
  Expected: All 3 installed

Test_TUI_HandleErrors:
  Input: Trigger error condition
  Expected: Error shown in UI, recoverable
```

**File System Integration (20 tests):**
```yaml
Test_Install_ReadWritePermissions:
  Platform: All (macOS, Linux, Windows)
  Expected: Correct permissions set

Test_Install_PathSeparators:
  Platform: Windows
  Expected: Backslashes handled correctly

Test_Install_SymlinkedInstallPath:
  Expected: Symlink followed

Test_Install_ReadOnlyDestination:
  Expected: Clear permission error

Test_Install_LongPaths:
  Platform: Windows
  Input: >260 char path
  Expected: Handled or clear error

Test_Uninstall_RemoveEmptyDirs:
  Expected: Empty parent dirs removed

Test_FileWatcher_DetectChanges:
  Input: User manually edits installed file
  Expected: Detected, state updated
```

**GitHub API Integration (15 tests):**
```yaml
Test_Sync_FetchFromGitHub:
  Expected: Real API call succeeds

Test_Sync_RateLimit:
  Expected: Respects rate limits

Test_Sync_Authentication:
  Input: GITHUB_TOKEN env var
  Expected: Authenticated requests

Test_Sync_Unauthenticated:
  Expected: Anonymous rate limit (60/hour)

Test_Download_ValidURL:
  Expected: Resource downloaded

Test_Download_404:
  Expected: Clear error

Test_Download_LargeFile:
  Input: >5MB resource
  Expected: Success or streaming
```

**Cross-Platform Integration (10 tests):**
```yaml
Test_CrossPlatform_PathHandling:
  Platforms: macOS, Linux, Windows
  Expected: Paths normalized correctly

Test_CrossPlatform_LineEndings:
  Expected: \n, \r\n handled

Test_CrossPlatform_Permissions:
  Expected: Platform-appropriate perms

Test_CrossPlatform_HomeDirectory:
  Expected: ~ expanded correctly on all platforms
```

---

### 3.2 System Integration Tests (25 tests)

**End-to-End User Workflows:**
```yaml
Test_E2E_NewUser_InstallFirstResource:
  Steps:
    1. Fresh system (no config)
    2. crm browse
    3. Navigate, select, install
    4. Verify file on disk
  Expected: First-time setup works

Test_E2E_PowerUser_InstallWithDeps:
  Steps:
    1. crm search "agent-team"
    2. crm install --with-deps agent-team-lead
    3. Verify all deps installed
  Expected: Complex workflow succeeds

Test_E2E_Update_AllResources:
  Steps:
    1. Install 10 resources
    2. Catalog updated (mock)
    3. crm update
    4. Verify all updated
  Expected: Batch update works

Test_E2E_Uninstall_CleanState:
  Steps:
    1. Install resources
    2. Uninstall all
    3. Verify no orphaned files
  Expected: Clean uninstall

Test_E2E_ErrorRecovery_NetworkFailure:
  Steps:
    1. Start install
    2. Simulate network failure
    3. Retry
  Expected: Recovers gracefully
```

---

## 4. Test Data Requirements

### 4.1 Test Fixtures

**Catalog Fixtures:**
```yaml
Fixtures Needed:
  minimal_catalog/
    - Single resource, no dependencies
    - Use for basic load tests

  standard_catalog/
    - 50 resources across all types
    - 10 with dependencies (2-3 levels deep)
    - Realistic prefix distribution
    - Use for integration tests

  large_catalog/
    - 1,000 resources
    - Complex dependency graphs
    - Use for performance tests

  edge_case_catalog/
    - Unicode characters in fields
    - Very long descriptions
    - Special characters in IDs
    - Empty optional fields
    - Use for edge case tests

  invalid_catalog/
    - Malformed YAML
    - Missing required fields
    - Invalid types
    - Use for error handling tests

Directory Structure:
tests/fixtures/
  ├── catalogs/
  │   ├── minimal/
  │   │   ├── index.yaml
  │   │   └── agents/
  │   │       └── simple-agent.yaml
  │   ├── standard/
  │   │   ├── index.yaml
  │   │   ├── agents/ (20 files)
  │   │   ├── commands/ (10 files)
  │   │   ├── hooks/ (10 files)
  │   │   └── mcps/ (10 files)
  │   ├── large/
  │   │   └── (1000 generated resources)
  │   ├── edge_cases/
  │   └── invalid/
  ├── resources/
  │   └── (Sample resource content files)
  └── configs/
      └── (Sample config files)
```

**Resource Fixtures:**
```yaml
Sample Resources:
  agent_no_deps.yaml:
    - Simple agent, no dependencies

  agent_with_deps.yaml:
    - Agent depending on command + hook

  agent_deep_deps.yaml:
    - 5-level dependency chain

  agent_diamond_deps.yaml:
    - Diamond dependency pattern

  mcp_complex.yaml:
    - MCP with optional dependencies

  hook_minimal.yaml:
    - Minimal required fields only

  command_unicode.yaml:
    - Unicode in description/name
```

### 4.2 Mock Data Generators

**Catalog Builder:**
```go
// tests/helpers/catalog_builder.go
package helpers

type CatalogBuilder struct {
    resources []Resource
}

func NewCatalogBuilder() *CatalogBuilder

func (cb *CatalogBuilder) AddAgent(id, name string) *CatalogBuilder
func (cb *CatalogBuilder) AddDependency(from, to string) *CatalogBuilder
func (cb *CatalogBuilder) AddCategory(id, category string) *CatalogBuilder
func (cb *CatalogBuilder) Build() *Catalog
func (cb *CatalogBuilder) WriteToDisk(path string) error

// Usage:
catalog := NewCatalogBuilder().
    AddAgent("a1", "Agent 1").
    AddAgent("a2", "Agent 2").
    AddDependency("a1", "a2").
    Build()
```

**Resource Builder:**
```go
type ResourceBuilder struct {
    resource Resource
}

func NewResourceBuilder() *ResourceBuilder
func (rb *ResourceBuilder) WithID(id string) *ResourceBuilder
func (rb *ResourceBuilder) WithType(t ResourceType) *ResourceBuilder
func (rb *ResourceBuilder) WithDependencies(deps ...string) *ResourceBuilder
func (rb *ResourceBuilder) Build() Resource

// Usage:
resource := NewResourceBuilder().
    WithID("test-agent").
    WithType(TypeAgent).
    WithDependencies("dep1", "dep2").
    Build()
```

**Dependency Graph Builder:**
```go
type GraphBuilder struct {
    nodes []string
    edges map[string][]string
}

func NewGraphBuilder() *GraphBuilder
func (gb *GraphBuilder) AddNode(id string) *GraphBuilder
func (gb *GraphBuilder) AddEdge(from, to string) *GraphBuilder
func (gb *GraphBuilder) WithCycle(nodes ...string) *GraphBuilder
func (gb *GraphBuilder) Build() *DependencyGraph

// Usage:
graph := NewGraphBuilder().
    AddNode("A").
    AddNode("B").
    AddEdge("A", "B").
    Build()
```

### 4.3 Mock Services

**File System Mock:**
```go
type MockFileSystem struct {
    files map[string][]byte
    perms map[string]os.FileMode
    errors map[string]error
}

func (m *MockFileSystem) ReadFile(path string) ([]byte, error)
func (m *MockFileSystem) WriteFile(path string, data []byte, perm os.FileMode) error
func (m *MockFileSystem) MkdirAll(path string, perm os.FileMode) error
func (m *MockFileSystem) Remove(path string) error
func (m *MockFileSystem) Stat(path string) (os.FileInfo, error)

// Helpers:
func (m *MockFileSystem) ShouldFailOn(path string, err error)
func (m *MockFileSystem) AssertWritten(t *testing.T, path string)
func (m *MockFileSystem) AssertNotWritten(t *testing.T, path string)
```

**HTTP Client Mock:**
```go
type MockHTTPClient struct {
    responses map[string]*http.Response
    calls []string
}

func (m *MockHTTPClient) Get(url string) (*http.Response, error)
func (m *MockHTTPClient) Do(req *http.Request) (*http.Response, error)

// Helpers:
func (m *MockHTTPClient) MockResponse(url string, status int, body string)
func (m *MockHTTPClient) MockError(url string, err error)
func (m *MockHTTPClient) AssertCalled(t *testing.T, url string)
func (m *MockHTTPClient) CallCount() int
```

**GitHub API Mock:**
```go
type MockGitHubClient struct {
    files map[string]string  // path -> content
    rateLimitRemaining int
}

func (m *MockGitHubClient) GetFileContent(repo, path string) (string, error)
func (m *MockGitHubClient) ListDirectory(repo, path string) ([]string, error)
func (m *MockGitHubClient) GetRateLimit() (*github.RateLimits, error)

// Helpers:
func (m *MockGitHubClient) MockFile(path, content string)
func (m *MockGitHubClient) MockRateLimit(remaining int)
func (m *MockGitHubClient) SimulateRateLimitExceeded()
```

---

## 5. Quality Metrics & Coverage Targets

### 5.1 Coverage Targets by Component

```yaml
Component Coverage Targets:

Critical Business Logic (95%+):
  - internal/installer/dependency.go (95%)
  - internal/installer/install.go (90%)
  - internal/registry/categorizer.go (90%)

Core Infrastructure (90%+):
  - internal/registry/loader.go (90%)
  - internal/models/resource.go (90%)
  - internal/config/config.go (90%)

CLI Layer (85%+):
  - cmd/install.go (85%)
  - cmd/list.go (85%)
  - cmd/search.go (85%)
  - cmd/browse.go (80%)  # TUI harder to test

TUI Components (75%+):
  - internal/tui/browser.go (75%)
  - internal/tui/detail.go (75%)
  - internal/tui/search.go (75%)

Utilities (90%+):
  - internal/util/path.go (90%)
  - internal/util/download.go (90%)

Overall Target: >85%
```

### 5.2 Code Quality Metrics

**Cyclomatic Complexity:**
```yaml
Target Limits:
  Per Function: <15 (ideal: <10)
  Per File: <50
  Per Package: <200

High-Risk Functions (Require Extra Tests):
  - DependencyResolver.Resolve() (complexity: 18)
  - Categorizer.BuildTree() (complexity: 15)
  - Installer.InstallWithDeps() (complexity: 20)
```

**Test Quality Metrics:**
```yaml
Test Assertions:
  Minimum: 1 assertion per test
  Target: 2-3 assertions per test
  Max: 5 (split if more)

Test Naming:
  Pattern: Test_[Component]_[Scenario]_[Expected]
  Examples:
    - Test_Loader_LoadIndex_Success
    - Test_Resolver_CircularDep_Error
    - Test_Installer_DiskFull_Rollback

Test Independence:
  - No shared state between tests
  - Each test runs in isolation
  - Parallel execution safe

Test Speed:
  Unit Tests: <10ms each (target: <5ms)
  Integration Tests: <100ms each
  E2E Tests: <5s each
  Full Suite: <2 minutes
```

### 5.3 Mutation Testing

**Mutation Testing Strategy:**
```yaml
Tool: go-mutesting or go-carpet

Target Mutation Score: >75%

Focus Areas:
  - Conditional logic (if/else branches)
  - Loop conditions
  - Boolean operators
  - Arithmetic operators
  - Boundary values

Run Frequency:
  - Weekly in CI
  - Before major releases
  - After significant refactors

Mutation Operators:
  - Conditionals (&&, ||, !)
  - Arithmetic (+, -, *, /)
  - Relational (<, >, <=, >=, ==, !=)
  - Remove statements
  - Negate conditionals
```

---

## 6. Performance Benchmarks

### 6.1 Performance Benchmark Suite

**Startup Performance:**
```yaml
Benchmark_CLI_ColdStart:
  Target: <10ms
  Metric: Time from exec to first output

Benchmark_CLI_ColdStart_LargeCatalog:
  Input: 10,000 resources
  Target: <50ms

Benchmark_TUI_Launch:
  Target: <100ms
  Metric: Time to render first frame
```

**Catalog Loading:**
```yaml
Benchmark_LoadIndex_331Resources:
  Target: <10ms

Benchmark_LoadAllMetadata_331Resources:
  Target: <200ms (cold)
  Target: <50ms (cached)

Benchmark_LoadCatalog_10KResources:
  Target: <2s (cold)
  Target: <500ms (cached)
```

**Search Performance:**
```yaml
Benchmark_Search_ExactMatch:
  Target: <1ms

Benchmark_Search_FuzzyMatch_331Resources:
  Target: <5ms

Benchmark_Search_FuzzyMatch_10KResources:
  Target: <50ms

Benchmark_Search_Incremental:
  Input: Type character by character
  Target: <10ms per keystroke
```

**Dependency Resolution:**
```yaml
Benchmark_ResolveDeps_Shallow_5Deps:
  Target: <1ms

Benchmark_ResolveDeps_Deep_10Levels:
  Target: <5ms

Benchmark_ResolveDeps_Wide_100Deps:
  Target: <10ms

Benchmark_ResolveDeps_Complex_331Resources:
  Target: <50ms

Benchmark_ResolveDeps_Massive_10KResources:
  Target: <500ms

Benchmark_DetectCycle_1000NodeGraph:
  Target: <100ms
```

**Installation Performance:**
```yaml
Benchmark_Install_SingleResource_LocalFile:
  Target: <50ms

Benchmark_Install_SingleResource_Network:
  Target: <500ms (depends on network)

Benchmark_Install_WithDeps_5Resources:
  Target: <2s

Benchmark_Install_Concurrent_10Resources:
  Target: <3s

Benchmark_Uninstall_SingleResource:
  Target: <10ms
```

**Memory Benchmarks:**
```yaml
Benchmark_MemoryUsage_331Resources:
  Target: <50MB

Benchmark_MemoryUsage_10KResources:
  Target: <500MB

Benchmark_MemoryUsage_TUI_Idle:
  Target: <20MB

Benchmark_MemoryUsage_NoLeaks:
  Test: Run for 1000 operations
  Expected: No growth beyond initial
```

### 6.2 Performance Regression Testing

**CI Performance Gates:**
```yaml
GitHub Actions Workflow:
  - name: performance-benchmarks
    steps:
      - Run benchmark suite
      - Compare to baseline (main branch)
      - Fail if >10% regression
      - Post results as PR comment

Baseline Storage:
  - Store benchmark results in git
  - File: benchmarks/baseline.json
  - Update on each release

Performance Dashboard:
  - Track metrics over time
  - Graph startup time, search speed, memory usage
  - Alert on regressions
```

---

## 7. Testing Tools & Frameworks

### 7.1 Core Testing Stack

**Go Testing Stdlib:**
```yaml
Package: testing
Usage: All unit tests
Features:
  - Table-driven tests
  - Subtests (t.Run)
  - Benchmarks
  - Test coverage
  - Parallel tests

Example:
  func TestLoader_LoadIndex(t *testing.T) {
      tests := []struct {
          name string
          input string
          want Index
          wantErr bool
      }{
          // test cases...
      }
      for _, tt := range tests {
          t.Run(tt.name, func(t *testing.T) {
              // test logic
          })
      }
  }
```

**Testify (Assertions & Mocks):**
```yaml
Package: github.com/stretchr/testify
Modules:
  - assert: Fluent assertions
  - require: Assertions that halt test
  - mock: Mock objects
  - suite: Test suites

Usage:
  import "github.com/stretchr/testify/assert"

  assert.Equal(t, expected, actual)
  assert.NoError(t, err)
  assert.Len(t, list, 10)
  require.NotNil(t, obj)  // Halts if fails
```

**Bubble Tea Test Utilities:**
```yaml
Package: github.com/charmbracelet/bubbletea/teatest
Usage: TUI component testing

Features:
  - Send keyboard events
  - Capture output
  - Test model updates
  - Verify rendering

Example:
  tm := teatest.NewTestModel(t, model)
  tm.Send(tea.KeyMsg{Type: tea.KeyDown})
  tm.WaitFinished(t, teatest.WithFinalTimeout(time.Second))
  output := tm.FinalOutput(t)
  assert.Contains(t, output, "Expected text")
```

**Go-VCR (HTTP Recording):**
```yaml
Package: gopkg.in/dnaeon/go-vcr.v3
Usage: Record/replay HTTP interactions

Features:
  - Record real API responses
  - Replay in tests (deterministic)
  - No network in CI

Example:
  r, _ := recorder.New("fixtures/github_api")
  defer r.Stop()

  client := &http.Client{Transport: r}
  // Make requests, responses recorded
```

**Afero (Virtual File System):**
```yaml
Package: github.com/spf13/afero
Usage: Mock file system operations

Features:
  - In-memory filesystem
  - Mock permissions, errors
  - Cross-platform testing

Example:
  fs := afero.NewMemMapFs()
  afero.WriteFile(fs, "test.yaml", []byte("data"), 0644)
  data, _ := afero.ReadFile(fs, "test.yaml")
```

### 7.2 Code Quality Tools

**golangci-lint:**
```yaml
Package: golangci-lint
Usage: Static analysis & linting

Enabled Linters:
  - gofmt: Code formatting
  - govet: Suspicious constructs
  - errcheck: Unchecked errors
  - staticcheck: Bugs, perf issues
  - gosec: Security issues
  - gocyclo: Cyclomatic complexity
  - goconst: Repeated strings
  - misspell: Spelling errors

Config: .golangci.yml
```

**go test -race:**
```yaml
Usage: Race condition detection

Command: go test -race ./...

Target: Zero race conditions
Frequency: Every CI run
```

**go test -cover:**
```yaml
Usage: Code coverage reporting

Commands:
  go test -cover ./...
  go test -coverprofile=coverage.out ./...
  go tool cover -html=coverage.out

Target: >85% overall coverage
```

**Benchmark Comparison:**
```yaml
Package: golang.org/x/perf/cmd/benchstat
Usage: Compare benchmark results

Workflow:
  1. Run benchmarks on main: go test -bench=. > old.txt
  2. Run benchmarks on branch: go test -bench=. > new.txt
  3. Compare: benchstat old.txt new.txt
  4. Fail CI if >10% regression
```

### 7.3 CI/CD Integration Tools

**GitHub Actions Workflows:**
```yaml
.github/workflows/test.yml:
  name: Tests
  on: [push, pull_request]

  jobs:
    unit-tests:
      runs-on: ubuntu-latest
      steps:
        - Checkout
        - Setup Go 1.22
        - go mod download
        - go test -v -race -coverprofile=coverage.out ./...
        - Upload coverage to Codecov

    integration-tests:
      runs-on: ubuntu-latest
      steps:
        - Checkout
        - Setup Go 1.22
        - go test -v -tags=integration ./...

    e2e-tests:
      strategy:
        matrix:
          os: [ubuntu-latest, macos-latest, windows-latest]
      runs-on: ${{ matrix.os }}
      steps:
        - Checkout
        - Setup Go 1.22
        - Build binary
        - Run E2E test suite

    benchmarks:
      runs-on: ubuntu-latest
      steps:
        - Checkout
        - Setup Go 1.22
        - go test -bench=. -benchmem ./...
        - Compare to baseline
        - Fail if regression >10%
```

**Codecov Integration:**
```yaml
Tool: codecov.io
Upload: codecov/codecov-action@v3

Features:
  - Coverage visualization
  - PR comments with diff
  - Trend tracking
  - Fail CI if coverage drops >2%
```

**Test Timing Analysis:**
```yaml
Tool: go test -json + custom parser
Purpose: Identify slow tests

Workflow:
  go test -json ./... | tee test-results.json
  Parse JSON, identify tests >100ms
  Create GitHub issue for optimization
```

---

## 8. CI/CD Test Pipeline

### 8.1 Pipeline Stages

```yaml
Pipeline: GitHub Actions

Stages:
  1. Code Quality (Fast Feedback)
     - golangci-lint
     - gofmt check
     - go vet
     Duration: ~30s
     Fail Fast: Yes

  2. Unit Tests (Parallel)
     - Run all unit tests with -race
     - Coverage report
     Duration: ~2m
     Fail Fast: Yes

  3. Integration Tests
     - Component integration tests
     - File system tests
     - Mock network tests
     Duration: ~3m
     Fail Fast: No (collect all failures)

  4. E2E Tests (Matrix)
     - macOS, Linux, Windows
     - Critical user workflows
     Duration: ~5m per platform
     Fail Fast: No

  5. Performance Benchmarks
     - Run benchmark suite
     - Compare to baseline
     - Report results
     Duration: ~2m
     Fail Fast: Only if >10% regression

  6. Security Scans
     - gosec
     - go list -m all | nancy (dependency check)
     Duration: ~1m
     Fail Fast: Critical vulnerabilities only

Total Pipeline Duration: ~15-20 minutes
```

### 8.2 Test Execution Strategy

**Pull Request Checks:**
```yaml
Required Checks:
  - Code Quality
  - Unit Tests (coverage >85%)
  - Integration Tests (all pass)
  - E2E Tests (Ubuntu only for speed)

Optional Checks (for visibility):
  - E2E Tests (macOS, Windows)
  - Performance Benchmarks

Merge Requirement: All required checks pass
```

**Main Branch (Post-Merge):**
```yaml
Full Test Suite:
  - All unit tests
  - All integration tests
  - Full E2E matrix (3 platforms)
  - Performance benchmarks (stored as baseline)
  - Security scans

Failure Handling:
  - Revert commit if critical failure
  - Create GitHub issue
  - Notify team via Slack
```

**Nightly Tests:**
```yaml
Schedule: Daily at 2 AM UTC

Extended Tests:
  - Mutation testing
  - Long-running performance tests
  - Stress tests (10K resources)
  - Memory leak detection
  - Fuzzing (if applicable)

Reporting:
  - Email summary to team
  - Create issues for failures
  - Update performance dashboard
```

**Release Tests:**
```yaml
Pre-Release Checklist:
  - Full test suite passes
  - All platforms tested
  - Performance benchmarks meet targets
  - Security scans clean
  - Manual smoke tests
  - Documentation reviewed

Release Gates:
  - Zero critical bugs
  - Coverage >85%
  - All E2E tests pass
  - Performance within 5% of targets
```

### 8.3 Test Environment Management

**Test Data Management:**
```yaml
Fixtures:
  - Checked into git (tests/fixtures/)
  - Small files (<100KB)
  - Version controlled
  - Documented in README

Large Test Data:
  - Stored in S3/GitHub Releases
  - Downloaded in CI if needed
  - Cached between runs

Generated Data:
  - Use seed for reproducibility
  - Document generation logic
  - Check in examples
```

**Test Isolation:**
```yaml
File System:
  - Each test gets temp directory
  - Cleaned up automatically (t.TempDir())

Parallel Tests:
  - Mark parallel-safe tests: t.Parallel()
  - Shared resources: Use locks or avoid

Database/State:
  - Use in-memory stores
  - Reset between tests
  - No shared global state
```

**Environment Variables:**
```yaml
CI Environment:
  GO_ENV=test
  CI=true
  NO_COLOR=true  # Disable ANSI colors

Local Development:
  - Use .env.test (not committed)
  - Document required vars in README
  - Provide .env.example
```

---

## 9. Edge Cases & Failure Modes

### 9.1 Dependency Resolution Edge Cases

**Circular Dependencies:**
```yaml
Test Cases:
  - Self-reference (A → A)
  - Two-node cycle (A → B → A)
  - Three-node cycle (A → B → C → A)
  - Long cycle (A → B → ... → Z → A)
  - Multiple disjoint cycles
  - Cycle with diamond pattern

Expected Behavior:
  - Detect cycle before any installation
  - Report full cycle path to user
  - Suggest breaking the cycle
  - Exit with error code 1
```

**Missing Dependencies:**
```yaml
Test Cases:
  - Direct dependency not found
  - Transitive dependency missing
  - Optional dependency missing
  - Wildcard dependency matches zero resources

Expected Behavior:
  - Direct/transitive: Error, halt installation
  - Optional: Warning, continue
  - Wildcard zero matches: Warning
```

**Deep Nesting:**
```yaml
Test Cases:
  - 10 levels deep
  - 100 levels deep
  - 1000 levels deep (stack overflow risk)

Expected Behavior:
  - <100 levels: Works normally
  - >100 levels: Stack-safe algorithm (use queue)
  - Warn if >50 levels (likely misconfiguration)
```

**Diamond Dependencies:**
```yaml
Test Cases:
  - Simple diamond (A → B, A → C, B → D, C → D)
  - Multiple diamonds
  - Nested diamonds
  - Diamond with conflicting versions

Expected Behavior:
  - Shared dependency installed once
  - Correct topological order maintained
  - Version conflicts detected and reported
```

### 9.2 File System Edge Cases

**Path Issues:**
```yaml
Test Cases:
  - Very long paths (>260 chars on Windows)
  - Paths with Unicode characters
  - Paths with spaces
  - Paths with special chars (!, @, #)
  - Relative paths (./path)
  - Absolute paths
  - Symlinks
  - Hardlinks

Expected Behavior:
  - Long paths: Use \\?\ prefix on Windows or error
  - Unicode: Supported
  - Spaces: Quoted correctly
  - Relative: Resolved to absolute
  - Symlinks: Followed
```

**Permission Issues:**
```yaml
Test Cases:
  - Read-only destination directory
  - No write permission to parent
  - No read permission to source
  - Permission denied during write

Expected Behavior:
  - Check permissions before starting
  - Clear error message with path
  - Suggest chmod/chown command
```

**Disk Space:**
```yaml
Test Cases:
  - Disk full during download
  - Disk full during write
  - Quota exceeded

Expected Behavior:
  - Check available space before install
  - Cleanup partial downloads on failure
  - Clear error message
```

**File Conflicts:**
```yaml
Test Cases:
  - File already exists
  - Directory exists at file path
  - File is open/locked (Windows)

Expected Behavior:
  - Prompt user for overwrite (unless --force)
  - Create backup if --backup
  - Error if directory at file path
  - Wait and retry if file locked
```

### 9.3 Network Edge Cases

**GitHub API:**
```yaml
Test Cases:
  - 404 Not Found
  - 403 Rate Limit Exceeded
  - 500 Server Error
  - Timeout
  - Connection refused
  - DNS failure
  - SSL certificate error

Expected Behavior:
  - 404: Clear error "resource not found"
  - 403 Rate Limit: Wait and retry or use auth token
  - 5xx: Retry with exponential backoff (3 attempts)
  - Timeout: Fail after 30s, clear message
  - Connection refused: Check network, firewall
  - DNS failure: Check internet connection
  - SSL error: Verify system certificates
```

**Download Failures:**
```yaml
Test Cases:
  - Partial download (connection dropped)
  - Corrupted content
  - Checksum mismatch
  - Content-Length mismatch

Expected Behavior:
  - Partial: Resume download if server supports
  - Corrupted: Retry download
  - Checksum fail: Error, don't install
  - Length mismatch: Retry
```

### 9.4 TUI Edge Cases

**Terminal Issues:**
```yaml
Test Cases:
  - Very small terminal (40x10)
  - Very large terminal (300x100)
  - Terminal resize during operation
  - No TTY (non-interactive mode)
  - TERM=dumb

Expected Behavior:
  - Small: Degrade gracefully, minimal UI
  - Large: Use available space
  - Resize: Reflow layout
  - No TTY: Fall back to plain text output
  - TERM=dumb: No colors, simple output
```

**Input Edge Cases:**
```yaml
Test Cases:
  - Rapid keypresses
  - Mouse input (if supported)
  - Paste large text into search
  - Special keys (F1-F12, etc.)

Expected Behavior:
  - Rapid keys: Debounce or queue
  - Mouse: Ignore if not handled
  - Large paste: Truncate or warn
  - Special keys: Document or ignore
```

### 9.5 Cross-Platform Edge Cases

**Windows-Specific:**
```yaml
Test Cases:
  - Backslash path separators
  - Drive letters (C:\)
  - UNC paths (\\server\share)
  - Long path support (>260 chars)
  - Line endings (\r\n)
  - Case-insensitive filesystem

Expected Behavior:
  - Always use filepath.Join()
  - Support drive letters
  - Support UNC paths
  - Enable long path support
  - Handle both \n and \r\n
  - Case-insensitive ID lookup
```

**macOS-Specific:**
```yaml
Test Cases:
  - Gatekeeper (unsigned binary)
  - Case-insensitive APFS
  - Extended attributes
  - .DS_Store files

Expected Behavior:
  - Warn about code signing
  - Case-insensitive where needed
  - Preserve xattrs if present
  - Ignore .DS_Store
```

**Linux-Specific:**
```yaml
Test Cases:
  - Different distributions (Ubuntu, Fedora, Arch)
  - Different package managers
  - SELinux/AppArmor
  - Case-sensitive filesystem

Expected Behavior:
  - Work on all major distros
  - Provide install instructions for each
  - Respect SELinux contexts
  - Case-sensitive operations
```

---

## 10. Test Maintenance & Evolution

### 10.1 Test Naming Conventions

**Pattern:**
```
Test_[Component]_[Scenario]_[ExpectedOutcome]
```

**Examples:**
```go
Test_Loader_LoadIndex_Success
Test_Loader_LoadIndex_FileNotFound
Test_Resolver_CircularDependency_ReturnsError
Test_Installer_DiskFull_RollsBack
Test_TUI_KeyDown_MovesSelectionDown
Test_CLI_InvalidFlag_ShowsError
```

**Benchmark Naming:**
```
Benchmark_[Component]_[Operation]_[InputSize]
```

**Examples:**
```go
Benchmark_Loader_LoadCatalog_331Resources
Benchmark_Search_FuzzyMatch_10KResources
Benchmark_Resolver_ResolveDeps_DeepChain
```

### 10.2 Test Documentation

**Test File Headers:**
```go
// Package installer_test contains tests for the installer component.
//
// Test Coverage:
// - File operations (create, overwrite, permissions)
// - Dependency resolution integration
// - Error handling (disk full, permission denied)
// - Rollback on failure
//
// Test Fixtures:
// - tests/fixtures/catalogs/standard/
// - tests/fixtures/resources/
//
// Mocks:
// - MockFileSystem for file operations
// - MockHTTPClient for downloads
```

**Test Function Documentation:**
```go
// Test_Installer_DiskFull_RollsBack verifies that when installation fails
// due to disk full error, all partially installed files are cleaned up.
//
// Setup:
//   - Mock filesystem with 100KB free space
//   - Resource requiring 200KB
//
// Expected:
//   - Installation fails with clear error
//   - No partial files left on disk
//   - Install state not updated
func Test_Installer_DiskFull_RollsBack(t *testing.T) {
    // ...
}
```

### 10.3 Test Refactoring Strategy

**When to Refactor Tests:**
```yaml
Triggers:
  - Test is flaky (fails intermittently)
  - Test is too slow (>100ms for unit test)
  - Test is hard to understand
  - Test has duplicate setup code
  - Test tests multiple things (split it)

Refactoring Techniques:
  - Extract test helpers
  - Use table-driven tests
  - Create custom assertions
  - Use test fixtures
  - Introduce test builders
```

**Test Smells:**
```yaml
Red Flags:
  - Tests that sleep (time.Sleep)
  - Tests that rely on external services
  - Tests that depend on execution order
  - Tests with hard-coded timestamps
  - Tests with no assertions
  - Tests over 50 lines long

Solutions:
  - Replace sleep with channels/waitgroups
  - Mock external services
  - Ensure test independence
  - Use test clock or relative times
  - Add meaningful assertions
  - Split into multiple tests
```

### 10.4 Handling Test Failures

**Flaky Test Protocol:**
```yaml
1. Identify:
   - Run test 100 times: go test -count=100
   - Check CI failure patterns

2. Investigate:
   - Add verbose logging
   - Check for race conditions (-race)
   - Review timing assumptions
   - Check for external dependencies

3. Fix:
   - Eliminate timing dependencies
   - Add proper synchronization
   - Mock unpredictable inputs
   - Increase timeouts (last resort)

4. Verify:
   - Run 1000 times: go test -count=1000
   - Monitor in CI for 1 week
   - Mark as stable
```

**Test Failure Debugging:**
```yaml
Steps:
  1. Read the error message carefully
  2. Check test logs (t.Log output)
  3. Run with -v flag for verbose output
  4. Run single test: go test -run TestName
  5. Add debug prints
  6. Use delve debugger if needed
  7. Check for recent code changes
  8. Review test fixtures

Common Causes:
  - Incorrect test data
  - Missing mock setup
  - Race condition
  - Filesystem state
  - Timing issue
```

---

## 11. Special Testing Considerations

### 11.1 TDD Workflow (Greenfield Advantage)

**Red-Green-Refactor Cycle:**
```yaml
For Each Feature:
  1. RED - Write failing test:
     - Write test for desired behavior
     - Run test, verify it fails
     - Confirm failure reason is correct

  2. GREEN - Make it pass:
     - Write minimal code to pass test
     - Don't worry about perfection
     - Run test, verify it passes

  3. REFACTOR - Improve code:
     - Clean up implementation
     - Remove duplication
     - Improve naming
     - Run tests, verify still passing

Example - Dependency Resolver:
  1. Write Test_ResolveDependencies_SingleLevel
  2. Implement minimal resolver (hardcoded?)
  3. Test passes
  4. Add Test_ResolveDependencies_TwoLevels
  5. Implement general algorithm
  6. Both tests pass
  7. Refactor to clean up
  8. Continue...
```

**TDD Benefits for This Project:**
```yaml
Why TDD is Perfect Here:
  - Greenfield: No legacy code to work around
  - Complex logic: Dep resolution, categorization
  - Clear requirements: Spec is well-defined
  - Type safety: Go's compiler catches many errors
  - Fast feedback: Tests run in milliseconds

Components Most Suited for TDD:
  - Dependency resolver (complex algorithm)
  - Category engine (clear input/output)
  - Resource loader (edge cases)
  - CLI command parsing (many variations)
```

### 11.2 Property-Based Testing

**Candidates for Property Testing:**
```yaml
Dependency Resolver:
  Property: For any acyclic graph, topological sort produces valid order
  Tool: gopter or go-fuzz

  Test:
    Generate random acyclic graphs
    Run resolver
    Verify all dependencies come before dependents
    Verify no cycles introduced

Category Tree:
  Property: For any set of resources, tree contains all resources exactly once

  Test:
    Generate random resource lists
    Build category tree
    Verify count matches input
    Verify no duplicates

File Operations:
  Property: Install → Uninstall → Install produces same result

  Test:
    Generate random resource
    Install, uninstall, install again
    Verify file contents identical
    Verify state consistent
```

**Example with gopter:**
```go
import "github.com/leanovate/gopter"

func TestProperty_TopologicalSort(t *testing.T) {
    properties := gopter.NewProperties(nil)

    properties.Property("topological sort is correct",
        prop.ForAll(
            func(graph DependencyGraph) bool {
                order := Resolve(graph)
                return isValidTopologicalOrder(graph, order)
            },
            genAcyclicGraph(),
        ),
    )

    properties.TestingRun(t)
}
```

### 11.3 Fuzzing Strategy

**Go 1.18+ Native Fuzzing:**
```go
// Fuzz test for YAML parsing
func FuzzParseResource(f *testing.F) {
    // Seed corpus
    f.Add([]byte("id: test\ntype: agent\nname: Test"))

    f.Fuzz(func(t *testing.T, data []byte) {
        var resource Resource
        err := yaml.Unmarshal(data, &resource)

        // Should never panic
        if err != nil {
            return  // Invalid YAML is ok
        }

        // If parsed, validate fields
        if resource.ID != "" {
            assert.NotEmpty(t, resource.Type)
        }
    })
}
```

**Fuzz Targets:**
```yaml
High-Value Targets:
  - YAML parsing (ParseResource)
  - Dependency resolution (handle malformed graphs)
  - Category prefix parsing (handle any string)
  - CLI command parsing (handle any input)

Fuzzing Duration:
  - Local: 1 minute per target
  - CI: 5 minutes per target
  - Nightly: 1 hour per target

Crash Handling:
  - Any crash is critical bug
  - Add crash input to test corpus
  - Fix and re-fuzz
```

### 11.4 Security Testing

**Security Test Cases:**
```yaml
Path Traversal:
  Test_Install_PathTraversal_Blocked:
    Input: install_path="../../../etc/passwd"
    Expected: Error, installation blocked

Command Injection:
  Test_Download_CommandInjection_Sanitized:
    Input: URL with shell metacharacters
    Expected: Characters escaped or error

Arbitrary Code Execution:
  Test_ResourceContent_CodeExecution_SafelyHandled:
    Input: YAML with malicious content
    Expected: Content not evaluated, stored safely

Denial of Service:
  Test_DependencyResolution_DeepRecursion_Limited:
    Input: 10,000-level deep dependency chain
    Expected: Error or safe handling (no stack overflow)

Information Disclosure:
  Test_ErrorMessages_NoSensitiveInfo:
    Expected: Error messages don't leak paths, tokens
```

**Security Scanning in CI:**
```yaml
Tools:
  - gosec: Go security scanner
  - nancy: Dependency vulnerability scanner
  - trivy: Container scanning (if dockerized)

Workflow:
  - Run on every PR
  - Fail CI on HIGH/CRITICAL findings
  - Weekly full scan with report

Exclude False Positives:
  - Document in .gosec.json
  - Require code review to exclude
```

---

## 12. Test Execution Environments

### 12.1 Local Development

**Developer Workflow:**
```bash
# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Run specific package
go test ./internal/installer/...

# Run specific test
go test -run Test_Resolver_CircularDep ./internal/installer/

# Run tests in parallel
go test -parallel 4 ./...

# Run with race detection
go test -race ./...

# Watch mode (using entr or air)
find . -name '*.go' | entr -c go test ./...
```

**Pre-Commit Hooks:**
```bash
# .git/hooks/pre-commit

#!/bin/bash
echo "Running pre-commit checks..."

# Run tests
go test ./... || exit 1

# Run linter
golangci-lint run || exit 1

# Check formatting
gofmt -l . | grep . && exit 1

echo "All checks passed!"
```

### 12.2 CI/CD Environments

**GitHub Actions Matrix:**
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    go: ['1.22', '1.23']

runs-on: ${{ matrix.os }}
steps:
  - uses: actions/setup-go@v4
    with:
      go-version: ${{ matrix.go }}

  - run: go test ./...
```

**Platform-Specific Tests:**
```go
// +build windows

package installer_test

func TestInstaller_WindowsPaths(t *testing.T) {
    // Windows-specific test
}
```

```go
// +build linux darwin

package installer_test

func TestInstaller_UnixPermissions(t *testing.T) {
    // Unix-specific test
}
```

### 12.3 Test Isolation

**Temporary Directories:**
```go
func TestInstaller_CreateFile(t *testing.T) {
    // Go 1.15+ automatic cleanup
    tmpDir := t.TempDir()

    installPath := filepath.Join(tmpDir, "agents", "test.md")
    err := installer.Install(resource, installPath)

    assert.NoError(t, err)
    assert.FileExists(t, installPath)
}
```

**Parallel Test Safety:**
```go
func TestLoader_Parallel(t *testing.T) {
    t.Parallel()  // Safe to run in parallel

    // Each test gets own temp dir, no shared state
}

func TestGlobalConfig(t *testing.T) {
    // Don't mark parallel - modifies global state
}
```

---

## 13. Success Criteria & Release Gates

### 13.1 Quality Gates for Release

**v1.0 Release Requirements:**
```yaml
Code Coverage:
  - Overall: >85%
  - Core logic: >90%
  - TUI components: >75%

Test Execution:
  - All unit tests pass: 350+ tests
  - All integration tests pass: 125+ tests
  - All E2E tests pass (3 platforms): 25+ tests

Performance:
  - Startup: <10ms (met)
  - Search: <1ms exact, <5ms fuzzy (met)
  - Memory: <50MB for 331 resources (met)

Quality Metrics:
  - Zero critical bugs
  - Zero high-priority bugs
  - <5 medium-priority bugs
  - Cyclomatic complexity <15 per function

Security:
  - gosec: Zero HIGH/CRITICAL findings
  - nancy: Zero vulnerabilities in deps

Documentation:
  - All public APIs documented
  - User guide complete
  - CLI reference complete
```

### 13.2 Continuous Improvement

**Post-Release Testing:**
```yaml
Monitor:
  - Production error rates
  - Performance metrics
  - User-reported bugs

Iterate:
  - Add regression tests for bugs
  - Improve coverage of weak areas
  - Optimize slow tests
  - Update test data for new resources

Metrics to Track:
  - Test execution time trend
  - Flaky test rate
  - Code coverage trend
  - Bug escape rate (bugs found in prod)
```

---

## 14. Summary & Recommendations

### 14.1 Strategic Summary

**Testing Approach:**
- **Test-Driven Development** from day 1 (greenfield advantage)
- **70/25/5 test pyramid** (unit/integration/E2E)
- **Component-level coverage targets** (75-95%)
- **Performance benchmarks** integrated into CI
- **Cross-platform testing** via GitHub Actions matrix

**Key Strengths:**
- Go's excellent testing stdlib minimizes tooling complexity
- Greenfield project enables TDD best practices
- Well-defined requirements allow comprehensive test planning
- Performance targets are measurable and achievable

**Key Challenges:**
- TUI testing requires specialized approach (Bubble Tea test utils)
- Dependency graph edge cases need exhaustive coverage
- Cross-platform testing requires platform-specific matrices
- Performance benchmarks need baseline management

### 14.2 Immediate Next Steps

**Week 1: Test Infrastructure Setup**
1. Initialize test directory structure (`tests/fixtures/`, `tests/helpers/`)
2. Create test fixture catalogs (minimal, standard, large)
3. Set up GitHub Actions workflows (unit, integration, E2E)
4. Configure golangci-lint, coverage reporting
5. Write test helpers (CatalogBuilder, ResourceBuilder, mocks)

**Week 2-3: Core Component Testing (TDD)**
1. Catalog Loader: 80-100 tests (TDD)
2. Dependency Resolver: 100-120 tests (TDD)
3. Category Engine: 60-80 tests (TDD)
4. Integration tests for above components: 50 tests

**Week 4-6: CLI & TUI Testing**
1. Installer: 80-100 tests
2. TUI Components: 60-80 tests (with Bubble Tea test utils)
3. CLI Commands: 40-50 tests
4. E2E workflows: 25-30 tests

**Week 7-9: Performance & Polish**
1. Performance benchmarks: 50+ benchmarks
2. Cross-platform E2E tests
3. Security testing
4. Test documentation
5. Coverage gap analysis

### 14.3 Final Recommendations

**DO:**
- Start with TDD for all core business logic
- Write tests for edge cases early (cycles, deep nesting, etc.)
- Use table-driven tests for comprehensive coverage
- Mock external dependencies (filesystem, network)
- Maintain <2 minute full test suite execution time
- Track performance benchmarks as first-class metrics

**DON'T:**
- Skip TDD for "simple" components (leads to gaps)
- Rely on E2E tests for edge case coverage (too slow)
- Test implementation details (test behavior, not code)
- Allow flaky tests to persist (fix immediately)
- Sacrifice test clarity for cleverness

**MONITOR:**
- Test execution time (optimize slow tests)
- Coverage trends (prevent regression)
- Flaky test rate (should be 0%)
- Bug escape rate (bugs found in production)

---

## Appendix A: Test File Organization

**Recommended Structure:**
```
claude_resource_manager-CLI/
├── internal/
│   ├── registry/
│   │   ├── loader.go
│   │   ├── loader_test.go          (60 tests)
│   │   ├── categorizer.go
│   │   ├── categorizer_test.go     (70 tests)
│   │   └── loader_benchmark_test.go (15 benchmarks)
│   ├── installer/
│   │   ├── install.go
│   │   ├── install_test.go         (80 tests)
│   │   ├── dependency.go
│   │   ├── dependency_test.go      (90 tests)
│   │   └── dependency_benchmark_test.go (20 benchmarks)
│   └── tui/
│       ├── browser.go
│       ├── browser_test.go         (60 tests)
│       └── testutil.go             (Test helpers)
├── cmd/
│   ├── install.go
│   ├── install_test.go             (40 tests)
│   └── ...
├── tests/
│   ├── fixtures/
│   │   ├── catalogs/
│   │   │   ├── minimal/
│   │   │   ├── standard/
│   │   │   ├── large/
│   │   │   ├── edge_cases/
│   │   │   └── invalid/
│   │   ├── resources/
│   │   └── configs/
│   ├── helpers/
│   │   ├── catalog_builder.go
│   │   ├── resource_builder.go
│   │   ├── graph_builder.go
│   │   └── mocks.go
│   ├── integration/
│   │   ├── catalog_installer_test.go (50 tests)
│   │   ├── tui_integration_test.go   (25 tests)
│   │   └── filesystem_test.go        (20 tests)
│   └── e2e/
│       ├── install_workflow_test.go  (10 tests)
│       ├── update_workflow_test.go   (8 tests)
│       └── browse_workflow_test.go   (7 tests)
└── benchmarks/
    └── baseline.json                 (Stored baselines)
```

---

## Appendix B: Example Test Templates

**Unit Test Template:**
```go
package registry_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestLoader_LoadIndex_Success(t *testing.T) {
    // Arrange
    loader := NewLoader("tests/fixtures/catalogs/minimal")

    // Act
    index, err := loader.LoadIndex()

    // Assert
    assert.NoError(t, err)
    assert.NotNil(t, index)
    assert.Equal(t, 1, index.TotalResources)
}
```

**Table-Driven Test Template:**
```go
func TestCategorizer_ParsePrefix(t *testing.T) {
    tests := []struct {
        name          string
        input         string
        wantCategory  string
        wantSubcat    string
    }{
        {
            name:         "single hyphen",
            input:        "database-postgres",
            wantCategory: "database",
            wantSubcat:   "postgres",
        },
        {
            name:         "no hyphen",
            input:        "standalone",
            wantCategory: "uncategorized",
            wantSubcat:   "",
        },
        // More test cases...
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            cat, subcat := ParsePrefix(tt.input)
            assert.Equal(t, tt.wantCategory, cat)
            assert.Equal(t, tt.wantSubcat, subcat)
        })
    }
}
```

**Benchmark Template:**
```go
func BenchmarkLoader_LoadCatalog_331Resources(b *testing.B) {
    loader := NewLoader("tests/fixtures/catalogs/standard")

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        _, _ = loader.LoadCatalog()
    }
}
```

**Integration Test Template:**
```go
// +build integration

package integration_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestIntegration_FullInstallFlow(t *testing.T) {
    // Setup
    tmpDir := t.TempDir()
    catalog := loadTestCatalog(t)

    // Execute workflow
    resolver := NewResolver(catalog)
    plan, err := resolver.Resolve("test-resource")
    assert.NoError(t, err)

    installer := NewInstaller(tmpDir)
    err = installer.Execute(plan)
    assert.NoError(t, err)

    // Verify
    assert.FileExists(t, filepath.Join(tmpDir, "agents", "test-resource.md"))
}
```

---

**Document End**

This testing strategy provides a comprehensive framework for ensuring the quality, performance, and reliability of the Claude Resource Manager CLI. The strategy emphasizes early testing through TDD, strong unit test coverage, targeted integration testing, and automated performance validation.

Next steps: Begin implementation following the phased approach outlined in Section 14.2, starting with test infrastructure setup and progressing to TDD of core components.
