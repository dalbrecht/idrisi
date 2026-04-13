# Rename Voyages → Idrisi

**Date:** 2026-04-13
**Status:** Approved

## Purpose

Rename the application from "Voyages" to "Idrisi" across code, packaging, UI, and active documentation. The repository has already been renamed on GitHub (`dalbrecht/Voyages` → `dalbrecht/idrisi`). This change brings the codebase in line. The project is pre-1.0, so no backwards-compatibility shims are required.

The new name honors Muhammad al-Idrisi (1100–1165), the Arab geographer and cartographer whose *Tabula Rogeriana* was one of the most accurate world maps of the medieval era. A short naming post lives under `docs/about/naming.md` and links to the [Wikipedia article](https://en.wikipedia.org/wiki/Muhammad_al-Idrisi).

## Scope

### In scope — rename

- **Python package:** `src/voyages/` → `src/idrisi/` (git mv)
- **Imports:** every `from voyages.X` / `import voyages.X` in `src/` and `tests/` → `idrisi.X`
- **Typer CLI app:** `name="voyages"` → `name="idrisi"` in `src/idrisi/cli/__init__.py`
- **Console script:** `voyages = "voyages.cli:app"` → `idrisi = "idrisi.cli:app"` in `pyproject.toml`
- **Package metadata:** `[project] name = "voyages"` → `name = "idrisi"`; mypy `[[tool.mypy.overrides]]` module paths
- **Default DB URL:** `sqlite:///voyages.db` → `sqlite:///idrisi.db` (no fallback)
- **Web package:** `voyages-web` → `idrisi-web` in `web/package.json`; lockfile regenerated
- **Web UI copy:** `<title>` in `web/index.html`, any on-screen "Voyages" in `web/src/`
- **Docs (active):** `README.md`, `docs/getting-started/`, `docs/guides/`, `docs/reference/`, `docs/album-import.md`, `docs/development/`
- **Build/infra:** `Makefile`, `.gitignore` entries that mention the old name
- **Server static output paths:** `src/voyages/server/static/` → `src/idrisi/server/static/` (follows package move)

### In scope — add

- **`docs/about/naming.md`** — ~200-word post on al-Idrisi (cartographer at the court of Roger II of Sicily, author of *Kitab Nuzhat al-Mushtaq* — "Book of Pleasant Journeys into Faraway Lands"), framing the rename as honoring a cartographer whose work was the travel-planning tool of its time. Includes a link to [https://en.wikipedia.org/wiki/Muhammad_al-Idrisi](https://en.wikipedia.org/wiki/Muhammad_al-Idrisi).
- **README.md link** to the naming post.

### Out of scope — intentionally untouched

- **`docs/superpowers/specs/*`** and **`docs/superpowers/plans/*`** — historical design/planning artifacts dated before the rename. Treated like commit messages: history is not rewritten.
- **`.claude/worktrees/*`** — stale local worktrees for unrelated in-flight branches.
- **Git history and past commit messages.**
- **External references** (uv cache, local databases in untracked paths).

## Approach

Single branch `chore/rename-to-idrisi`, single PR against `main`, executed in a fresh worktree at `.claude/worktrees/rename-to-idrisi`.

The rename is mechanical enough to execute in three commits for reviewability:

1. **`chore(rename): move python package and rewrite imports`** — `git mv src/voyages src/idrisi`, rewrite all `voyages` identifiers in Python source + tests, update `pyproject.toml` (name, console_script, mypy overrides).
2. **`chore(rename): update web package, CLI strings, and DB defaults`** — `web/package.json` name, typer app name, `sqlite:///voyages.db` → `sqlite:///idrisi.db`, regenerate `web/package-lock.json`, any UI copy in `web/src/`.
3. **`docs: rewrite active docs and add al-Idrisi naming post`** — README, `docs/getting-started/`, `docs/guides/`, `docs/reference/`, `docs/album-import.md`, `docs/development/`, new `docs/about/naming.md`.

## Verification

Before pushing:
- `make ci` green (ruff + mypy + ruff format --check + pytest 95% coverage)
- `make build-web` green (vite build writes to `src/idrisi/server/static/`)
- `voyages` command no longer present: `command -v voyages` returns nothing after `uv pip install -e .`
- `idrisi --help` works
- `grep -rE "voyages|Voyages|VOYAGES" src/ tests/ web/src/ web/index.html docs/getting-started/ docs/guides/ docs/reference/ docs/development/ docs/album-import.md docs/about/ README.md pyproject.toml Makefile .gitignore` returns zero matches (historical `docs/superpowers/` is excluded by design).

## Risks

- **Lockfile churn:** `web/package-lock.json` is regenerated, which is a large diff. Unavoidable with a package rename.
- **Lost CI cache:** `actions/setup-uv` cache keyed by `pyproject.toml`. First CI run after merge re-resolves; not a correctness issue.
- **Anyone with a local `voyages.db`** will appear to have "lost" their data. Documented in the naming post / README migration note: pre-1.0, one-line rename (`mv voyages.db idrisi.db`) restores.
