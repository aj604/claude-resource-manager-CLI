# Migration Guide: Phase 1 to Phase 2

**How-To Guide for Upgrading**

This guide helps you migrate from Phase 1 to Phase 2 of the Claude Resource Manager.

---

## Table of Contents

1. [What's New](#whats-new)
2. [Breaking Changes](#breaking-changes)
3. [Configuration Updates](#configuration-updates)
4. [Deprecated Features](#deprecated-features)
5. [Upgrade Instructions](#upgrade-instructions)
6. [Post-Upgrade Checklist](#post-upgrade-checklist)
7. [Troubleshooting](#troubleshooting)

---

## What's New

### Major Features

1. **Fuzzy Search**
   - Typo-tolerant searching with RapidFuzz
   - 77x faster than Phase 1 target
   - Intelligent scoring and ranking

2. **Category System**
   - Automatic hierarchical categorization
   - 331 resources auto-categorized
   - Fast category filtering (<1ms)

3. **Multi-Select & Batch Operations**
   - Select multiple resources (Space key)
   - Batch installation with progress tracking
   - Dependency resolution for batches

4. **Advanced UI**
   - Context-sensitive help system ('?' key)
   - Advanced sorting (by name, type, date)
   - Responsive preview pane

5. **Performance**
   - 8.4x faster startup (11.6ms)
   - Sub-millisecond search (0.32ms)
   - 5.9x better memory usage (8.5MB)

### New Dependencies

```python
# Added in Phase 2
rapidfuzz>=3.0.0    # Fuzzy search
```

No other new dependencies. All Phase 2 features use existing libraries more efficiently.

---

## Breaking Changes

### None!

Phase 2 is **100% backward compatible** with Phase 1.

- All Phase 1 APIs still work
- All Phase 1 commands unchanged
- All Phase 1 configurations honored

**You can upgrade with zero code changes.**

---

## Configuration Updates

### New Configuration Options

Phase 2 adds new optional settings. All have sensible defaults.

#### settings.json Location

```
~/.config/claude-resources/settings.json
```

#### New Settings (Optional)

```json
{
  "sort_field": "name",
  "sort_ascending": true,
  "preview_visible": true,
  "max_selections": null,
  "cache_ttl_hours": 24,
  "fuzzy_threshold": 35,
  "batch_parallel": true,
  "rollback_on_error": false
}
```

#### Setting Details

**sort_field** (string)
- Default: `"name"`
- Options: `"name"`, `"type"`, `"updated"`
- Description: Default sort field for resources

**sort_ascending** (boolean)
- Default: `true`
- Description: Sort direction (true = A-Z, false = Z-A)

**preview_visible** (boolean)
- Default: `true`
- Description: Show preview pane by default

**max_selections** (integer or null)
- Default: `null` (unlimited)
- Description: Maximum number of selectable resources

**cache_ttl_hours** (integer)
- Default: `24`
- Description: Cache time-to-live in hours

**fuzzy_threshold** (integer)
- Default: `35`
- Range: `0-100`
- Description: Minimum fuzzy match score (lower = more permissive)

**batch_parallel** (boolean)
- Default: `true`
- Description: Use parallel downloads in batch installs

**rollback_on_error** (boolean)
- Default: `false`
- Description: Rollback all on any batch failure

---

### Environment Variables

Phase 2 adds new environment variable support:

```bash
# Override config location
export CLAUDE_RESOURCES_CONFIG="~/.custom/config.json"

# Override cache location
export CLAUDE_RESOURCES_CACHE="~/.custom/cache/"

# Disable caching
export CLAUDE_RESOURCES_NO_CACHE=1

# Enable debug logging
export CLAUDE_RESOURCES_DEBUG=1
```

---

## Deprecated Features

### None!

All Phase 1 features remain supported in Phase 2.

No features deprecated. This is a purely additive release.

---

## Upgrade Instructions

### Method 1: pip (Recommended)

```bash
# Upgrade to Phase 2
pip install --upgrade claude-resources

# Verify version
claude-resources --version
# Should show: v0.2.0 or higher
```

### Method 2: From Source

```bash
# Navigate to repo
cd claude_resource_manager-CLI

# Pull latest changes
git pull origin main

# Upgrade dependencies
pip install --upgrade -e ".[dev]"

# Verify upgrade
pytest tests/unit/
# Should show: 457 passed (Phase 2 test count)
```

### Method 3: Docker (if using containers)

```bash
# Pull latest image
docker pull anthropics/claude-resources:latest

# Or rebuild
docker build -t claude-resources:phase2 .
```

---

## Post-Upgrade Checklist

### 1. Verify Installation

```bash
# Check version
claude-resources --version

# Should output:
# claude-resources v0.2.0
```

### 2. Test Basic Commands

```bash
# Browse resources (should show new UI)
claude-resources browse

# Fuzzy search should work
# In browser, type "/" then "architet" (typo)
# Should find "architect"

# Help screen should appear
# Press "?" to show help
```

### 3. Check Configuration

```bash
# Verify config location
ls -la ~/.config/claude-resources/settings.json

# If missing, create default
cat > ~/.config/claude-resources/settings.json << EOF
{
  "sort_field": "name",
  "sort_ascending": true,
  "preview_visible": true,
  "cache_ttl_hours": 24
}
EOF
```

### 4. Test New Features

#### Fuzzy Search

```bash
# Launch browser
claude-resources browse

# Type "/" to search
# Enter: "architet" (typo)
# Should find: "architect"
```

#### Multi-Select

```bash
# In browser:
# 1. Press Space on a resource (should see [x])
# 2. Press Space on another (should see [x])
# 3. Press 'i' to install selected
# Should see batch progress
```

#### Category Filtering

```bash
# In browser:
# Click "MCP" filter button
# Should show only MCP servers (52 resources)
```

#### Help System

```bash
# In browser:
# Press "?"
# Should show help screen with all shortcuts
```

### 5. Verify Performance

Run performance benchmarks:

```bash
# Run benchmark tests
pytest tests/unit/test_performance.py -v

# Should see:
# test_BENCHMARK_cold_start_under_100ms PASSED (11.6ms < 100ms)
# test_BENCHMARK_search_performance PASSED (0.32ms < 5ms)
# ... all benchmarks passing
```

---

## Troubleshooting

### Issue: "Module not found: rapidfuzz"

**Cause**: RapidFuzz dependency not installed

**Solution**:
```bash
pip install rapidfuzz>=3.0.0
# Or reinstall package
pip install --upgrade --force-reinstall claude-resources
```

---

### Issue: Fuzzy search not working

**Symptoms**: Typing in search box doesn't find resources with typos

**Diagnosis**:
```bash
# Check RapidFuzz version
python -c "import rapidfuzz; print(rapidfuzz.__version__)"
# Should be >= 3.0.0
```

**Solution**:
```bash
pip install --upgrade rapidfuzz
```

---

### Issue: Help screen shows old shortcuts

**Cause**: Cached TUI screens

**Solution**:
```bash
# Clear cache
rm -rf ~/.cache/claude-resources/

# Restart application
claude-resources browse
```

---

### Issue: Multi-select not visible

**Symptoms**: Pressing Space doesn't show checkbox

**Diagnosis**: Check if table has checkbox column

**Solution**:
```bash
# Verify Phase 2 version
claude-resources --version
# Should be v0.2.0+

# If not, upgrade:
pip install --upgrade claude-resources
```

---

### Issue: Performance slower than expected

**Symptoms**: Search takes >1 second

**Diagnosis**:
```bash
# Enable debug logging
export CLAUDE_RESOURCES_DEBUG=1
claude-resources browse

# Check logs for bottlenecks
```

**Solutions**:

1. **Enable caching**:
   ```json
   {
     "use_cache": true
   }
   ```

2. **Check terminal performance**:
   ```bash
   # Test terminal rendering speed
   time printf "\n%.0s" {1..1000}
   # Should be <50ms
   ```

3. **Reduce catalog size**:
   ```bash
   # Filter before searching
   # Click "Agent" filter, then search
   ```

---

### Issue: Memory usage high

**Symptoms**: Application uses >50MB memory

**Diagnosis**:
```bash
# Check memory usage
ps aux | grep claude-resources

# Typical Phase 2 usage: 8-15MB
```

**Solutions**:

1. **Disable caching** (if memory constrained):
   ```bash
   export CLAUDE_RESOURCES_NO_CACHE=1
   ```

2. **Restart application** (clear accumulated data):
   ```bash
   # Exit and relaunch
   q  # Exit
   claude-resources browse  # Relaunch
   ```

---

### Issue: Configuration not loading

**Symptoms**: Settings.json changes not taking effect

**Diagnosis**:
```bash
# Check config file location
cat ~/.config/claude-resources/settings.json

# Verify JSON is valid
python -m json.tool ~/.config/claude-resources/settings.json
```

**Solution**:
```bash
# Fix JSON syntax errors
# Common issue: missing comma or trailing comma
{
  "sort_field": "name",    ← Comma required
  "sort_ascending": true   ← No trailing comma
}

# Verify fix
python -m json.tool ~/.config/claude-resources/settings.json
# Should output formatted JSON if valid
```

---

## Migration Path Examples

### Example 1: Basic User (No Custom Config)

**Before (Phase 1)**:
```bash
pip install claude-resources
claude-resources browse
```

**After (Phase 2)**:
```bash
pip install --upgrade claude-resources
claude-resources browse  # All new features work automatically!
```

**Changes Required**: None!

---

### Example 2: User with Custom Config

**Before (Phase 1)**:
```json
{
  "catalog_path": "~/.claude/catalog.yaml",
  "install_path": "~/.claude"
}
```

**After (Phase 2)**:
```json
{
  "catalog_path": "~/.claude/catalog.yaml",
  "install_path": "~/.claude",

  // New Phase 2 settings (optional)
  "sort_field": "name",
  "fuzzy_threshold": 40,
  "max_selections": 10
}
```

**Changes Required**: Add new settings (optional)

---

### Example 3: Developer Using API

**Before (Phase 1)**:
```python
from claude_resource_manager.core.search_engine import SearchEngine

engine = SearchEngine()
results = engine.search("architect", limit=10)
```

**After (Phase 2)**:
```python
from claude_resource_manager.core.search_engine import SearchEngine

engine = SearchEngine(use_cache=True)  # New: caching support

# Phase 1 API still works
results = engine.search("architect", limit=10)

# Phase 2 new API: fuzzy search with scoring
results = engine.search_smart("architet", limit=10)  # Typo-tolerant!
for r in results:
    print(f"{r['id']}: score={r['score']}")
```

**Changes Required**: Optional (can use new APIs for better features)

---

## Summary

### Upgrade is Easy

1. Run: `pip install --upgrade claude-resources`
2. Test: `claude-resources browse`
3. Done!

### Zero Breaking Changes

- All Phase 1 code still works
- All Phase 1 configs still work
- All Phase 1 commands unchanged

### New Features Available Immediately

- Fuzzy search
- Categories
- Multi-select
- Help system
- Better performance

### Recommended Post-Upgrade

1. Enable caching: `{"use_cache": true}`
2. Try fuzzy search: Search with typos
3. Try multi-select: Space key + 'i'
4. Review help: Press '?'

**Migration Time**: <5 minutes

See [PHASE_2_FEATURES.md](PHASE_2_FEATURES.md) for full feature documentation.
