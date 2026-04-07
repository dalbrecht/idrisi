# GitHub Actions CI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a GitHub Actions CI workflow that enforces lint, format, tests, and coverage thresholds on PRs to main.

**Architecture:** Single workflow file triggered on PRs to main. Coverage config in pyproject.toml. Makefile targets updated to include coverage enforcement. Two coverage gates: 100% domain, 89% overall.

**Tech Stack:** GitHub Actions, pytest-cov, uv, ruff, mypy

**Spec:** `docs/superpowers/specs/2026-04-07-github-actions-ci-design.md`

---

### Task 1: Add coverage configuration to pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add coverage config**

In `pyproject.toml`, add after the `[tool.pytest.ini_options]` section:

```toml
[tool.coverage.run]
source = ["voyages"]

[tool.coverage.report]
show_missing = true
```

- [ ] **Step 2: Verify coverage works**

```bash
uv run pytest tests/domain/ --cov=voyages.domain -q
```

Expected: Coverage report shows 100% for domain.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "build: add coverage configuration to pyproject.toml"
```

---

### Task 2: Update Makefile with coverage enforcement

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Update test target to include coverage**

Change the `test` target from:

```makefile
test: ## Run pytest
	uv run pytest
```

to:

```makefile
test: ## Run tests with coverage (excludes e2e)
	uv run pytest -m "not e2e" --cov=voyages --cov-fail-under=89
```

Note: If the Makefile already has `-m "not e2e"` from PR #6, just add the `--cov` flags. Read the current file before editing.

- [ ] **Step 2: Add domain coverage target**

Add after the `test` target:

```makefile
ci-domain: ## Verify 100% domain test coverage
	uv run pytest tests/domain/ --cov=voyages.domain --cov-fail-under=100
```

- [ ] **Step 3: Update ci target to include domain coverage**

Change the `ci` target from:

```makefile
ci: ## Run full CI pipeline (lint + format check + test)
	$(MAKE) lint
	$(MAKE) fmt-check
	$(MAKE) test
```

to:

```makefile
ci: ## Run full CI pipeline (lint + format check + test + coverage)
	$(MAKE) lint
	$(MAKE) fmt-check
	$(MAKE) test
	$(MAKE) ci-domain
```

- [ ] **Step 4: Update .PHONY**

Add `ci-domain` to the `.PHONY` line. If `test-e2e` and `test-all` are already there (from PR #6), just append `ci-domain`.

- [ ] **Step 5: Verify locally**

```bash
make ci
```

Expected: lint passes, fmt-check passes, tests pass with coverage ≥89%, domain coverage = 100%.

- [ ] **Step 6: Commit**

```bash
git add Makefile
git commit -m "build: add coverage enforcement to Makefile targets"
```

---

### Task 3: Create GitHub Actions workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create the workflow file**

```bash
mkdir -p .github/workflows
```

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: true

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Node.js 18
        uses: actions/setup-node@v4
        with:
          node-version: "18"

      - name: Install system dependencies
        run: sudo apt-get update && sudo apt-get install -y libgeos-dev libproj-dev

      - name: Install Python dependencies
        run: make bootstrap

      - name: Build web frontend
        run: make build-web

      - name: Run CI pipeline
        run: make ci
```

- [ ] **Step 2: Verify the workflow file is valid YAML**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow for PRs to main

Runs lint (ruff + mypy), format check, tests with 89% overall
coverage floor, and 100% domain coverage enforcement."
```

---

### Task 4: Create coverage gap issue and PR

- [ ] **Step 1: Push branch and create PR**

```bash
git push -u origin <branch-name>
gh pr create \
  --title "ci: add GitHub Actions workflow with coverage enforcement" \
  --body "$(cat <<'EOF'
## Summary

- Add `.github/workflows/ci.yml` — runs on PRs to main
- Add coverage config to `pyproject.toml`
- Update `make test` to enforce 89% overall coverage
- Add `make ci-domain` to enforce 100% domain coverage
- Update `make ci` to run full pipeline including domain coverage

## CI Pipeline

1. Checkout with submodules
2. Python 3.12 + uv + Node.js 18 + system deps (GEOS, PROJ)
3. `make bootstrap` + `make build-web`
4. `make ci` (lint + format + tests@89% + domain@100%)

## Test plan

- [x] `make ci` passes locally
- [ ] CI runs on this PR (self-testing)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 2: Create follow-up issue for coverage targets**

```bash
gh issue create \
  --title "test: increase overall test coverage from 89% to 95%" \
  --body "$(cat <<'EOF'
## Context

CI now enforces 89% overall coverage (current baseline) and 100% domain coverage.
The project target is 95% overall. Key files with coverage gaps:

| File | Current | Gap |
|------|---------|-----|
| `cli/serve_command.py` | 43% | Not tested (starts uvicorn) |
| `cli/render_commands.py` | 69% | Service wiring untested |
| `infrastructure/renderer/engine.py` | 79% | Region/route renderers partially tested |
| `infrastructure/exif/extractor.py` | 80% | Edge cases in GPS parsing |
| `cli/place_commands.py` | 86% | Service wiring untested |
| `cli/trip_commands.py` | 85% | Service wiring untested |
| `cli/project_commands.py` | 90% | Service wiring untested |
| `server/routes/regions.py` | 82% | Some routes untested |
| `server/routes/render.py` | 81% | Region/route render routes |
| `infrastructure/db/repository.py` | 91% | Trip save/stop management |

## Plan

Increase `--cov-fail-under` in Makefile as coverage improves. Target: 95%.
EOF
)"
```
