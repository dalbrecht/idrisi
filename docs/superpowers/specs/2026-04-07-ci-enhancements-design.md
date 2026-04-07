# CI Enhancements Design Spec

**Date:** 2026-04-07
**Status:** Draft

## Overview

Four CI enhancements in one PR: dependency caching for faster builds, a PR template following coding standards, documented branch protection rules, and Dependabot for automated dependency updates.

## 1. Dependency Caching

Add caching to `.github/workflows/ci.yml` to reduce CI runtime on cache hits.

- **uv cache:** `astral-sh/setup-uv` has built-in cache support via `enable-cache: true`
- **npm cache:** `actions/setup-node` has built-in cache support via `cache: 'npm'` with `cache-dependency-path: 'web/package-lock.json'`
- No `actions/cache` needed — both setup actions handle caching natively

## 2. PR Template

Create `.github/pull_request_template.md` following `proc-02_git_version_control_standards.md`:

```markdown
## Summary

<!-- Brief overview of what changed and why -->

## Changes

<!-- Detailed list of what was modified -->

-

## Testing

- [ ] `make ci` passes (lint + format + tests + coverage)
- [ ] Tests added for new functionality
- [ ] Documentation updated (if user-facing changes)

## Breaking Changes

<!-- List any breaking changes, or delete this section if none -->

None
```

## 3. Branch Protection Documentation

Create `.github/BRANCH_PROTECTION.md` documenting the recommended GitHub settings to enable manually:

- Require pull request reviews before merging (1 approval)
- Require status checks to pass (CI workflow)
- Require branches to be up to date before merging
- Automatically delete head branches after merge
- Do not allow force pushes to main

This is documentation only — branch protection rules must be configured through GitHub's web UI or API.

## 4. Dependabot

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "npm"
    directory: "/web"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Out of Scope

- Branch protection rule automation (requires admin API token or manual setup)
- Renovate (Dependabot is sufficient for this project)
- Security scanning workflows (Dependabot covers vulnerability alerts)
- Release automation

## Success Criteria

1. CI uses cached uv and npm dependencies on subsequent runs
2. New PRs auto-populate with the template
3. Branch protection settings are documented and easy to enable
4. Dependabot creates update PRs for Python, npm, and Actions dependencies
