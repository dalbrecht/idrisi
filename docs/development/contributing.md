---
title: "Contributing"
description: "How to set up, develop, and submit changes to Voyages"
section: "development"
order: 1
---

# Contributing

## Getting Started

Fork the repository on GitHub at [https://github.com/dalbrecht/Voyages](https://github.com/dalbrecht/Voyages), then clone your fork locally:

```bash
git clone https://github.com/<your-username>/Voyages.git
cd Voyages
```

Initialize submodules and set up the development environment:

```bash
make repo-setup   # runs: git submodule update --init
make bootstrap    # runs: uv venv && uv pip install -e ".[dev]"
make dev          # runs: uv pip install -e ".[dev]"
```

## Branch Workflow

Use one branch per feature or fix. Branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b feat/my-feature
```

Branch naming conventions:

- `feat/<name>` — new feature
- `fix/<name>` — bug fix
- `docs/<name>` — documentation change

## Conventional Commits

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): subject
```

Valid types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

Examples:

```
feat(cli): add --format flag to map export command
fix(renderer): correct bounding box calculation for polar regions
docs(architecture): clarify layer dependency rules
test(domain): add coverage for Coordinates range validation
```

## Code Quality

Before submitting a PR, run the full CI check locally:

```bash
make ci
```

This runs the following checks in order:

**`make lint`** — static analysis and type checking:
```bash
uv run ruff check src tests && uv run mypy src
```
mypy runs in strict mode with the pydantic plugin enabled.

**`make fmt-check`** — formatting verification:
```bash
uv run ruff format --check src tests
```
Line length is 100 characters, targeting Python 3.12.

**`make test`** — test suite:
```bash
uv run pytest
```

All three checks must pass before opening a PR.

## Pull Requests

Open one PR per feature or fix. When your branch is ready:

```bash
make pr   # runs: gh pr create --fill
```

In the PR description:

- Summarize what changed and why
- Reference any related GitHub issues (e.g., `Closes #42`)
- Note any migration steps or breaking changes

## Code Style

Style is enforced automatically by [ruff](https://docs.astral.sh/ruff/):

- Line length: 100 characters
- Target Python version: 3.12
- Strict mypy typing required throughout

Auto-format before committing:

```bash
make fmt   # runs: uv run ruff format src tests
```

The CI check (`make fmt-check`) will fail if formatting is not applied.

## Getting Oriented

New to the codebase? See:

- [Architecture](architecture.md) — layer structure, design decisions, and the directory map
- [Testing](testing.md) — how tests are organized and how to run them
