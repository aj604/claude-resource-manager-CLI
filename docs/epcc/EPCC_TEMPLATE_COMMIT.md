# Commit Summary: [Feature/Task Name]
**Date:** YYYY-MM-DD
**Author:** [Your Name/Claude]
**Branch:** `feature/branch-name`

## Change Overview

### What Changed
[Concise summary of the changes made]

### Why It Changed
[Business justification and technical reasoning]

### Impact
- **Users:** [How this affects end users]
- **Developers:** [How this affects other developers]
- **System:** [Performance, scaling, architecture impacts]

## Files Changed Summary

### Added (X files)
```
+ src/new_module/service.py
+ src/new_module/models.py
+ tests/unit/new_module/test_service.py
+ docs/api/new_endpoint.md
```

### Modified (Y files)
```
M src/main.py
M src/config.py
M README.md
M pyproject.toml
```

### Deleted (Z files)
```
- src/deprecated/old_service.py
- tests/unit/deprecated/test_old_service.py
```

## Testing Summary

### Test Results
- ✅ **Unit Tests:** 45/45 passing
- ✅ **Integration Tests:** 12/12 passing
- ✅ **E2E Tests:** 8/8 passing
- ✅ **Coverage:** 96% (target: 80%)

### Quality Checks
- ✅ **Linting:** Pass (ruff)
- ✅ **Type Checking:** Pass (mypy strict)
- ✅ **Security Scan:** Pass (bandit)
- ✅ **Performance:** Pass (<100ms response time)

### Manual Testing
- [x] Feature works in development
- [x] Feature works in staging
- [x] Edge cases tested
- [x] Error handling verified

## Security Validation

### Security Checklist
- [x] No secrets in code
- [x] Input validation implemented
- [x] Output sanitization in place
- [x] Authentication/authorization checked
- [x] Dependencies scanned for vulnerabilities
- [x] OWASP Top 10 considerations addressed

### Security Scan Results
```
Bandit: No high or medium severity issues found
Safety: All dependencies secure
```

## Breaking Changes
[List any breaking changes, or write "None"]

### Migration Guide
[If breaking changes exist, provide migration instructions]

## Commit Message

```
feat(module): Add new feature with enhanced capabilities

- Implement core service with async support
- Add comprehensive test coverage (96%)
- Create API documentation
- Update configuration system
- Deprecate old implementation

Breaking Change: API endpoint format changed from /v1/old to /v2/new
Migration: Update client code to use new endpoint structure

Closes #123
Refs #124, #125

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Pull Request Description

### Title
`feat(module): Add new feature with enhanced capabilities`

### Description
```markdown
## Summary
This PR implements [feature name] with improved performance and maintainability.

## Changes
- ✨ New async service implementation
- 🧪 96% test coverage
- 📚 Complete API documentation
- 🔧 Updated configuration system
- 🗑️ Removed deprecated code

## Testing
- All unit and integration tests passing
- Manual testing completed
- Performance benchmarks met

## Screenshots/Demos
[If applicable]

## Checklist
- [x] Tests added/updated
- [x] Documentation updated
- [x] Security review completed
- [x] Performance validated
- [x] Breaking changes documented

## Related Issues
Closes #123
```

### Labels
- `enhancement`
- `feature`
- `needs-review`

### Reviewers
- @team-lead
- @domain-expert

## Deployment Considerations

### Pre-Deployment Checklist
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] Feature flags set
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented

### Deployment Steps
1. Run database migrations
2. Deploy to staging
3. Validate in staging
4. Deploy to production
5. Monitor metrics
6. Enable feature flag (if applicable)

### Rollback Plan
[Specific steps to rollback if issues occur]

## Documentation Updates
- [x] README.md updated
- [x] API docs generated
- [x] Architecture diagrams updated
- [x] CHANGELOG.md updated
- [x] Migration guide created (if breaking changes)

## Post-Commit Actions
- [ ] Create pull request
- [ ] Request code review
- [ ] Update project board
- [ ] Notify stakeholders
- [ ] Schedule demo (if applicable)

## Metrics & Success Indicators
- **Code Quality:** Maintainability index improved by X%
- **Performance:** Response time reduced by Xms
- **Test Coverage:** Increased from X% to Y%
- **Technical Debt:** Reduced by X story points

## Lessons Learned
1. [Key lesson or insight from implementation]
2. [What would be done differently]
3. [Best practices to apply to future work]

---
*Generated via /epcc-commit command*
