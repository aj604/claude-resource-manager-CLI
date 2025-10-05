# Claude Resource Manager CLI - Deep Exploration Findings

**Date:** October 4, 2025
**Exploration Type:** Deep (--deep flag)
**Focus Areas:** Dependency Management & Prefix-Based Categorization

---

## Executive Summary

After deep exploration of the existing claude_resource_manager implementation and the proposed CLI architecture, I've identified clear patterns and design opportunities for implementing:

1. **Automatic Prefix-Based Categorization** - Resources naturally organize into hierarchical categories based on ID prefixes
2. **Cross-Type Dependency Management** - A flexible dependency system supporting all resource types with automatic resolution

### Key Findings

- **331 total resources** across 5 types (181 agents, 18 commands, 64 hooks, 16 templates, 52 MCPs)
- **Clear prefix patterns** indicating natural categorization (e.g., `mcp-dev-team-*`, `ai-specialists-*`, `database-*`)
- **No existing dependency tracking** - this is a greenfield feature
- **Existing catalog format** uses YAML with standardized metadata structure
- **Current implementation** (Node.js) provides sync/catalog generation but no dependency resolution

---

## 1. Existing System Analysis

### 1.1 Current Architecture

```
claude_resource_manager/
├── registry/
│   ├── sources.yaml              # External repo definitions
│   └── catalog/                  # Generated resource catalog
│       ├── index.yaml           # Main index with counts
│       ├── agents/
│       │   ├── index.yaml       # Type-level index
│       │   └── *.yaml          # Individual resource metadata
│       ├── commands/
│       ├── hooks/
│       ├── templates/
│       └── mcps/
└── scripts/
    └── sync.js                   # GitHub API-based catalog generator
```

### 1.2 Current Resource Metadata Format

```yaml
id: ai-specialists-prompt-engineer
type: agent
name: prompt-engineer
description: Expert prompt optimization for LLMs and AI systems...
summary: Expert prompt optimization for LLMs... (truncated)
version: 1.0.0
author: ''
fileType: .md
source:
  repo: davila-templates
  path: cli-tool/components/agents/ai-specialists/prompt-engineer.md
  url: https://raw.githubusercontent.com/...
metadata:
  name: prompt-engineer
  description: Full description...
  tools: Read, Write, Edit
  model: opus
  _body: |
    Actual agent content...
install_path: ~/.claude/agents/prompt-engineer.md
```

**Missing:** `dependencies`, `category`, `subcategory`, `tags`

### 1.3 Distribution Statistics

**Prefix Analysis by Type:**

**Agents (181 total):**
- `obsidian-*` (17) - Obsidian vault operations
- `development-*` (17) - Development tools
- `programming-*` (11) - Language specialists
- `podcast-*` (11) - Podcast creation team
- `business-*` (10) - Business analysts
- `database-*` (9) - Database specialists
- `ffmpeg-*` (8) - Video/audio processing
- `devops-*` (8) - DevOps specialists
- `data-*` (8) - Data engineering
- `performance-*` (7) - Performance optimization
- `ocr-*` (7) - OCR extraction team
- `mcp-*` (7) - MCP development team
- `ai-*` (7) - AI specialists
- `web-*` (6) - Web development
- `security-*` (6) - Security specialists
- `documentation-*` (5) - Documentation generators
- And many more...

**MCPs (52 total):**
- `devtools-*` (30) - Development tools integrations
- `browser_automation-*` (6) - Browser automation
- `deepgraph-*` (4) - Deep graph analysis
- `database-*` (4) - Database integrations

**Hooks (64 total):**
- `development-tools-*` (6)
- `post-tool-*` (4)
- `pre-tool-*` (3)
- `automation-telegram-*` (3)
- `automation-slack-*` (3)
- `automation-discord-*` (3)

**Commands (18 total):**
- `docs-*` (5)
- `epcc-*` (4) - EPCC workflow commands
- `tdd-*` (2)

---

## 2. Prefix-Based Categorization Design

### 2.1 Pattern Recognition

Resources follow clear naming conventions:
```
{category}-{subcategory}-{name}
{team}-{role}
{domain}-{specialty}
```

Examples:
- `ai-specialists-prompt-engineer` → AI Specialists > Prompt Engineer
- `mcp-dev-team-mcp-security-auditor` → MCP Dev Team > Security Auditor
- `database-supabase-schema-architect` → Database > Supabase > Schema Architect
- `podcast-creator-team-social-media-copywriter` → Podcast Creator Team > Social Media Copywriter

### 2.2 Automatic Category Extraction

**Algorithm:**

```go
type ResourceCategory struct {
    Category    string   // First prefix segment
    Subcategory string   // Second prefix segment (if exists)
    Tags        []string // All prefix segments
}

func ExtractCategory(resourceID string) ResourceCategory {
    parts := strings.Split(resourceID, "-")

    if len(parts) == 1 {
        return ResourceCategory{
            Category: "general",
            Tags:     []string{parts[0]},
        }
    }

    category := parts[0]
    subcategory := ""
    if len(parts) > 1 {
        subcategory = parts[1]
    }

    // Generate hierarchical tags
    tags := []string{category}
    if subcategory != "" {
        tags = append(tags, category+"-"+subcategory)
    }

    return ResourceCategory{
        Category:    category,
        Subcategory: subcategory,
        Tags:        tags,
    }
}
```

### 2.3 Enhanced Metadata Format

**Proposed addition to catalog YAML:**

```yaml
id: ai-specialists-prompt-engineer
type: agent
name: prompt-engineer
description: Expert prompt optimization...
version: 1.0.0

# NEW: Auto-generated categorization
category:
  primary: ai-specialists      # First prefix
  secondary: null              # Second prefix (if exists)
  tags:
    - ai
    - specialists
    - prompt-engineering
    - llm-optimization

# NEW: Auto-generated during catalog sync
dependencies: []  # Added in dependency section

# Existing fields...
source:
  repo: davila-templates
  path: ...
```

### 2.4 TUI Category Navigation

**Proposed CLI Browser UX:**

```
┌─ Claude Resources Browser ─────────────────────────────────┐
│ Filter: [All] ▼  Search: _                                  │
├─────────────────────────────────────────────────────────────┤
│ Categories                          Resources (181 agents)  │
├─────────────────────────────────────────────────────────────┤
│ ▶ All Agents           (181)   │ ☐ ai-specialists-prompt-…│
│ ▼ AI Specialists       (7)     │ ☐ ai-specialists-model-…│
│     prompt-engineer             │ ☐ ai-specialists-search-…│
│     model-evaluator             │                           │
│     search-specialist           │ ▼ Database (9)            │
│   ▶ Business Analysts  (10)    │ ☐ database-supabase-sch…│
│   ▶ Database           (9)     │ ☐ database-neon-databas…│
│   ▶ Development Tools  (17)    │                           │
│   ▶ DevOps            (8)      │ ▼ MCP Dev Team (7)        │
│   ▶ MCP Dev Team      (7)      │ ☐ mcp-dev-team-mcp-secu…│
│   ▶ Podcast Team      (11)     │ ☐ mcp-dev-team-mcp-depl…│
│   ▶ OCR Team          (7)      │                           │
│   ▶ Performance       (7)      │                           │
├─────────────────────────────────────────────────────────────┤
│ [Space] Select  [Enter] Expand  [i] Install  [/] Search    │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Auto-generated category tree from prefixes
- Collapsible categories
- Resource counts per category
- Filter by category + search
- Multi-select within categories

### 2.5 Implementation Strategy

**Phase 1: Catalog Enhancement**
1. Extend `sync.js` to auto-generate `category` field during catalog sync
2. Add category extraction logic to parse resource IDs
3. Generate category metadata in individual resource YAML files
4. Update indexes to include category information

**Phase 2: CLI Integration**
1. Implement category tree builder in Go
2. Add category filter to TUI browser
3. Create hierarchical list view with collapsible categories
4. Support category-based search/filtering

**Code snippet (Go):**

```go
// internal/registry/categorizer.go
package registry

type CategoryTree struct {
    Root     *CategoryNode
    Index    map[string]*CategoryNode
}

type CategoryNode struct {
    Name      string
    Resources []*Resource
    Children  map[string]*CategoryNode
    Parent    *CategoryNode
    Count     int
}

func BuildCategoryTree(resources []*Resource) *CategoryTree {
    tree := &CategoryTree{
        Root: &CategoryNode{
            Name:     "root",
            Children: make(map[string]*CategoryNode),
        },
        Index: make(map[string]*CategoryNode),
    }

    for _, resource := range resources {
        category := extractCategoryFromID(resource.ID)
        node := tree.getOrCreateNode(category.Category)
        node.Resources = append(node.Resources, resource)
        node.Count++

        // Update parent counts
        current := node
        for current.Parent != nil {
            current.Parent.Count++
            current = current.Parent
        }
    }

    return tree
}
```

---

## 3. Dependency Management Design

### 3.1 Dependency Types

**1. Hard Dependencies (Required)**
- Must be installed before the resource can function
- Installation fails if dependency is missing
- Example: MCP server requiring a specific configuration hook

**2. Soft Dependencies (Recommended)**
- Enhance functionality but not required
- Warning shown if missing, but installation proceeds
- Example: Agent suggesting complementary agents for team workflows

**3. Cross-Type Dependencies**
- Agent depends on Command
- Hook depends on Agent
- MCP depends on Hook
- Any type can depend on any other type

### 3.2 Dependency Metadata Format

**In Source Files (Frontmatter):**

```markdown
---
name: mcp-deployment-orchestrator
description: MCP server deployment specialist
dependencies:
  required:
    - type: agent
      id: architect
      reason: "Architectural design before deployment"
    - type: hook
      id: pre-tool-security-check
      reason: "Security validation before deployment"
  recommended:
    - type: agent
      id: security-reviewer
      reason: "Enhanced security analysis"
    - type: mcp
      id: devtools-kubernetes-mcp
      reason: "Kubernetes cluster management"
tools: Read, Write, Edit, Bash
model: sonnet
---

Agent content...
```

**In Catalog YAML:**

```yaml
id: mcp-dev-team-mcp-deployment-orchestrator
type: agent
name: mcp-deployment-orchestrator
version: 1.0.0

dependencies:
  required:
    - id: architect
      type: agent
      reason: Architectural design before deployment
      version: ">=1.0.0"
    - id: pre-tool-security-check
      type: hook
      reason: Security validation before deployment

  recommended:
    - id: security-reviewer
      type: agent
      reason: Enhanced security analysis
    - id: devtools-kubernetes-mcp
      type: mcp
      reason: Kubernetes cluster management

source:
  repo: davila-templates
  path: ...
```

### 3.3 Dependency Resolution Algorithm

**Graph-Based Resolution (Topological Sort):**

```go
// internal/installer/dependency.go
package installer

type DependencyGraph struct {
    Resources map[string]*Resource
    Edges     map[string][]string  // resource_id -> dependency_ids
    Resolved  []string             // Installation order
}

type InstallPlan struct {
    ToInstall     []*Resource  // Resources to install in order
    AlreadyInstalled []*Resource  // Dependencies already present
    Missing       []*Dependency    // Required deps not found in catalog
    Recommended   []*Resource  // Optional recommended deps
}

func ResolveDependencies(resource *Resource, catalog *Catalog) (*InstallPlan, error) {
    plan := &InstallPlan{}
    visited := make(map[string]bool)

    // Build dependency graph
    graph := &DependencyGraph{
        Resources: make(map[string]*Resource),
        Edges:     make(map[string][]string),
    }

    // Recursive DFS to build graph
    if err := buildGraph(resource, catalog, graph, visited); err != nil {
        return nil, err
    }

    // Detect cycles
    if hasCycle(graph) {
        return nil, errors.New("circular dependency detected")
    }

    // Topological sort for installation order
    plan.ToInstall = topologicalSort(graph)

    // Check which are already installed
    for _, res := range plan.ToInstall {
        if isInstalled(res) {
            plan.AlreadyInstalled = append(plan.AlreadyInstalled, res)
        }
    }

    // Collect recommended dependencies
    plan.Recommended = collectRecommended(resource, catalog)

    return plan, nil
}

func buildGraph(resource *Resource, catalog *Catalog, graph *DependencyGraph, visited map[string]bool) error {
    if visited[resource.ID] {
        return nil
    }

    visited[resource.ID] = true
    graph.Resources[resource.ID] = resource

    // Process required dependencies
    for _, dep := range resource.Dependencies.Required {
        depResource, err := catalog.FindResource(dep.Type, dep.ID)
        if err != nil {
            return fmt.Errorf("required dependency not found: %s/%s", dep.Type, dep.ID)
        }

        graph.Edges[resource.ID] = append(graph.Edges[resource.ID], dep.ID)

        // Recursively resolve dependencies
        if err := buildGraph(depResource, catalog, graph, visited); err != nil {
            return err
        }
    }

    return nil
}

func hasCycle(graph *DependencyGraph) bool {
    visited := make(map[string]bool)
    recStack := make(map[string]bool)

    for id := range graph.Resources {
        if detectCycle(id, graph, visited, recStack) {
            return true
        }
    }

    return false
}

func detectCycle(id string, graph *DependencyGraph, visited, recStack map[string]bool) bool {
    if recStack[id] {
        return true // Cycle detected
    }
    if visited[id] {
        return false
    }

    visited[id] = true
    recStack[id] = true

    for _, depID := range graph.Edges[id] {
        if detectCycle(depID, graph, visited, recStack) {
            return true
        }
    }

    recStack[id] = false
    return false
}

func topologicalSort(graph *DependencyGraph) []*Resource {
    inDegree := make(map[string]int)

    // Calculate in-degrees
    for id := range graph.Resources {
        inDegree[id] = 0
    }
    for _, deps := range graph.Edges {
        for _, depID := range deps {
            inDegree[depID]++
        }
    }

    // Queue for resources with no dependencies
    queue := []string{}
    for id, degree := range inDegree {
        if degree == 0 {
            queue = append(queue, id)
        }
    }

    result := []*Resource{}

    for len(queue) > 0 {
        id := queue[0]
        queue = queue[1:]

        result = append(result, graph.Resources[id])

        // Reduce in-degree for dependents
        for _, depID := range graph.Edges[id] {
            inDegree[depID]--
            if inDegree[depID] == 0 {
                queue = append(queue, depID)
            }
        }
    }

    return result
}
```

### 3.4 Installation Flow with Dependencies

**User Experience:**

```bash
$ claude-resources install mcp-deployment-orchestrator

Resolving dependencies for mcp-deployment-orchestrator...

📦 Installation Plan:

Required Dependencies:
  1. architect (agent) - already installed ✓
  2. pre-tool-security-check (hook) - will be installed

Recommended Dependencies:
  • security-reviewer (agent)
  • devtools-kubernetes-mcp (mcp)

Install recommended dependencies? [Y/n]: y

Total to install: 4 resources

Installation Order:
  1. pre-tool-security-check (hook)
  2. security-reviewer (agent)
  3. devtools-kubernetes-mcp (mcp)
  4. mcp-deployment-orchestrator (agent)

Proceed with installation? [Y/n]: y

Installing...
  ✓ pre-tool-security-check installed to ~/.claude/hooks/
  ✓ security-reviewer installed to ~/.claude/agents/
  ✓ devtools-kubernetes-mcp installed to ~/.claude/mcps/
  ✓ mcp-deployment-orchestrator installed to ~/.claude/agents/

Installation complete! 4 resources installed.
```

**Error Handling:**

```bash
$ claude-resources install resource-with-missing-deps

Resolving dependencies...

❌ Cannot install: Missing required dependencies

Missing Required Dependencies:
  • non-existent-resource (agent) - not found in catalog
    Reason: Required for core functionality

Suggested Actions:
  1. Update catalog: claude-resources sync
  2. Check if resource exists with different ID
  3. Report issue to resource author

Installation aborted.
```

### 3.5 Dependency Visualization

**CLI Command:**

```bash
$ claude-resources deps mcp-deployment-orchestrator --tree
```

**Output:**

```
mcp-deployment-orchestrator (agent)
├── architect (agent) [required] ✓ installed
│   └── system-designer (agent) [recommended]
├── pre-tool-security-check (hook) [required]
│   └── security-reviewer (agent) [recommended]
├── security-reviewer (agent) [recommended] ✓ installed
└── devtools-kubernetes-mcp (mcp) [recommended]
    └── devtools-docker-mcp (mcp) [required]

Legend:
  [required] - Must be installed
  [recommended] - Enhances functionality
  ✓ installed - Already present
```

### 3.6 Reverse Dependencies

**Finding what depends on a resource:**

```bash
$ claude-resources deps --reverse architect

Resources that depend on architect:

Required by (2):
  • mcp-deployment-orchestrator (agent)
  • system-designer (agent)

Recommended by (5):
  • project-manager (agent)
  • code-archaeologist (agent)
  • tech-evaluator (agent)
  • business-analyst (agent)
  • architect-hook (hook)

Total: 7 resources
```

---

## 4. Enhanced Catalog Format

### 4.1 Updated Sync Process

**Enhanced sync.js logic:**

```javascript
async function extractMetadataFromContent(content, fileName) {
  const ext = path.extname(fileName);

  if (ext === '.md') {
    try {
      const { data, content: body } = matter(content);

      // NEW: Parse dependencies from frontmatter
      const dependencies = parseDependencies(data.dependencies || {});

      return {
        ...data,
        _body: body,
        dependencies  // Add to metadata
      };
    } catch (error) {
      console.error(`Error parsing frontmatter for ${fileName}:`, error.message);
      return null;
    }
  }
  // ... rest of existing code
}

function parseDependencies(depsRaw) {
  const result = {
    required: [],
    recommended: []
  };

  if (depsRaw.required) {
    result.required = depsRaw.required.map(dep => ({
      id: dep.id || dep,
      type: dep.type,
      reason: dep.reason || '',
      version: dep.version || '*'
    }));
  }

  if (depsRaw.recommended) {
    result.recommended = depsRaw.recommended.map(dep => ({
      id: dep.id || dep,
      type: dep.type,
      reason: dep.reason || ''
    }));
  }

  return result;
}

async function scanDirectoryRemote(owner, repo, branch, dirPath, resourceType) {
  // ... existing code ...

  const catalogEntry = {
    id,
    type: resourceType.slice(0, -1),
    name: resource.metadata.name || id,
    description: resource.metadata.description || '',
    version: resource.metadata.version || '1.0.0',

    // NEW: Add category
    category: extractCategory(id),

    // NEW: Add dependencies
    dependencies: resource.metadata.dependencies || { required: [], recommended: [] },

    // Existing fields...
    source: {
      repo: source.id,
      path: resource.path,
      url: rawUrl
    },
    metadata: resource.metadata,
    install_path: `~/.claude/${resourceType}/${resource.filename}`
  };

  // ... rest of code
}

function extractCategory(id) {
  const parts = id.split('-');

  if (parts.length === 1) {
    return {
      primary: 'general',
      secondary: null,
      tags: [parts[0]]
    };
  }

  return {
    primary: parts[0],
    secondary: parts.length > 1 ? parts[1] : null,
    tags: parts.slice(0, Math.min(3, parts.length))
  };
}
```

### 4.2 Updated Index Format

**Enhanced index.yaml structure:**

```yaml
# registry/catalog/agents/index.yaml
resources:
  - id: architect
    name: architect
    summary: System architecture design specialist
    fileType: .md
    category: general
    has_dependencies: false

  - id: mcp-deployment-orchestrator
    name: mcp-deployment-orchestrator
    summary: MCP server deployment specialist
    fileType: .md
    category: mcp-dev-team
    has_dependencies: true
    dependency_count: 4

count: 181

# NEW: Category breakdown
categories:
  ai-specialists:
    count: 7
    resources:
      - ai-specialists-prompt-engineer
      - ai-specialists-model-evaluator
      - ai-specialists-search-specialist
  database:
    count: 9
    resources:
      - database-supabase-schema-architect
      - database-neon-database-architect
  mcp-dev-team:
    count: 7
    resources:
      - mcp-dev-team-mcp-deployment-orchestrator
      - mcp-dev-team-mcp-security-auditor

# NEW: Dependency graph stats
dependency_stats:
  resources_with_dependencies: 23
  total_dependency_links: 67
  max_depth: 3
```

---

## 5. CLI Implementation Plan

### 5.1 Go Project Structure

```
claude-resources/
├── main.go
├── cmd/
│   ├── root.go              # Root command
│   ├── browse.go            # TUI browser
│   ├── install.go           # Install with deps
│   ├── search.go            # Search catalog
│   ├── deps.go              # Dependency analyzer
│   ├── sync.go              # Sync catalog (calls Node.js script)
│   └── categories.go        # Category browser
├── internal/
│   ├── registry/
│   │   ├── loader.go        # YAML catalog loader
│   │   ├── cache.go         # In-memory cache
│   │   ├── index.go         # Search index
│   │   ├── categorizer.go   # Category tree builder
│   │   └── validator.go     # Dependency validator
│   ├── installer/
│   │   ├── installer.go     # Resource installation
│   │   ├── dependency.go    # Dependency resolution
│   │   └── downloader.go    # GitHub file fetcher
│   ├── ui/
│   │   ├── browser.go       # Main TUI
│   │   ├── list.go          # Resource list view
│   │   ├── tree.go          # Category tree view
│   │   ├── preview.go       # Preview pane
│   │   ├── deps_view.go     # Dependency tree view
│   │   └── install_plan.go  # Installation plan UI
│   └── models/
│       ├── resource.go      # Resource types
│       ├── dependency.go    # Dependency types
│       └── category.go      # Category types
├── go.mod
└── go.sum
```

### 5.2 Key Dependencies

```go
require (
    github.com/charmbracelet/bubbletea v0.25.0    // TUI framework
    github.com/charmbracelet/bubbles v0.18.0      // TUI components
    github.com/charmbracelet/lipgloss v0.9.0      // Styling
    gopkg.in/yaml.v3 v3.0.1                       // YAML parsing
    github.com/sahilm/fuzzy v0.1.0                // Fuzzy search
    github.com/spf13/cobra v1.8.0                 // CLI framework
    github.com/dominikbraun/graph v0.23.0         // Dependency graph
    golang.org/x/sync v0.5.0                      // Concurrency utils
)
```

### 5.3 Core Data Structures

```go
// internal/models/resource.go
package models

type Resource struct {
    ID          string              `yaml:"id"`
    Type        ResourceType        `yaml:"type"`
    Name        string              `yaml:"name"`
    Description string              `yaml:"description"`
    Summary     string              `yaml:"summary"`
    Version     string              `yaml:"version"`
    Author      string              `yaml:"author"`
    FileType    string              `yaml:"fileType"`
    Category    Category            `yaml:"category"`
    Dependencies Dependencies       `yaml:"dependencies"`
    Source      Source              `yaml:"source"`
    InstallPath string              `yaml:"install_path"`
    Metadata    map[string]interface{} `yaml:"metadata"`
}

type ResourceType string

const (
    TypeAgent    ResourceType = "agent"
    TypeCommand  ResourceType = "command"
    TypeHook     ResourceType = "hook"
    TypeTemplate ResourceType = "template"
    TypeMCP      ResourceType = "mcp"
)

type Category struct {
    Primary   string   `yaml:"primary"`
    Secondary string   `yaml:"secondary,omitempty"`
    Tags      []string `yaml:"tags"`
}

type Dependencies struct {
    Required    []Dependency `yaml:"required"`
    Recommended []Dependency `yaml:"recommended"`
}

type Dependency struct {
    ID      string       `yaml:"id"`
    Type    ResourceType `yaml:"type"`
    Reason  string       `yaml:"reason,omitempty"`
    Version string       `yaml:"version,omitempty"`
}

type Source struct {
    Repo string `yaml:"repo"`
    Path string `yaml:"path"`
    URL  string `yaml:"url"`
}
```

### 5.4 Enhanced Install Command

```go
// cmd/install.go
package cmd

import (
    "fmt"
    "github.com/spf13/cobra"
    "claude-resources/internal/installer"
    "claude-resources/internal/registry"
)

var (
    noDeps      bool
    skipPrompt  bool
    showPlan    bool
)

var installCmd = &cobra.Command{
    Use:   "install [resource_id]",
    Short: "Install a resource with dependency resolution",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        resourceID := args[0]

        // Load catalog
        catalog, err := registry.LoadCatalog()
        if err != nil {
            return err
        }

        // Find resource
        resource := catalog.FindByID(resourceID)
        if resource == nil {
            return fmt.Errorf("resource not found: %s", resourceID)
        }

        // Create installer
        inst := installer.New(catalog)

        // Resolve dependencies
        plan, err := inst.ResolveDependencies(resource, !noDeps)
        if err != nil {
            return err
        }

        // Show installation plan
        if showPlan || !skipPrompt {
            plan.Display()

            if !skipPrompt {
                if !promptConfirm("Proceed with installation?") {
                    return nil
                }
            }
        }

        // Execute installation
        return inst.ExecutePlan(plan)
    },
}

func init() {
    rootCmd.AddCommand(installCmd)

    installCmd.Flags().BoolVar(&noDeps, "no-deps", false, "Skip dependency resolution")
    installCmd.Flags().BoolVar(&skipPrompt, "yes", false, "Skip confirmation prompts")
    installCmd.Flags().BoolVar(&showPlan, "show-plan", false, "Show installation plan only")
}
```

---

## 6. Migration & Rollout Strategy

### 6.1 Phase 1: Catalog Enhancement (Week 1)

**Goal:** Extend existing catalog with dependency and category metadata

**Tasks:**
1. Update sync.js to parse dependencies from frontmatter
2. Add category extraction logic
3. Enhance catalog YAML format
4. Update all index files
5. Document new metadata format for contributors

**Deliverables:**
- Enhanced catalog with dependencies and categories
- Updated sync script
- Migration guide for adding dependencies to resources

### 6.2 Phase 2: CLI Core (Week 2)

**Goal:** Build Go CLI with basic installation and browsing

**Tasks:**
1. Set up Go project structure
2. Implement catalog loader
3. Build basic TUI browser with category support
4. Implement installation without dependencies
5. Add search and filtering

**Deliverables:**
- Working CLI binary
- Basic browse and install functionality
- Category-based navigation

### 6.3 Phase 3: Dependency System (Week 3)

**Goal:** Full dependency resolution and installation

**Tasks:**
1. Implement dependency graph builder
2. Add topological sort for installation order
3. Build dependency tree UI
4. Add circular dependency detection
5. Implement reverse dependency lookup
6. Create installation plan UI

**Deliverables:**
- Full dependency resolution
- Installation with auto-dependency handling
- Dependency visualization commands

### 6.4 Phase 4: Polish & Testing (Week 4)

**Goal:** Production-ready release

**Tasks:**
1. Comprehensive testing (unit + integration)
2. Performance optimization
3. Error handling refinement
4. Documentation (README, examples, guides)
5. CI/CD setup for releases
6. Cross-platform builds

**Deliverables:**
- Production-ready v1.0.0 release
- Full documentation
- Automated releases

---

## 7. Example Use Cases

### 7.1 Installing a Resource with Dependencies

**Scenario:** User wants to install the `mcp-deployment-orchestrator` agent

**Command:**
```bash
claude-resources install mcp-deployment-orchestrator
```

**Flow:**
1. CLI loads catalog
2. Finds mcp-deployment-orchestrator resource
3. Resolves dependency graph:
   - architect (agent) - required
   - pre-tool-security-check (hook) - required
   - security-reviewer (agent) - recommended
   - devtools-kubernetes-mcp (mcp) - recommended
4. Checks installation status:
   - architect: already installed ✓
   - Others: need installation
5. Shows installation plan with 3 resources to install
6. User confirms
7. Installs in correct order
8. Reports success

### 7.2 Browsing by Category

**Command:**
```bash
claude-resources browse --category mcp-dev-team
```

**Output:**
```
📦 MCP Dev Team Agents (7)

mcp-deployment-orchestrator (v1.0.0)
MCP server deployment and operations specialist. Containerization,
Kubernetes orchestration, autoscaling, monitoring...

mcp-protocol-specialist (v1.0.0)
MCP protocol implementation expert. Streaming, SSE, transport layers...

mcp-security-auditor (v1.0.0)
Security auditing for MCP servers. Vulnerability scanning, authentication...

[4 more...]

Commands:
  i <number>  - Install resource
  d <number>  - Show dependencies
  / - Search within category
```

### 7.3 Analyzing Dependencies

**Command:**
```bash
claude-resources deps architect --tree --reverse
```

**Output:**
```
Dependency Tree for: architect

Dependencies (0):
  (none - this is a root resource)

Reverse Dependencies (7):

Required by:
  ├── mcp-deployment-orchestrator (agent)
  │   └── Needs architectural design before deployment
  └── system-designer (agent)
      └── Collaborates on system architecture

Recommended by:
  ├── project-manager (agent)
  ├── code-archaeologist (agent)
  ├── tech-evaluator (agent)
  ├── business-analyst (agent)
  └── architect-hook (hook)

Summary:
  • 2 resources require this
  • 5 resources recommend this
  • Total impact: 7 resources
```

---

## 8. Performance Considerations

### 8.1 Catalog Loading

**Optimization:**
- Lazy load full resource details
- Index-first approach for browsing
- Parallel YAML parsing
- In-memory caching

**Benchmark targets:**
- Load main index: <10ms
- Load type index: <20ms
- Full catalog load: <100ms (331 resources)
- Category tree build: <50ms

### 8.2 Dependency Resolution

**Optimization:**
- Cache dependency graphs
- Memoize topological sorts
- Parallel dependency validation
- Early cycle detection

**Benchmark targets:**
- Resolve dependencies (5 levels deep): <5ms
- Build full dependency graph: <20ms
- Detect cycles: <10ms

### 8.3 Installation

**Optimization:**
- Parallel downloads (within dependency constraints)
- Progress streaming
- Resume partial installations
- Deduplication of already-installed resources

**Benchmark targets:**
- Download single resource: <500ms
- Install 10 resources with deps: <5s
- Verify installation: <100ms

---

## 9. Security Considerations

### 9.1 Dependency Chain Attacks

**Risks:**
- Malicious dependency injection
- Compromised upstream resources
- Circular dependency exploits

**Mitigations:**
- Dependency verification via checksums
- Source validation (only trusted repos)
- Dependency depth limits (max 5 levels)
- User confirmation for external dependencies
- Audit log of all installations

### 9.2 Resource Validation

**Checks:**
- YAML schema validation
- Dependency existence verification
- Circular dependency detection
- Installation path validation (prevent path traversal)
- File type verification

---

## 10. Future Enhancements

### 10.1 Version Management

**Features:**
- Semantic versioning support
- Version constraints in dependencies (`>=1.0.0`, `^2.0.0`)
- Update checking
- Version rollback
- Changelog integration

### 10.2 Custom Registries

**Features:**
- Private catalog support
- Multiple registry sources
- Registry prioritization
- Local registry overlay

### 10.3 Resource Collections

**Features:**
- Pre-defined resource bundles
- Team-specific collections
- Workflow templates (e.g., "Full DevOps Stack")
- One-command collection installation

### 10.4 Analytics & Recommendations

**Features:**
- Most popular resources
- Trending resources
- Personalized recommendations based on installed resources
- Usage analytics (opt-in)

---

## 11. Key Recommendations

### 11.1 Immediate Actions

1. **Extend Catalog Format**
   - Add `dependencies` field to resource metadata
   - Add `category` field with auto-extraction from IDs
   - Update sync.js to parse and generate these fields

2. **Start CLI Development**
   - Initialize Go project with Bubble Tea
   - Implement basic catalog loading
   - Build category-aware TUI browser

3. **Document Dependency Format**
   - Create contribution guide for adding dependencies
   - Provide examples for each resource type
   - Document best practices

### 11.2 Design Principles

1. **User-First**
   - Automatic dependency resolution (smart defaults)
   - Clear installation plans (no surprises)
   - Easy category navigation (intuitive grouping)

2. **Performance**
   - Fast startup (<10ms)
   - Instant search (<1ms)
   - Efficient dependency resolution (<20ms)

3. **Reliability**
   - Robust error handling
   - Cycle detection
   - Atomic installations (all or nothing)
   - Rollback capability

### 11.3 Success Criteria

- ✅ Automatic category extraction for 100% of resources
- ✅ Dependency resolution in <20ms for any resource
- ✅ Zero circular dependencies in catalog
- ✅ TUI category browser with <1ms response time
- ✅ Installation success rate >99%
- ✅ User satisfaction >90% (via feedback)

---

## Conclusion

The CLI-based Resource Manager with dependency resolution and prefix-based categorization represents a significant UX and functionality upgrade:

**Key Benefits:**
1. **Automatic Organization** - 331 resources automatically categorized by prefix
2. **Smart Dependencies** - Cross-type dependency management with auto-resolution
3. **Better Discovery** - Hierarchical category browsing makes finding resources intuitive
4. **Reduced Errors** - Automatic dependency installation prevents missing resource issues
5. **Enhanced UX** - Rich TUI with category trees and dependency visualization

**Implementation Path:**
- Week 1: Catalog enhancement with dependencies + categories
- Week 2: CLI core with category navigation
- Week 3: Dependency resolution system
- Week 4: Polish and release

**Next Steps:**
1. Prototype category extraction in sync.js
2. Design dependency metadata format with community
3. Start Go CLI implementation
4. Test with subset of resources
5. Iterate based on feedback

This architecture positions the resource manager as a powerful, user-friendly tool that scales gracefully from 331 to 10,000+ resources while maintaining excellent performance and usability.

---

## Testing Analysis

**Date:** October 4, 2025
**Analysis Type:** Comprehensive Test Planning & Strategy
**Focus:** Unit, Integration, TUI, and E2E Testing Requirements

---

### Executive Summary

The Claude Resource Manager CLI requires a comprehensive testing strategy to ensure reliability across complex dependency resolution, file operations, TUI interactions, and catalog management. This analysis identifies testing requirements, tools, frameworks, coverage gaps, and quality targets for a production-ready Go CLI application managing 331+ resources.

**Key Findings:**
- **No existing tests** in the current Node.js codebase (sync.js has 421 LOC untested)
- **Greenfield Go project** - opportunity to build test-first from day 1
- **Complex testing challenges**: Dependency graphs, TUI interactions, GitHub API mocking, file I/O
- **Target coverage**: >90% for core logic, >80% overall
- **Testing frameworks identified**: Go stdlib testing, testify, bubbletea testing utilities

---

### 1. Existing Test Coverage Analysis

#### 1.1 Current State (Node.js Resource Manager)

**Location:** `../claude_resource_manager`

**Findings:**
```yaml
Test Coverage: 0%
Test Files: 0 (excluding node_modules)
Untested Code:
  - scripts/sync.js: 421 LOC (0% coverage)
  - scripts/cleanup-registry.js: 161 LOC (0% coverage)

Critical Untested Functions:
  - discoverViaGitHubAPI(): GitHub API tree traversal
  - scanDirectoryRemote(): Recursive directory scanning
  - extractMetadataFromContent(): YAML/JSON/Markdown parsing
  - generateIndex(): Catalog index generation
  - processSource(): Main orchestration logic

Risk Level: HIGH
  - No validation of GitHub API responses
  - No error handling tests
  - No edge case coverage (404s, rate limits, malformed YAML)
  - No performance regression detection
```

**Impact:**
- Catalog generation failures go undetected until runtime
- Breaking changes to GitHub repos cause silent failures
- Malformed resource metadata crashes sync process
- No regression testing for 331 resources

#### 1.2 Planned CLI Project (Go)

**Location:** `.`

**Current State:**
```yaml
Implementation Status: Planning phase (no code yet)
Test Files: 0
Opportunity: Greenfield TDD approach
```

**Advantage:** Can implement **test-first development** from the beginning

---

### 2. Testing Strategy by Component

#### 2.1 Catalog Loader (`internal/registry/loader.go`)

**Purpose:** Load and parse YAML catalog files into memory

**Unit Tests Required:**

```go
// Test Cases
- TestLoadMainIndex: Load catalog/index.yaml successfully
- TestLoadTypeIndex: Load agents/index.yaml with 181 entries
- TestLoadSingleResource: Parse individual resource YAML
- TestLoadInvalidYAML: Handle malformed YAML gracefully
- TestLoadMissingFile: Return appropriate error
- TestLoadEmptyFile: Handle empty catalog
- TestLoadConcurrent: Thread-safety for parallel loads
- TestCachingBehavior: Verify in-memory cache works
- TestLazyLoading: Load indexes before full resources

// Edge Cases
- Catalog with 10,000+ resources (performance)
- YAML with non-UTF8 characters
- Extremely large resource descriptions (>1MB)
- Circular directory symlinks
- Permission denied scenarios
- Corrupted YAML (partial UTF8 sequences)
```

**Test Data Fixtures:**
```
tests/fixtures/catalog/
├── valid/
│   ├── index.yaml (minimal valid index)
│   ├── agents/
│   │   ├── index.yaml (3 test agents)
│   │   ├── simple-agent.yaml
│   │   ├── agent-with-deps.yaml
│   │   └── agent-complex.yaml
├── invalid/
│   ├── malformed.yaml (syntax error)
│   ├── missing-fields.yaml (required fields absent)
│   └── wrong-type.yaml (type mismatches)
├── edge-cases/
│   ├── empty-catalog.yaml
│   ├── huge-description.yaml (100KB description)
│   └── unicode-heavy.yaml (emoji, CJK chars)
└── performance/
    └── large-catalog/ (1000 resources)
```

**Performance Benchmarks:**
```go
func BenchmarkLoadMainIndex(b *testing.B)
// Target: <10ms for main index
// Measures: Parse time, memory allocation

func BenchmarkLoadFullCatalog(b *testing.B)
// Target: <100ms for 331 resources
// Measures: Total load time, memory footprint

func BenchmarkConcurrentLoads(b *testing.B)
// Target: No data races, <150ms for 10 goroutines
// Measures: Thread safety, cache efficiency
```

---

#### 2.2 Dependency Resolver (`internal/installer/dependency.go`)

**Purpose:** Build dependency graph, detect cycles, topological sort

**Unit Tests Required:**

```go
// Core Functionality
- TestBuildSimpleDependencyGraph: Single required dependency
- TestBuildComplexGraph: Multi-level (5 levels deep)
- TestDetectCircularDependency: A→B→C→A cycle
- TestTopologicalSort: Correct installation order
- TestCrossTypeDependencies: Agent→Hook→MCP chain
- TestMixedDependencies: Required + Recommended
- TestAlreadyInstalled: Skip installed dependencies
- TestMissingDependency: Error on unfound resource

// Edge Cases
- TestEmptyDependencies: Resource with no deps
- TestSelfDependency: A depends on A (invalid)
- TestDiamondDependency: A→B,C; B→D; C→D (dedupe)
- TestDeepNesting: 10+ levels (depth limit?)
- TestLargeFanout: 1 resource → 50 dependencies
- TestVersionConstraints: Semantic version matching

// Error Handling
- TestPartialGraph: Some deps missing
- TestCycleInSubgraph: Main OK, subdep has cycle
- TestInvalidResourceType: Unknown type in deps
```

**Dependency Test Scenarios:**

```yaml
# Scenario 1: Linear Chain
test-agent-1:
  dependencies:
    required: [test-hook-1]

test-hook-1:
  dependencies:
    required: [test-mcp-1]

test-mcp-1:
  dependencies: []

Expected Order: [test-mcp-1, test-hook-1, test-agent-1]

# Scenario 2: Diamond Pattern
coordinator:
  dependencies:
    required: [worker-a, worker-b]

worker-a:
  dependencies:
    required: [shared-lib]

worker-b:
  dependencies:
    required: [shared-lib]

shared-lib:
  dependencies: []

Expected Order: [shared-lib, worker-a, worker-b, coordinator]
Expected Installs: 4 (shared-lib only once)

# Scenario 3: Circular Dependency (Invalid)
agent-a:
  dependencies:
    required: [agent-b]

agent-b:
  dependencies:
    required: [agent-c]

agent-c:
  dependencies:
    required: [agent-a]

Expected: Error "circular dependency detected"
```

**Performance Benchmarks:**
```go
func BenchmarkResolveDependencies_Shallow(b *testing.B)
// 1 level, 5 deps
// Target: <5ms

func BenchmarkResolveDependencies_Deep(b *testing.B)
// 5 levels, 20 total deps
// Target: <20ms

func BenchmarkDetectCycle_Large(b *testing.B)
// 100 resources, complex graph
// Target: <10ms
```

---

#### 2.3 Category Extractor (`internal/registry/categorizer.go`)

**Purpose:** Parse resource IDs into hierarchical categories

**Unit Tests Required:**

```go
// Basic Parsing
- TestExtractSimpleCategory: "database-architect" → {Primary: "database"}
- TestExtractNestedCategory: "ai-specialists-prompt-engineer" → {Primary: "ai", Secondary: "specialists"}
- TestExtractDeepNesting: "mcp-dev-team-security-auditor" → tags
- TestExtractSingleWord: "architect" → {Primary: "general"}
- TestExtractWithNumbers: "web-dev-v2-optimizer" → parsing

// Edge Cases
- TestEmptyID: "" → error or default category
- TestSpecialChars: "react-performance-100%" → sanitization
- TestUnicode: "日本語-category" → UTF8 handling
- TestVeryLongID: 200+ character ID
- TestHyphenOnly: "---" → invalid handling

// Category Tree Building
- TestBuildCategoryTree: 331 resources → tree structure
- TestCategoryCount: Verify counts per category
- TestCategoryHierarchy: Parent-child relationships
- TestCategoryFiltering: Filter resources by category
```

**Category Test Data:**
```yaml
Expected Categories (from 331 resources):
  ai-specialists: 7 resources
  database: 9 resources
  development: 17 resources
  mcp-dev-team: 7 resources
  obsidian: 17 resources
  podcast: 11 resources
  # ... 30+ more categories

Test Cases:
  - All 181 agents correctly categorized
  - No resources in "unknown" category
  - Consistent prefix extraction
  - Category tree balanced (no single category >50%)
```

---

#### 2.4 Installer (`internal/installer/installer.go`)

**Purpose:** Download and install resources to correct paths

**Integration Tests Required:**

```go
// File Operations
- TestInstallSingleResource: Download + write to ~/.claude/agents/
- TestInstallWithDependencies: Install 3 resources in order
- TestInstallToCustomPath: Support alternative install locations
- TestInstallOverwriteExisting: Confirm before overwriting
- TestInstallAtomicOperation: Rollback on partial failure
- TestInstallConcurrent: Parallel installs (safe?)

// Error Handling
- TestInstallNetworkFailure: Handle download timeout
- TestInstallDiskFull: Handle out of space
- TestInstallPermissionDenied: Handle read-only directories
- TestInstallInvalidURL: Handle 404 from GitHub
- TestInstallCorruptedFile: Validate downloaded content

// State Management
- TestInstallTracking: Record installation in state file
- TestInstallRollback: Undo failed installation
- TestUninstall: Remove resource and clean up
- TestUpdateExisting: Replace with newer version
```

**Mock GitHub API:**
```go
// Use httptest to mock GitHub responses
type MockGitHubServer struct {
    responses map[string]string // URL → file content
    delays    map[string]time.Duration // simulate slow network
    errors    map[string]error // simulate API errors
}

func TestInstallWithMockGitHub(t *testing.T) {
    mock := NewMockGitHubServer()
    mock.AddResource("test-agent.md", validAgentContent)

    installer := NewInstaller(WithGitHubClient(mock.Client()))
    err := installer.Install("test-agent")

    assert.NoError(t, err)
    assert.FileExists(t, "~/.claude/agents/test-agent.md")
}
```

**File System Testing:**
```go
// Use afero for in-memory filesystem testing
import "github.com/spf13/afero"

func TestInstallWithMockFS(t *testing.T) {
    fs := afero.NewMemMapFs()
    installer := NewInstaller(WithFileSystem(fs))

    err := installer.Install("test-agent")

    exists, _ := afero.Exists(fs, "/home/.claude/agents/test-agent.md")
    assert.True(t, exists)
}
```

**Performance Benchmarks:**
```go
func BenchmarkInstallSingle(b *testing.B)
// Target: <500ms (with real network)
// Target: <100ms (with mock)

func BenchmarkInstallBatch_10Resources(b *testing.B)
// Target: <5s (with real network)
// Target: <1s (with mock)
```

---

#### 2.5 TUI Browser (`internal/ui/browser.go`)

**Purpose:** Interactive Bubble Tea interface

**TUI Testing Challenges:**
- Terminal rendering is stateful
- Keyboard input simulation
- Screen size variations
- Race conditions in update loop

**Bubble Tea Testing Utilities:**

```go
import tea "github.com/charmbracelet/bubbletea"

// Test Model State Transitions
func TestBrowserInitialState(t *testing.T) {
    model := NewBrowserModel()

    assert.Equal(t, SearchMode, model.mode)
    assert.Empty(t, model.searchQuery)
    assert.Equal(t, 0, model.selectedIndex)
}

func TestBrowserKeyNavigation(t *testing.T) {
    model := NewBrowserModel()

    // Simulate down arrow
    model, _ = model.Update(tea.KeyMsg{Type: tea.KeyDown})
    assert.Equal(t, 1, model.selectedIndex)

    // Simulate up arrow
    model, _ = model.Update(tea.KeyMsg{Type: tea.KeyUp})
    assert.Equal(t, 0, model.selectedIndex)
}

func TestBrowserSearch(t *testing.T) {
    model := NewBrowserModel()

    // Enter search mode
    model, _ = model.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("/")})
    assert.True(t, model.searchMode)

    // Type search query
    model, _ = model.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("test")})
    assert.Equal(t, "test", model.searchQuery)

    // Verify filtered results
    assert.Greater(t, len(model.filteredResources), 0)
}

// Test View Rendering
func TestBrowserRenderOutput(t *testing.T) {
    model := NewBrowserModel()
    view := model.View()

    assert.Contains(t, view, "Claude Resources Browser")
    assert.Contains(t, view, "Search:")
    assert.Contains(t, view, "[Space] Select")
}

// Test Component Integration
func TestBrowserFullWorkflow(t *testing.T) {
    model := NewBrowserModel()

    // Search → Select → Install workflow
    testSequence := []tea.Msg{
        tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("/")},     // Enter search
        tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("test")},  // Type query
        tea.KeyMsg{Type: tea.KeyEnter},                          // Confirm search
        tea.KeyMsg{Type: tea.KeyDown},                           // Navigate
        tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune(" ")},     // Select (space)
        tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("i")},     // Install
    }

    for _, msg := range testSequence {
        model, _ = model.Update(msg)
    }

    assert.Equal(t, 1, len(model.selectedResources))
}
```

**Snapshot Testing for TUI:**
```go
func TestBrowserViewSnapshot(t *testing.T) {
    model := NewBrowserModel()
    view := model.View()

    // Golden file approach
    goldenFile := "testdata/browser_view.golden"

    if *update {
        os.WriteFile(goldenFile, []byte(view), 0644)
    }

    expected, _ := os.ReadFile(goldenFile)
    assert.Equal(t, string(expected), view)
}
```

**Terminal Size Testing:**
```go
func TestBrowserResponsiveLayout(t *testing.T) {
    sizes := []struct{width, height int}{
        {80, 24},   // Standard terminal
        {120, 40},  // Large terminal
        {40, 10},   // Small terminal (edge case)
    }

    for _, size := range sizes {
        model := NewBrowserModel()
        model, _ = model.Update(tea.WindowSizeMsg{
            Width: size.width,
            Height: size.height,
        })

        view := model.View()
        assert.NotEmpty(t, view)
        // Verify no line exceeds terminal width
        for _, line := range strings.Split(view, "\n") {
            assert.LessOrEqual(t, len(line), size.width)
        }
    }
}
```

---

#### 2.6 Search Engine (`internal/registry/index.go`)

**Purpose:** Fast fuzzy search across 331+ resources

**Unit Tests Required:**

```go
// Exact Matching
- TestSearchExactMatch: "architect" → exact ID match
- TestSearchCaseSensitive: "ARCHITECT" → case-insensitive
- TestSearchMultipleResults: "test" → all test-related resources

// Fuzzy Matching
- TestFuzzySearchTypo: "architet" → "architect" (1 char diff)
- TestFuzzySearchAbbreviation: "tcrev" → "test-code-reviewer"
- TestFuzzySearchPartial: "mcp dep" → "mcp-deployment-orchestrator"

// Performance
- TestSearchSpeed: <1ms for single query
- TestSearchLargeDataset: 10,000 resources in <10ms
- TestSearchConcurrent: Thread-safe searches

// Ranking
- TestSearchRanking: Most relevant results first
- TestSearchWeighting: Prefer ID matches over description matches
```

**Search Test Data:**
```yaml
Query: "test"
Expected Results (ranked):
  1. test-generator (exact ID match)
  2. test-engineer (ID prefix match)
  3. mcp-testing-engineer (ID contains)
  4. unit-test-creator (ID contains)
  5. performance-testing-* (category match)
  6. (description mentions "testing")

Query: "tcrev" (fuzzy)
Expected Results:
  1. test-code-reviewer (fuzzy match score: 0.85)

Query: "database postgres"
Expected Results:
  1. database-postgres-architect
  2. database-supabase-schema-architect (partial)
```

**Benchmarks:**
```go
func BenchmarkSearchExact(b *testing.B)
// Target: <1ms

func BenchmarkSearchFuzzy(b *testing.B)
// Target: <5ms

func BenchmarkSearchLargeCatalog(b *testing.B)
// 10,000 resources
// Target: <10ms
```

---

### 3. Integration Testing

#### 3.1 End-to-End Workflows

**Scenario 1: Browse and Install**
```go
func TestE2E_BrowseAndInstall(t *testing.T) {
    // Setup
    tmpDir := t.TempDir()
    os.Setenv("HOME", tmpDir)

    // Run CLI
    cmd := exec.Command("./claude-resources", "browse")

    // Simulate user input
    input := "test\n"  // Search for "test"
    input += " "       // Select first result
    input += "i\n"     // Install
    input += "y\n"     // Confirm

    cmd.Stdin = strings.NewReader(input)
    output, err := cmd.CombinedOutput()

    assert.NoError(t, err)
    assert.Contains(t, string(output), "Installation complete")

    // Verify file written
    installedPath := filepath.Join(tmpDir, ".claude", "agents", "test-generator.md")
    assert.FileExists(t, installedPath)
}
```

**Scenario 2: Dependency Resolution**
```go
func TestE2E_InstallWithDependencies(t *testing.T) {
    cmd := exec.Command("./claude-resources", "install", "mcp-deployment-orchestrator")
    output, err := cmd.CombinedOutput()

    assert.NoError(t, err)
    assert.Contains(t, string(output), "Resolving dependencies")
    assert.Contains(t, string(output), "architect (agent)")
    assert.Contains(t, string(output), "Installation complete! 4 resources installed")
}
```

**Scenario 3: Sync Catalog**
```go
func TestE2E_SyncCatalog(t *testing.T) {
    cmd := exec.Command("./claude-resources", "sync")
    output, err := cmd.CombinedOutput()

    assert.NoError(t, err)
    assert.Contains(t, string(output), "Sync complete")
    assert.FileExists(t, "registry/catalog/index.yaml")
}
```

#### 3.2 Integration with Node.js Sync Script

**Test Interoperability:**
```go
func TestIntegration_NodeSyncToGoLoader(t *testing.T) {
    // 1. Run Node.js sync script
    cmd := exec.Command("npm", "run", "sync")
    cmd.Dir = "/path/to/node-resource-manager"
    err := cmd.Run()
    assert.NoError(t, err)

    // 2. Load catalog with Go
    catalog, err := registry.LoadCatalog()
    assert.NoError(t, err)
    assert.Equal(t, 331, catalog.TotalResources())

    // 3. Verify all resources parseable
    for _, resource := range catalog.AllResources() {
        assert.NotEmpty(t, resource.ID)
        assert.NotEmpty(t, resource.Type)
        assert.NotEmpty(t, resource.Source.URL)
    }
}
```

---

### 4. Test Data & Fixtures

#### 4.1 Mock Catalog Structure

```
tests/fixtures/
├── catalog/
│   ├── minimal/              # Tiny catalog (3 resources)
│   │   ├── index.yaml
│   │   └── agents/
│   │       ├── index.yaml
│   │       ├── simple-agent.yaml
│   │       ├── agent-with-deps.yaml
│   │       └── complex-agent.yaml
│   │
│   ├── standard/             # Realistic catalog (50 resources)
│   │   ├── index.yaml
│   │   ├── agents/ (30 files)
│   │   ├── hooks/ (10 files)
│   │   ├── mcps/ (10 files)
│   │
│   └── large/                # Performance testing (1000 resources)
│       └── (auto-generated)
│
├── dependencies/
│   ├── simple-chain.yaml     # A→B→C
│   ├── diamond.yaml          # Diamond dependency
│   ├── circular.yaml         # Invalid: A→B→A
│   ├── deep-nesting.yaml     # 10 levels
│   └── large-fanout.yaml     # 1→50 deps
│
├── resources/
│   ├── valid/
│   │   ├── minimal-agent.md
│   │   ├── full-featured-agent.md
│   │   ├── hook-example.json
│   │   └── mcp-config.yaml
│   │
│   └── invalid/
│       ├── missing-name.md
│       ├── malformed-yaml.md
│       └── invalid-type.md
│
└── github-responses/          # Mock API responses
    ├── tree-response.json
    ├── contents-response.json
    ├── 404-response.json
    └── rate-limit-response.json
```

#### 4.2 Test Data Generation

```go
// Generate large catalog for performance testing
func GenerateLargeCatalog(count int) *Catalog {
    catalog := &Catalog{}

    for i := 0; i < count; i++ {
        resource := &Resource{
            ID:          fmt.Sprintf("test-resource-%d", i),
            Type:        "agent",
            Name:        fmt.Sprintf("Test Resource %d", i),
            Description: strings.Repeat("Test description ", 50),
            Version:     "1.0.0",
        }

        // Add random dependencies (10% chance)
        if rand.Float32() < 0.1 && i > 0 {
            depID := fmt.Sprintf("test-resource-%d", rand.Intn(i))
            resource.Dependencies.Required = []Dependency{
                {ID: depID, Type: "agent"},
            }
        }

        catalog.Add(resource)
    }

    return catalog
}

// Generate dependency graph scenarios
func GenerateCircularDependency() []*Resource {
    return []*Resource{
        {ID: "a", Dependencies: Dependencies{Required: []Dependency{{ID: "b", Type: "agent"}}}},
        {ID: "b", Dependencies: Dependencies{Required: []Dependency{{ID: "c", Type: "agent"}}}},
        {ID: "c", Dependencies: Dependencies{Required: []Dependency{{ID: "a", Type: "agent"}}}},
    }
}

func GenerateDiamondDependency() []*Resource {
    return []*Resource{
        {ID: "top", Dependencies: Dependencies{Required: []Dependency{
            {ID: "left", Type: "agent"},
            {ID: "right", Type: "agent"},
        }}},
        {ID: "left", Dependencies: Dependencies{Required: []Dependency{{ID: "bottom", Type: "agent"}}}},
        {ID: "right", Dependencies: Dependencies{Required: []Dependency{{ID: "bottom", Type: "agent"}}}},
        {ID: "bottom", Dependencies: Dependencies{}},
    }
}
```

---

### 5. Testing Tools & Frameworks

#### 5.1 Go Standard Library Testing

**Built-in Framework:**
```go
import "testing"

// Pros:
// - No external dependencies
// - Fast execution
// - Built-in benchmarking
// - Table-driven test support

// Example
func TestCatalogLoader(t *testing.T) {
    tests := []struct{
        name     string
        input    string
        expected int
        wantErr  bool
    }{
        {"valid catalog", "fixtures/valid.yaml", 10, false},
        {"empty catalog", "fixtures/empty.yaml", 0, false},
        {"invalid yaml", "fixtures/invalid.yaml", 0, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            catalog, err := LoadCatalog(tt.input)

            if tt.wantErr {
                assert.Error(t, err)
                return
            }

            assert.NoError(t, err)
            assert.Equal(t, tt.expected, catalog.Count())
        })
    }
}
```

#### 5.2 Testify (Assertions & Mocking)

**Recommended:** `github.com/stretchr/testify`

```go
import (
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
    "github.com/stretchr/testify/mock"
)

// Cleaner assertions
assert.Equal(t, expected, actual)
assert.NoError(t, err)
assert.Contains(t, slice, element)

// Fail fast with require
require.NoError(t, err)  // Stops test if error

// Mocking
type MockGitHubClient struct {
    mock.Mock
}

func (m *MockGitHubClient) FetchFile(url string) (string, error) {
    args := m.Called(url)
    return args.String(0), args.Error(1)
}

func TestWithMock(t *testing.T) {
    client := new(MockGitHubClient)
    client.On("FetchFile", "test.md").Return("content", nil)

    result, err := client.FetchFile("test.md")

    assert.NoError(t, err)
    assert.Equal(t, "content", result)
    client.AssertExpectations(t)
}
```

#### 5.3 Bubble Tea Testing Utilities

**Framework:** Bubble Tea's built-in test helpers

```go
import (
    tea "github.com/charmbracelet/bubbletea"
    "github.com/charmbracelet/x/exp/teatest"
)

func TestTUIInteraction(t *testing.T) {
    model := NewBrowserModel()

    tm := teatest.NewTestModel(
        t, model,
        teatest.WithInitialTermSize(80, 24),
    )

    // Send key events
    tm.Send(tea.KeyMsg{Type: tea.KeyDown})
    tm.Send(tea.KeyMsg{Type: tea.KeyEnter})

    // Wait for updates
    teatest.WaitFor(
        t, tm.Output(),
        func(bts []byte) bool {
            return bytes.Contains(bts, []byte("Selected"))
        },
        teatest.WithDuration(time.Second),
    )

    // Assert final state
    finalModel := tm.FinalModel().(BrowserModel)
    assert.Equal(t, 1, finalModel.selectedIndex)
}
```

#### 5.4 Afero (Filesystem Mocking)

**Framework:** `github.com/spf13/afero`

```go
import "github.com/spf13/afero"

func TestInstallWithMockFS(t *testing.T) {
    // In-memory filesystem
    fs := afero.NewMemMapFs()

    // Create test structure
    fs.MkdirAll("/home/.claude/agents", 0755)

    installer := NewInstaller(WithFS(fs))
    err := installer.Install("test-agent")

    assert.NoError(t, err)

    // Verify file written
    exists, _ := afero.Exists(fs, "/home/.claude/agents/test-agent.md")
    assert.True(t, exists)

    // Read and verify content
    content, _ := afero.ReadFile(fs, "/home/.claude/agents/test-agent.md")
    assert.Contains(t, string(content), "test-agent")
}
```

#### 5.5 HTTPTest (GitHub API Mocking)

**Built-in:** `net/http/httptest`

```go
import "net/http/httptest"

func TestGitHubFetcher(t *testing.T) {
    // Mock server
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.URL.Path == "/test-agent.md" {
            w.WriteHeader(http.StatusOK)
            w.Write([]byte("# Test Agent"))
        } else {
            w.WriteHeader(http.StatusNotFound)
        }
    }))
    defer server.Close()

    // Use mock server
    fetcher := NewGitHubFetcher(server.URL)
    content, err := fetcher.FetchFile("test-agent.md")

    assert.NoError(t, err)
    assert.Equal(t, "# Test Agent", content)

    // Test 404
    _, err = fetcher.FetchFile("missing.md")
    assert.Error(t, err)
}
```

#### 5.6 GoConvey (BDD-Style Testing) - Optional

**Framework:** `github.com/smartystreets/goconvey`

```go
import . "github.com/smartystreets/goconvey/convey"

func TestDependencyResolver(t *testing.T) {
    Convey("Given a resource with dependencies", t, func() {
        resource := &Resource{
            ID: "test-agent",
            Dependencies: Dependencies{
                Required: []Dependency{{ID: "dep1", Type: "agent"}},
            },
        }

        Convey("When resolving dependencies", func() {
            plan, err := ResolveDependencies(resource)

            Convey("Then should create installation plan", func() {
                So(err, ShouldBeNil)
                So(len(plan.ToInstall), ShouldEqual, 2)
            })

            Convey("And should order dependencies correctly", func() {
                So(plan.ToInstall[0].ID, ShouldEqual, "dep1")
                So(plan.ToInstall[1].ID, ShouldEqual, "test-agent")
            })
        })
    })
}
```

---

### 6. Coverage Gaps & Risk Assessment

#### 6.1 Current Gaps (Node.js Codebase)

| Component | Risk | Impact | Mitigation |
|-----------|------|--------|------------|
| `sync.js` GitHub API calls | HIGH | Catalog generation fails | Add integration tests with VCR |
| Frontmatter parsing | MEDIUM | Invalid resources in catalog | Unit test all formats (.md, .json, .py) |
| Error handling | HIGH | Silent failures | Test all error paths |
| Performance (331 resources) | MEDIUM | Slow sync times | Benchmark + optimize |

#### 6.2 Planned Gaps (Go CLI)

| Component | Testing Challenge | Strategy |
|-----------|-------------------|----------|
| TUI interactions | Keyboard simulation | Use Bubble Tea test utilities |
| Dependency graphs | Complex edge cases | Generate test scenarios programmatically |
| File I/O | Filesystem operations | Use afero for in-memory FS |
| GitHub API | Network calls | Mock with httptest |
| Concurrent operations | Race conditions | `go test -race` + stress tests |
| Terminal rendering | ANSI codes, colors | Snapshot testing with golden files |

---

### 7. Testing Pyramid

```
            /\
           /  \  E2E Tests (5%)
          /────\
         /      \  Integration Tests (25%)
        /────────\
       /          \  Unit Tests (70%)
      /────────────\
```

**Distribution:**
- **Unit Tests (70%)**: Fast, isolated, test single functions
  - Target: 1000+ unit tests
  - Execution time: <5s for full suite
  - Coverage: >90% of core logic

- **Integration Tests (25%)**: Test component interactions
  - Target: 50-100 integration tests
  - Execution time: <30s
  - Coverage: Critical workflows (install, sync, browse)

- **E2E Tests (5%)**: Full user workflows
  - Target: 10-20 E2E tests
  - Execution time: <2min
  - Coverage: Happy paths + critical errors

---

### 8. Quality Metrics & Targets

#### 8.1 Code Coverage Goals

```yaml
Overall Coverage Target: >80%

Per-Component Targets:
  Core Logic (registry, installer, dependency): >90%
  CLI Commands: >85%
  TUI Components: >75% (harder to test)
  Utilities: >90%

Coverage Exclusions:
  - main.go (entry point)
  - Generated code
  - Third-party integrations (measured separately)

Tools:
  - go test -cover
  - go test -coverprofile=coverage.out
  - go tool cover -html=coverage.out
```

**Coverage Enforcement:**
```bash
# CI pipeline check
go test -coverprofile=coverage.out ./...
COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
if (( $(echo "$COVERAGE < 80" | bc -l) )); then
    echo "Coverage $COVERAGE% below target 80%"
    exit 1
fi
```

#### 8.2 Performance Benchmarks

```yaml
Startup Time:
  Current: N/A
  Target: <10ms
  Measured: time ./claude-resources --version

Catalog Load (331 resources):
  Target: <100ms
  Benchmark: BenchmarkLoadFullCatalog

Dependency Resolution:
  Target: <20ms for 5 levels deep
  Benchmark: BenchmarkResolveDependencies_Deep

Search Query:
  Target: <1ms exact match
  Target: <5ms fuzzy search
  Benchmark: BenchmarkSearch*

Installation:
  Target: <500ms single resource (with network)
  Target: <100ms single resource (mocked)
  Benchmark: BenchmarkInstall*

Memory Usage:
  Target: <50MB for full catalog in memory
  Measured: -benchmem flag
```

**Benchmark Examples:**
```go
func BenchmarkLoadCatalog(b *testing.B) {
    b.ReportAllocs()

    for i := 0; i < b.N; i++ {
        _, err := LoadCatalog("fixtures/standard/index.yaml")
        if err != nil {
            b.Fatal(err)
        }
    }
}

// Sample output:
// BenchmarkLoadCatalog-8    1234   89456 ns/op   45678 B/op   234 allocs/op
//                           ^runs  ^time        ^memory    ^allocations
```

#### 8.3 Reliability Metrics

```yaml
Test Pass Rate:
  Target: 100% (all tests must pass)
  Measured: CI pipeline

Flaky Test Rate:
  Target: <1% (max 1 flaky test per 100)
  Tracked: Failed tests that pass on retry

Race Condition Detection:
  Command: go test -race ./...
  Target: Zero races detected

Test Execution Time:
  Unit tests: <5s total
  Integration tests: <30s total
  E2E tests: <2min total
  Full suite: <3min total
```

---

### 9. Test Scenarios by Priority

#### 9.1 Critical Path (P0 - Must Test)

1. **Load catalog successfully**
   - Valid 331-resource catalog
   - Parse all resource types
   - Build in-memory index

2. **Install single resource**
   - Download from GitHub
   - Write to correct path
   - Verify file content

3. **Resolve dependencies**
   - Build dependency graph
   - Detect circular dependencies
   - Generate installation order

4. **Search resources**
   - Exact match
   - Fuzzy search
   - Category filtering

5. **TUI navigation**
   - Arrow key navigation
   - Search input
   - Selection (space key)
   - Installation trigger

#### 9.2 Important (P1 - Should Test)

1. **Install with dependencies**
   - Multi-level resolution
   - Skip already installed
   - Batch installation

2. **Category extraction**
   - Parse all 331 resource IDs
   - Build category tree
   - Count resources per category

3. **Error handling**
   - Network failures
   - Invalid YAML
   - Missing dependencies
   - Permission errors

4. **Concurrent operations**
   - Parallel catalog loading
   - Thread-safe search
   - Atomic installations

#### 9.3 Nice to Have (P2 - Could Test)

1. **Performance edge cases**
   - 10,000 resource catalog
   - Deep dependency chains (20 levels)
   - Large fanout (100 deps)

2. **Unicode handling**
   - Japanese resource names
   - Emoji in descriptions
   - RTL languages

3. **Terminal variations**
   - Different terminal sizes
   - Color support detection
   - SSH sessions

---

### 10. CI/CD Integration

#### 10.1 GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        go: ['1.21', '1.22']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: ${{ matrix.go }}

      - name: Install dependencies
        run: go mod download

      - name: Run unit tests
        run: go test -v -race -coverprofile=coverage.out ./...

      - name: Check coverage
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
          echo "Coverage: $COVERAGE%"
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage below 80%"
            exit 1
          fi

      - name: Run benchmarks
        run: go test -bench=. -benchmem ./...

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.out

  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.22'

      - name: Build binary
        run: go build -o claude-resources ./cmd/main.go

      - name: Run E2E tests
        run: go test -v ./tests/e2e/...
```

#### 10.2 Pre-commit Hooks

```bash
# .githooks/pre-commit
#!/bin/bash

echo "Running tests before commit..."

# Run tests
go test -short ./...
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

# Check formatting
go fmt ./...

# Run linter
golangci-lint run
if [ $? -ne 0 ]; then
    echo "Linting failed. Commit aborted."
    exit 1
fi

echo "All checks passed!"
```

---

### 11. Test Data Management

#### 11.1 Fixture Organization

```
tests/
├── fixtures/
│   ├── catalog/
│   │   ├── README.md (explains fixture structure)
│   │   ├── minimal/      # 3 resources
│   │   ├── standard/     # 50 resources (representative)
│   │   └── large/        # 1000 resources (performance)
│   │
│   ├── resources/
│   │   ├── agents/
│   │   │   ├── valid/
│   │   │   └── invalid/
│   │   ├── hooks/
│   │   └── mcps/
│   │
│   ├── dependencies/
│   │   └── scenarios/
│   │       ├── linear-chain.yaml
│   │       ├── diamond.yaml
│   │       ├── circular.yaml
│   │       └── deep-nesting.yaml
│   │
│   └── github-responses/
│       ├── tree-success.json
│       ├── tree-404.json
│       └── tree-rate-limit.json
│
├── golden/               # Expected outputs for snapshot testing
│   ├── browser-view.txt
│   ├── install-plan.txt
│   └── dependency-tree.txt
│
└── helpers/              # Test utilities
    ├── catalog_builder.go
    ├── dependency_builder.go
    └── mock_github.go
```

#### 11.2 Test Helper Functions

```go
// tests/helpers/catalog_builder.go
package helpers

func NewTestCatalog() *Catalog {
    return &Catalog{
        Resources: []*Resource{
            NewTestAgent("architect", nil),
            NewTestAgent("test-generator", nil),
            NewTestHook("pre-commit-test", nil),
        },
    }
}

func NewTestAgent(id string, deps []string) *Resource {
    resource := &Resource{
        ID:          id,
        Type:        "agent",
        Name:        id,
        Description: fmt.Sprintf("Test agent: %s", id),
        Version:     "1.0.0",
    }

    for _, depID := range deps {
        resource.Dependencies.Required = append(
            resource.Dependencies.Required,
            Dependency{ID: depID, Type: "agent"},
        )
    }

    return resource
}

func NewTestCatalogFromYAML(yamlPath string) (*Catalog, error) {
    // Load from fixture file
}

// Generate large catalog for perf testing
func GenerateLargeCatalog(count int, avgDeps int) *Catalog {
    // Procedurally generate catalog with dependencies
}
```

---

### 12. Testing Best Practices

#### 12.1 Test Naming Conventions

```go
// Good test names (descriptive)
func TestLoadCatalog_ValidYAML_ReturnsCorrectCount(t *testing.T)
func TestResolveDependencies_CircularDependency_ReturnsError(t *testing.T)
func TestBrowserUpdate_DownKeyPressed_IncrementsSelectedIndex(t *testing.T)

// Bad test names (unclear)
func TestCatalog(t *testing.T)
func TestDeps(t *testing.T)
func TestBrowser(t *testing.T)

// Naming pattern:
// Test{Component}_{Scenario}_{ExpectedOutcome}
```

#### 12.2 Table-Driven Tests

```go
func TestExtractCategory(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        expected Category
    }{
        {
            name:  "simple prefix",
            input: "database-architect",
            expected: Category{Primary: "database", Secondary: ""},
        },
        {
            name:  "nested prefix",
            input: "ai-specialists-prompt-engineer",
            expected: Category{Primary: "ai", Secondary: "specialists"},
        },
        {
            name:  "single word",
            input: "architect",
            expected: Category{Primary: "general", Secondary: ""},
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := ExtractCategory(tt.input)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

#### 12.3 Test Isolation

```go
// Each test should be independent
func TestInstaller(t *testing.T) {
    // Setup: Fresh state for each test
    tmpDir := t.TempDir()  // Auto-cleanup
    installer := NewInstaller(tmpDir)

    // Test
    err := installer.Install("test-agent")

    // Assertions
    assert.NoError(t, err)

    // No explicit cleanup needed - tmpDir auto-removed
}

// Avoid global state
var globalCatalog *Catalog  // BAD - shared across tests

func TestWithGlobalState(t *testing.T) {
    globalCatalog = LoadCatalog()  // Affects other tests
}

// Better approach
func TestWithLocalState(t *testing.T) {
    catalog := LoadCatalog()  // Isolated
}
```

#### 12.4 Parallel Testing

```go
func TestCatalogLoader(t *testing.T) {
    t.Parallel()  // Run in parallel with other tests

    catalog, err := LoadCatalog("fixtures/valid.yaml")
    assert.NoError(t, err)
}

func TestSearch(t *testing.T) {
    t.Parallel()

    results := Search("test")
    assert.Greater(t, len(results), 0)
}

// Careful: Don't parallelize tests that share state
```

---

### 13. Testing Roadmap

#### Week 1: Foundation
```yaml
Tasks:
  - Set up test directory structure
  - Create fixture catalog (minimal, standard, large)
  - Implement test helpers (catalog builder, mock GitHub)
  - Write first 20 unit tests for catalog loader
  - Set up CI pipeline with coverage reporting

Deliverables:
  - Tests passing for registry/loader.go
  - Coverage: >90% for loader
  - CI workflow running on push

Metrics:
  - 20+ unit tests
  - <5s test execution
```

#### Week 2: Core Components
```yaml
Tasks:
  - Test dependency resolver (all scenarios)
  - Test category extractor
  - Test search engine (exact + fuzzy)
  - Add benchmarks for performance-critical paths
  - Integration tests for loader + dependency resolver

Deliverables:
  - Dependency resolution fully tested
  - Search performance <1ms verified
  - 50+ total tests

Metrics:
  - 70+ unit tests
  - 5+ integration tests
  - 10+ benchmarks
```

#### Week 3: TUI & Installer
```yaml
Tasks:
  - Test TUI components (browser, list, preview)
  - Test installer with mocked GitHub + FS
  - E2E tests for install workflows
  - Add golden file tests for TUI views
  - Test error handling paths

Deliverables:
  - TUI interactions testable
  - Install workflows verified
  - 100+ total tests

Metrics:
  - 100+ unit tests
  - 15+ integration tests
  - 5+ E2E tests
  - Coverage >80% overall
```

#### Week 4: Polish & Performance
```yaml
Tasks:
  - Stress tests (1000 resources, deep deps)
  - Race condition testing (go test -race)
  - Cross-platform testing (Linux, macOS, Windows)
  - Performance optimization based on benchmarks
  - Documentation of test patterns

Deliverables:
  - Production-ready test suite
  - All platforms tested
  - Performance targets met
  - Test documentation complete

Metrics:
  - 150+ tests total
  - Zero race conditions
  - Coverage >85%
  - All benchmarks meeting targets
```

---

### 14. Success Criteria

#### 14.1 Test Suite Completeness

```yaml
Unit Tests: ✓
  - Catalog loader: 20+ tests
  - Dependency resolver: 30+ tests
  - Category extractor: 15+ tests
  - Search engine: 20+ tests
  - Installer: 25+ tests
  - TUI components: 30+ tests

Integration Tests: ✓
  - Loader + Resolver: 5 tests
  - Installer + Downloader: 5 tests
  - TUI + Registry: 5 tests

E2E Tests: ✓
  - Browse workflow: 2 tests
  - Install workflow: 3 tests
  - Dependency workflow: 3 tests
  - Sync workflow: 2 tests

Total: 150+ tests
```

#### 14.2 Coverage Achieved

```yaml
Overall Coverage: >85%

Component Breakdown:
  - internal/registry/: >90%
  - internal/installer/: >90%
  - internal/ui/: >75%
  - cmd/: >85%

Exclusions:
  - main.go (entry point)
  - Generated mocks
```

#### 14.3 Performance Verified

```yaml
All Benchmarks Meeting Targets:
  ✓ Startup: <10ms
  ✓ Load catalog: <100ms
  ✓ Resolve deps: <20ms
  ✓ Search: <1ms exact, <5ms fuzzy
  ✓ Install: <500ms with network

Memory Usage:
  ✓ Full catalog: <50MB
  ✓ No memory leaks detected
```

#### 14.4 Quality Gates

```yaml
CI Pipeline:
  ✓ All tests pass on push
  ✓ Coverage >80% enforced
  ✓ No race conditions
  ✓ Builds on Linux, macOS, Windows
  ✓ Linting passes (golangci-lint)

Pre-commit Hooks:
  ✓ Tests run before commit
  ✓ Formatting enforced (go fmt)
  ✓ Quick feedback (<10s)
```

---

### 15. Key Recommendations

#### 15.1 Immediate Actions (Week 1)

1. **Set up test infrastructure**
   - Create `tests/` directory structure
   - Build fixture catalog (minimal, standard, large)
   - Configure CI pipeline with coverage reporting

2. **Start with catalog loader**
   - Highest risk component (parses 331 resources)
   - Most straightforward to test (pure functions)
   - Foundation for other components

3. **Implement test helpers**
   - Catalog builder utilities
   - Mock GitHub server
   - Fixture management functions

#### 15.2 Testing Principles

1. **Test-First Development**
   - Write failing test
   - Implement minimal code
   - Refactor while keeping tests green

2. **Isolation is Key**
   - Use mocks for external dependencies (GitHub, filesystem)
   - Each test should be independent
   - No shared global state

3. **Performance Matters**
   - Benchmark critical paths early
   - Optimize before implementing more features
   - Fast tests = faster feedback loop

4. **Coverage ≠ Quality**
   - Focus on testing behavior, not just coverage percentage
   - Edge cases and error paths are critical
   - Integration tests validate real workflows

#### 15.3 Testing Anti-Patterns to Avoid

```yaml
DON'T:
  - Test implementation details (test behavior instead)
  - Write flaky tests (use deterministic fixtures)
  - Skip error path testing (errors are critical)
  - Ignore performance (benchmark early)
  - Share state between tests (isolate each test)
  - Mock everything (integration tests need real components)

DO:
  - Test user-facing behavior
  - Use table-driven tests for variations
  - Test happy path + error paths + edge cases
  - Benchmark performance-critical code
  - Parallelize independent tests
  - Use golden files for complex outputs (TUI)
```

---

### 16. Testing Resources & References

#### 16.1 Go Testing Resources

**Official Documentation:**
- [Go Testing Package](https://pkg.go.dev/testing)
- [Go Test Command](https://pkg.go.dev/cmd/go#hdr-Test_packages)
- [Benchmarking](https://pkg.go.dev/testing#hdr-Benchmarks)

**Best Practices:**
- [Effective Go: Testing](https://go.dev/doc/effective_go#testing)
- [Table Driven Tests](https://dave.cheney.net/2019/05/07/prefer-table-driven-tests)
- [Testing Best Practices](https://github.com/golang/go/wiki/TestComments)

#### 16.2 Testing Frameworks

**Testify:**
- Repo: https://github.com/stretchr/testify
- Docs: https://pkg.go.dev/github.com/stretchr/testify

**Bubble Tea Testing:**
- Repo: https://github.com/charmbracelet/bubbletea
- Testing Utils: https://github.com/charmbracelet/x/tree/main/exp/teatest

**Afero (FS Mocking):**
- Repo: https://github.com/spf13/afero
- Docs: https://pkg.go.dev/github.com/spf13/afero

**GoConvey (Optional BDD):**
- Repo: https://github.com/smartystreets/goconvey
- Docs: http://goconvey.co/

#### 16.3 CI/CD Integration

**GitHub Actions:**
- [Go Setup Action](https://github.com/actions/setup-go)
- [Codecov Action](https://github.com/codecov/codecov-action)

**Coverage Tools:**
- [Codecov](https://about.codecov.io/)
- [Coveralls](https://coveralls.io/)

---

## Conclusion

The Claude Resource Manager CLI testing strategy provides comprehensive coverage across unit, integration, and E2E testing with clear targets and tools identified. Key priorities:

1. **Start test-first** - Greenfield Go project is ideal for TDD
2. **Focus on critical paths** - Catalog loading, dependency resolution, installation
3. **Use appropriate tools** - Go stdlib + testify + Bubble Tea testing + afero
4. **Meet coverage targets** - >90% for core logic, >80% overall
5. **Verify performance** - Benchmark early, optimize continuously

**Next Steps:**
1. Set up test infrastructure (fixtures, helpers, CI)
2. Begin with catalog loader tests (foundation)
3. Implement dependency resolver tests (critical complexity)
4. Add TUI tests (unique challenges)
5. Complete E2E workflow tests (user validation)

This test-first approach ensures reliability, maintainability, and confidence in managing 331+ resources with complex dependencies across all platforms.
