# VHS CI/CD Quick Reference

**Last Updated:** 2025-10-05
**Status:** Production Ready
**Workflow:** `.github/workflows/vhs-demos.yml`

## Quick Commands

### Local Demo Generation

```bash
# Generate all demos
make demos

# Generate specific demo
make demo-quick-start

# Clean generated GIFs
make demo-clean

# Validate workflow
bash scripts/validate-vhs-workflow.sh

# Test workflow locally (requires 'act')
bash scripts/test-vhs-workflow-local.sh
```

### CI/CD Triggers

Workflow runs automatically when:
- TUI code changes: `src/claude_resource_manager/tui/**`
- Tape files change: `demo/**/*.tape`
- Workflow file changes: `.github/workflows/vhs-demos.yml`

Manual trigger:
```bash
gh workflow run vhs-demos.yml
```

## Workflow Jobs (7 Total)

| Job | Duration | Purpose |
|-----|----------|---------|
| `security-scan` | ~30s | Validate tape files for dangerous patterns |
| `generate-demos` | 3-5min | Generate all 5 demos (parallel matrix) |
| `validate-all-demos` | ~1min | Aggregate validation of all GIFs |
| `test-vhs-integration` | 5-10min | Run 15 VHS integration tests |
| `commit-demos` | ~30s | Auto-commit GIFs (main branch only) |
| `pr-preview` | ~15s | Comment on PR with demo info (PRs only) |
| `notify-failure` | ~10s | Create GitHub issue on failure |

**Total Pipeline Time:** 10-15 minutes

## Demo Quality Standards

| Standard | Limit | Action |
|----------|-------|--------|
| Individual GIF size | 2.0MB | Warning at 2.5MB |
| Total size | 10.0MB | Hard limit |
| Dimensions | 1200x800 | Validate and warn |
| Animation frames | >1 | Fail if not animated |
| Quick Start duration | 25-35s | Test validation |
| Feature demo duration | 15-25s | Test validation |

## Security Patterns Blocked

- Command substitution: `$(...)`
- Backtick execution: `` `...` ``
- Dangerous deletions: `rm -rf /`
- Privilege escalation: `sudo`
- Remote code execution: `curl ... | sh`, `wget ... | sh`
- Insecure permissions: `chmod 777`
- Eval/exec commands: `eval`, `exec`

## Troubleshooting

### Workflow Fails on Security Scan

**Cause:** Dangerous pattern detected in tape file

**Solution:**
1. Check security scan output in GitHub Actions logs
2. Review flagged tape file
3. Remove or fix dangerous pattern
4. Commit and push fix

### GIF Too Large (>2.5MB)

**Cause:** Demo too long or complex

**Solutions:**
1. Reduce demo duration in tape file
2. Increase `TypingSpeed` (slower typing = fewer frames)
3. Remove unnecessary `Sleep` commands
4. Let auto-optimization handle it (gifsicle)

### Dimension Mismatch

**Cause:** Wrong Width/Height in tape file

**Solution:**
```bash
# Fix in .tape file
Set Width 1200
Set Height 800
```

### VHS Installation Timeout

**Cause:** Slow network or GitHub Actions issues

**Solution:**
1. Re-run workflow (VHS is cached after first success)
2. Increase timeout in workflow if persistent

### Demos Not Committed to Main

**Expected Behavior:** Demos only auto-commit on main branch pushes

**To Commit:**
1. Merge PR to main
2. Workflow runs and commits GIFs automatically
3. Check git log for commit with `[skip ci]` flag

## File Locations

```
.github/workflows/vhs-demos.yml          # Main workflow
CONTRIBUTING.md                          # Developer guide (VHS section)
docs/VHS_CI_CD_IMPLEMENTATION.md         # Full implementation docs
scripts/validate-vhs-workflow.sh         # Validation script
scripts/test-vhs-workflow-local.sh       # Local testing script
demo/*.tape                              # VHS tape files (5 files)
demo/output/*.gif                        # Generated GIFs (5 files)
tests/integration/test_vhs_integration.py # Integration tests (15 tests)
Makefile                                 # Demo generation targets
```

## Workflow Artifacts

**Retention:** 30 days
**Location:** GitHub Actions → Run → Artifacts

Download artifacts:
```bash
# Via GitHub CLI
gh run download <run-id>

# Via web
# GitHub Actions → Select run → Scroll to artifacts section
```

## Monitoring

Check workflow status:
```bash
# List recent runs
gh run list --workflow=vhs-demos.yml

# View specific run
gh run view <run-id>

# Watch run in real-time
gh run watch <run-id>
```

## Performance Benchmarks

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Total pipeline | <30min | 10-15min | ✅ 2x faster |
| Demo generation | <5min | 2-3min | ✅ Beat target |
| Security scan | <2min | ~30s | ✅ 4x faster |
| Validation | <5min | ~1min | ✅ 5x faster |

## Support

- **Issues:** Create GitHub issue with `vhs` label
- **Workflow logs:** Check GitHub Actions for detailed logs
- **Local validation:** Run `bash scripts/validate-vhs-workflow.sh`
- **Documentation:** See `docs/VHS_CI_CD_IMPLEMENTATION.md`

## Quick Fixes

### Force Re-run Workflow

```bash
# Trigger workflow manually
gh workflow run vhs-demos.yml
```

### Skip Workflow on Commit

```bash
git commit -m "fix: Update docs [skip ci]"
```

### Debug Locally

```bash
# Install VHS
brew install vhs  # macOS
# See CONTRIBUTING.md for Linux installation

# Generate demo
vhs demo/quick-start.tape

# Check output
ls -lh demo/output/quick-start.gif
```

### Update VHS Version

Edit `.github/workflows/vhs-demos.yml`:
```yaml
env:
  VHS_VERSION: 'v0.7.2'  # Change this
```

## Common Workflow Patterns

### After TUI Changes

1. Push changes to feature branch
2. Workflow runs automatically
3. Check PR for demo preview comment
4. Review generated GIFs (download artifacts)
5. Merge to main
6. Demos auto-committed to repository

### After Tape File Changes

1. Edit `.tape` file
2. Test locally: `make demo-quick-start`
3. Push changes
4. Workflow validates and generates
5. Review output in PR comments
6. Merge to main

### Manual Demo Update

1. Trigger workflow: `gh workflow run vhs-demos.yml`
2. Wait for completion (~10-15min)
3. Check main branch for new GIF commits
4. Update README.md with new demo links

## Best Practices

1. **Test locally first:** Run `make demos` before pushing
2. **Keep demos focused:** 15-25s for features, 25-35s for overview
3. **Validate syntax:** Use `bash scripts/validate-vhs-workflow.sh`
4. **Monitor file sizes:** Keep total <10MB
5. **Review security:** Don't use sudo, rm -rf, etc. in tape files
6. **Use caching:** VHS binary cached for 90% faster installs

## Emergency Procedures

### Disable Workflow

Comment out trigger in `.github/workflows/vhs-demos.yml`:
```yaml
on:
  # push:
  #   branches: [main]
  workflow_dispatch:  # Keep manual trigger
```

### Rollback Bad Demos

```bash
# Find commit with bad demos
git log --oneline --grep="Update VHS demos"

# Revert
git revert <commit-sha>
git push origin main
```

### Fix Broken Workflow

1. Create fix in feature branch
2. Test with: `bash scripts/validate-vhs-workflow.sh`
3. Push and create PR
4. Merge to main

---

**For complete documentation, see:**
- `docs/VHS_CI_CD_IMPLEMENTATION.md` - Full implementation details
- `CONTRIBUTING.md` - Developer guide with VHS section
- `.github/workflows/vhs-demos.yml` - Workflow source code
