# GitHub Actions CI Design Spec

**Date:** 2026-04-07
**Status:** Draft

## Overview

Add a GitHub Actions CI workflow that runs lint, format checks, tests, and coverage enforcement on pull requests to `main`. Coverage thresholds are set at current baselines (100% domain, 89% overall) with an issue to track reaching targets (100% domain, 95% overall).

## Goals

1. PRs to `main` are automatically validated: lint, format, tests, coverage
2. Domain layer coverage is enforced at 100% (current baseline)
3. Overall coverage is enforced at 89% (current baseline)
4. `make ci` enforces the same thresholds locally
5. No external services (no Codecov, no tokens)

## Current Coverage Baselines

| Layer | Coverage | Target |
|-------|----------|--------|
| Domain | 100% | 100% (met) |
| Overall | 89% | 95% (gap: 6%) |

## Workflow: `.github/workflows/ci.yml`

**Triggers:** Pull requests targeting `main`.

**Runner:** `ubuntu-latest`

**Steps:**
1. Checkout code with submodules (`actions/checkout` with `submodules: true`)
2. Set up Python 3.12 (`actions/setup-python`)
3. Install uv (`astral-sh/setup-uv`)
4. Set up Node.js 18 (`actions/setup-node`)
5. Install system dependencies for Cartopy: `sudo apt-get install -y libgeos-dev libproj-dev`
6. `make bootstrap` — create venv and install deps
7. `make build-web` — build Svelte frontend
8. `make ci` — lint + format check + tests with overall coverage enforcement (89%)
10. Domain coverage gate: `uv run pytest tests/domain/ --cov=voyages.domain --cov-fail-under=100`

## pyproject.toml Changes

Add coverage configuration:

```toml
[tool.coverage.run]
source = ["voyages"]

[tool.coverage.report]
show_missing = true
```

## Makefile Changes

Update `test` target to include coverage:

```makefile
test: ## Run tests with coverage (excludes e2e)
	uv run pytest -m "not e2e" --cov=voyages --cov-fail-under=89
```

Add domain coverage target:

```makefile
ci-domain: ## Verify 100% domain test coverage
	uv run pytest tests/domain/ --cov=voyages.domain --cov-fail-under=100
```

Update `ci` target to include domain coverage:

```makefile
ci: ## Run full CI pipeline
	$(MAKE) lint
	$(MAKE) fmt-check
	$(MAKE) test
	$(MAKE) ci-domain
```

## Follow-up Issue

After merging, create an issue:
- Title: "test: increase overall test coverage from 91% to 95%"
- Body: List uncovered files with biggest gaps (render_commands.py 69%, serve_command.py 43%, engine.py 79%, extractor.py 80%)
- Label: enhancement

## Out of Scope

- Coverage upload to external services (Codecov, Coveralls)
- Matrix builds (multiple Python versions or OS)
- E2E tests in CI (subprocess tests excluded)
- Caching (uv cache, node_modules) — can be added later for speed
- Branch protection rules (manual GitHub settings)

## Success Criteria

1. `.github/workflows/ci.yml` exists and runs on PRs to main
2. CI runs lint, format check, tests, and coverage
3. CI fails if domain coverage drops below 100%
4. CI fails if overall coverage drops below 89%
5. `make ci` locally enforces the same thresholds
6. Follow-up issue created for reaching 95% target
