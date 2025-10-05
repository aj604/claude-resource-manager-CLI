# Configuration Reference

**Reference-Oriented Configuration Documentation**

Complete reference for configuring the Claude Resource Manager CLI.

---

## Table of Contents

1. [Configuration File](#configuration-file)
2. [Settings Reference](#settings-reference)
3. [Environment Variables](#environment-variables)
4. [Configuration Precedence](#configuration-precedence)
5. [Examples](#examples)

---

## Configuration File

### Location

```
~/.config/claude-resources/settings.json
```

### Format

JSON format with optional settings. All settings have sensible defaults.

### Creating Configuration File

```bash
# Create config directory
mkdir -p ~/.config/claude-resources

# Create default settings
cat > ~/.config/claude-resources/settings.json << 'EOF'
{
  "sort_field": "name",
  "sort_ascending": true,
  "preview_visible": true,
  "cache_ttl_hours": 24
}
EOF
```

### Validation

```bash
# Validate JSON syntax
python -m json.tool ~/.config/claude-resources/settings.json

# Expected output: Formatted JSON (if valid)
```

---

## Settings Reference

### Complete Settings Schema

```json
{
  "sort_field": "name",
  "sort_ascending": true,
  "preview_visible": true,
  "max_selections": null,
  "cache_ttl_hours": 24,
  "fuzzy_threshold": 35,
  "batch_parallel": true,
  "rollback_on_error": false,
  "catalog_url": "https://raw.githubusercontent.com/...",
  "install_path": "~/.claude",
  "catalog_path": "~/.claude/catalog.yaml"
}
```

---

### sort_field

**Type**: `string`

**Default**: `"name"`

**Options**:
- `"name"` - Sort by resource name
- `"type"` - Sort by resource type
- `"updated"` - Sort by last updated date

**Description**: Default field for sorting resources in browser.

**Example**:
```json
{
  "sort_field": "type"
}
```

**UI**: Press `s` in browser to change sort field dynamically.

---

### sort_ascending

**Type**: `boolean`

**Default**: `true`

**Description**: Sort direction. `true` = ascending (A-Z), `false` = descending (Z-A).

**Example**:
```json
{
  "sort_field": "name",
  "sort_ascending": false
}
```

**Result**: Resources sorted Z-A by name.

**UI**: Press `1`, `2`, or `3` to toggle sort direction.

---

### preview_visible

**Type**: `boolean`

**Default**: `true`

**Description**: Show preview pane by default in browser.

**Example**:
```json
{
  "preview_visible": false
}
```

**Result**: Browser starts with preview pane hidden.

**UI**: Press `p` to toggle preview pane visibility.

**Note**: Automatically hidden on narrow terminals (<80 columns).

---

### max_selections

**Type**: `integer` or `null`

**Default**: `null` (unlimited)

**Range**: `1` to `1000` (or `null`)

**Description**: Maximum number of resources that can be selected for batch operations.

**Examples**:

```json
{
  "max_selections": null
}
```
**Result**: Unlimited selections.

```json
{
  "max_selections": 10
}
```
**Result**: Can select up to 10 resources. Attempting to select more shows warning.

**Use Cases**:
- Prevent accidental mass installs
- Limit resource usage
- Control batch size

---

### cache_ttl_hours

**Type**: `integer`

**Default**: `24`

**Range**: `1` to `168` (1 week)

**Description**: Cache time-to-live in hours for catalog and search results.

**Example**:
```json
{
  "cache_ttl_hours": 48
}
```

**Result**: Cache valid for 48 hours before refresh.

**Cache Locations**:
- Catalog cache: `~/.cache/claude-resources/catalog.json`
- Search cache: In-memory (LRU)

**Clear Cache**:
```bash
rm -rf ~/.cache/claude-resources/
```

---

### fuzzy_threshold

**Type**: `integer`

**Default**: `35`

**Range**: `0` to `100`

**Description**: Minimum fuzzy match score (0-100) for search results. Lower = more permissive.

**Score Interpretation**:
- `100`: Exact match
- `80-99`: High match (1-2 typos)
- `60-79`: Medium match (3-4 typos)
- `35-59`: Weak match (many typos)
- `0-34`: Very weak (unlikely to be relevant)

**Examples**:

```json
{
  "fuzzy_threshold": 50
}
```
**Result**: Stricter matching, fewer results. Good for reducing noise.

```json
{
  "fuzzy_threshold": 25
}
```
**Result**: More permissive, more results. Good for exploratory searching.

**Recommended Values**:
- **Strict**: `50-60` (only high-quality matches)
- **Balanced**: `35-45` (default, good trade-off)
- **Permissive**: `20-30` (find everything, more noise)

---

### batch_parallel

**Type**: `boolean`

**Default**: `true`

**Description**: Use parallel downloads in batch installations (faster but uses more resources).

**Example**:
```json
{
  "batch_parallel": true
}
```

**Result**: Batch installs download in parallel (2-3x faster).

**Performance**:
- **Parallel (`true`)**: 5 resources in ~2-5s
- **Sequential (`false`)**: 5 resources in ~5-10s

**Use Cases**:
- **Enable** for fast installs (default)
- **Disable** if network/CPU limited

**Note**: Phase 2 implementation is sequential with dependency resolution. True parallelism is a future enhancement.

---

### rollback_on_error

**Type**: `boolean`

**Default**: `false`

**Description**: Rollback all installations on any failure during batch install.

**Example**:
```json
{
  "rollback_on_error": true
}
```

**Result**: If any resource fails to install, all successfully installed resources are deleted.

**Behavior**:

**`false` (default)**:
```text
Installing 5 resources:
  ✓ architect         (success)
  ✓ security-expert   (success)
  ✗ broken-resource   (failed)
  ✓ test-generator    (success)
  ○ duplicate-item    (skipped)

Result: 3 succeeded, 1 failed, 1 skipped
Files kept: architect, security-expert, test-generator
```

**`true`**:
```text
Installing 5 resources:
  ✓ architect         (success)
  ✓ security-expert   (success)
  ✗ broken-resource   (failed)

Result: Rolling back all changes
Files deleted: architect, security-expert
```

**Use Cases**:
- **Disable** (`false`): Keep successful installs (default)
- **Enable** (`true`): All-or-nothing atomic batch

---

### catalog_url

**Type**: `string` (URL)

**Default**: `"https://raw.githubusercontent.com/anthropics/claude-resources/main/catalog.yaml"`

**Description**: URL to fetch resource catalog from.

**Example**:
```json
{
  "catalog_url": "https://example.com/custom-catalog.yaml"
}
```

**Result**: Loads catalog from custom URL.

**Security**: Must be HTTPS (HTTP blocked for security).

**Custom Catalogs**:
```yaml
# custom-catalog.yaml
total: 10
resources:
  - id: my-custom-agent
    type: agent
    name: My Custom Agent
    source:
      url: https://example.com/agents/my-custom-agent.md
```

---

### install_path

**Type**: `string` (path)

**Default**: `"~/.claude"`

**Description**: Base directory for installing resources.

**Example**:
```json
{
  "install_path": "~/Documents/claude-resources"
}
```

**Result**: Resources installed to `~/Documents/claude-resources/agents/`, `~/Documents/claude-resources/mcps/`, etc.

**Directory Structure**:
```
~/.claude/
├── agents/
│   ├── architect.md
│   └── security-expert.md
├── mcps/
│   └── mcp-server-config.yaml
├── hooks/
├── commands/
└── templates/
```

**Security**: Path validated to prevent traversal attacks.

---

### catalog_path

**Type**: `string` (path)

**Default**: `"~/.claude/catalog.yaml"`

**Description**: Local path to catalog file (for offline use or custom catalogs).

**Example**:
```json
{
  "catalog_path": "~/my-catalog.yaml"
}
```

**Result**: Loads catalog from local file instead of downloading.

**Use Cases**:
- Offline usage
- Custom catalog
- Testing/development

**Precedence**: If `catalog_path` exists, it's used instead of `catalog_url`.

---

## Environment Variables

Environment variables override `settings.json` values.

### CLAUDE_RESOURCES_CONFIG

**Type**: `string` (path)

**Description**: Override config file location.

**Example**:
```bash
export CLAUDE_RESOURCES_CONFIG="~/.custom/config.json"
claude-resources browse
```

**Result**: Loads config from `~/.custom/config.json` instead of default location.

---

### CLAUDE_RESOURCES_CACHE

**Type**: `string` (path)

**Description**: Override cache directory location.

**Example**:
```bash
export CLAUDE_RESOURCES_CACHE="~/.custom/cache/"
claude-resources browse
```

**Result**: Cache stored in `~/.custom/cache/` instead of `~/.cache/claude-resources/`.

---

### CLAUDE_RESOURCES_NO_CACHE

**Type**: `boolean` (0 or 1)

**Description**: Disable all caching.

**Example**:
```bash
export CLAUDE_RESOURCES_NO_CACHE=1
claude-resources browse
```

**Result**: No caching (always fetch fresh data).

**Use Cases**:
- Debugging
- Memory-constrained environments
- Testing

---

### CLAUDE_RESOURCES_DEBUG

**Type**: `boolean` (0 or 1)

**Description**: Enable debug logging.

**Example**:
```bash
export CLAUDE_RESOURCES_DEBUG=1
claude-resources browse 2> debug.log
```

**Result**: Verbose debug logs to stderr.

**Log Contents**:
- API calls
- Cache hits/misses
- Performance timings
- Error stack traces

---

## Configuration Precedence

Settings are loaded in this order (highest priority first):

1. **Environment Variables** (highest priority)
2. **Command-Line Arguments**
3. **Config File** (`~/.config/claude-resources/settings.json`)
4. **Default Values** (lowest priority)

### Example Precedence

**Config file** (`settings.json`):
```json
{
  "sort_field": "name",
  "cache_ttl_hours": 24
}
```

**Environment variable**:
```bash
export CLAUDE_RESOURCES_CACHE_TTL=48
```

**Command-line**:
```bash
claude-resources browse --sort-field type
```

**Result**:
- `sort_field`: `"type"` (command-line wins)
- `cache_ttl_hours`: `48` (env var wins over config)
- `preview_visible`: `true` (default, nothing overrides)

---

## Examples

### Example 1: Developer Configuration

**Use Case**: Developer who wants fast installs, strict search, and custom paths.

```json
{
  "install_path": "~/dev/claude-resources",
  "catalog_path": "~/dev/claude-catalog.yaml",
  "fuzzy_threshold": 50,
  "batch_parallel": true,
  "rollback_on_error": true,
  "cache_ttl_hours": 1
}
```

**Result**:
- Resources installed to `~/dev/claude-resources/`
- Uses local catalog: `~/dev/claude-catalog.yaml`
- Strict fuzzy search (threshold 50)
- Fast parallel installs
- All-or-nothing batch installs
- Cache expires every hour (frequent updates)

---

### Example 2: Conservative Configuration

**Use Case**: User on limited network, wants offline mode and conservative settings.

```json
{
  "catalog_path": "~/.claude/offline-catalog.yaml",
  "batch_parallel": false,
  "fuzzy_threshold": 60,
  "max_selections": 5,
  "cache_ttl_hours": 168
}
```

**Result**:
- Uses offline catalog
- Sequential installs (less network load)
- Strict search (threshold 60)
- Max 5 selections (controlled batches)
- Cache valid for 1 week

**Setup**:
```bash
# Download catalog for offline use
curl https://example.com/catalog.yaml -o ~/.claude/offline-catalog.yaml
```

---

### Example 3: Power User Configuration

**Use Case**: Power user who wants maximum control and performance.

```json
{
  "sort_field": "updated",
  "sort_ascending": false,
  "preview_visible": true,
  "max_selections": null,
  "fuzzy_threshold": 35,
  "batch_parallel": true,
  "rollback_on_error": false,
  "cache_ttl_hours": 12
}
```

**Result**:
- Sort by newest first (updated desc)
- Preview always visible
- Unlimited selections
- Balanced fuzzy search
- Fast parallel installs
- Keep partial successes
- Cache refreshes twice daily

---

### Example 4: Testing Configuration

**Use Case**: Developer testing new features, needs fresh data and verbose logging.

**Config file**:
```json
{
  "catalog_url": "http://localhost:8000/test-catalog.yaml",
  "install_path": "/tmp/claude-test",
  "cache_ttl_hours": 0
}
```

**Environment variables**:
```bash
export CLAUDE_RESOURCES_DEBUG=1
export CLAUDE_RESOURCES_NO_CACHE=1
```

**Result**:
- Uses local test catalog
- Installs to temp directory
- No caching (always fresh)
- Debug logging enabled

---

## Configuration Best Practices

### 1. Start with Defaults

```json
{}
```

**Result**: All defaults applied. Good starting point.

---

### 2. Only Override What You Need

```json
{
  "fuzzy_threshold": 40
}
```

**Result**: Only fuzzy threshold changed, everything else uses defaults.

**Advantage**: Easier to maintain, benefits from future default improvements.

---

### 3. Document Custom Settings

```json
{
  // Stricter search for production use
  "fuzzy_threshold": 50,

  // Custom install location for team
  "install_path": "/team/shared/claude-resources"
}
```

**Note**: JSON doesn't support comments. Use a separate `README.md`:

```markdown
# Configuration Notes

- `fuzzy_threshold: 50` - Stricter search to reduce noise
- `install_path: /team/shared/...` - Shared team directory
```

---

### 4. Version Control Friendly

```bash
# Don't commit personal settings
echo "settings.json" >> ~/.config/claude-resources/.gitignore

# Commit example/template
cp settings.json settings.example.json
git add settings.example.json
```

---

### 5. Validate After Changes

```bash
# Validate JSON syntax
python -m json.tool ~/.config/claude-resources/settings.json

# Test configuration
claude-resources browse
# Verify expected behavior
```

---

## Troubleshooting Configuration

### Issue: Configuration Not Loading

**Symptoms**: Changes to `settings.json` not taking effect.

**Diagnosis**:
```bash
# Check file location
ls -la ~/.config/claude-resources/settings.json

# Check JSON syntax
python -m json.tool ~/.config/claude-resources/settings.json
```

**Solutions**:
1. Verify file location is correct
2. Fix JSON syntax errors (common: trailing commas, missing quotes)
3. Restart application

---

### Issue: Invalid JSON

**Symptoms**: Error message: "Invalid JSON in configuration file"

**Common Mistakes**:

```json
{
  "sort_field": "name",   ← Trailing comma (invalid)
}

{
  sort_field: "name"      ← Missing quotes (invalid)
}

{
  "fuzzy_threshold": 35,
  "cache_ttl_hours": 24,  ← Trailing comma (invalid)
}
```

**Fix**:
```json
{
  "sort_field": "name",
  "fuzzy_threshold": 35,
  "cache_ttl_hours": 24
}
```

**Validation Tool**:
```bash
python -m json.tool settings.json
# Shows exactly where error is
```

---

### Issue: Setting Ignored

**Symptoms**: Setting in config file not taking effect.

**Cause**: Environment variable or command-line argument overriding it.

**Diagnosis**:
```bash
# Check environment variables
env | grep CLAUDE_RESOURCES

# Check for overrides
echo $CLAUDE_RESOURCES_CACHE_TTL
```

**Solution**: Unset environment variable if not needed:
```bash
unset CLAUDE_RESOURCES_CACHE_TTL
```

---

## Summary

Configuration provides flexible control over:

1. **Search behavior**: Fuzzy threshold, sorting
2. **UI preferences**: Preview, selections
3. **Performance**: Caching, parallelism
4. **Paths**: Install location, catalog source
5. **Batch operations**: Parallelism, rollback

**Key Points**:
- All settings optional (sensible defaults)
- Environment variables override config file
- JSON format with validation
- Changes take effect on next launch

**Configuration Locations**:
- Settings: `~/.config/claude-resources/settings.json`
- Cache: `~/.cache/claude-resources/`
- Installs: `~/.claude/` (or custom `install_path`)

See [PHASE_2_FEATURES.md](PHASE_2_FEATURES.md) for feature documentation and [MIGRATION_PHASE1_TO_PHASE2.md](MIGRATION_PHASE1_TO_PHASE2.md) for upgrade instructions.
