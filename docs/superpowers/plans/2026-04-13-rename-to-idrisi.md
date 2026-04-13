# Rename Voyages → Idrisi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the application from "Voyages" to "Idrisi" across code, packaging, UI, and active documentation. Add a naming-origin post that links to the Wikipedia article about Muhammad al-Idrisi.

**Architecture:** Pure rename — no behavioral changes. Executed in a single worktree on branch `chore/rename-to-idrisi`, structured as five atomic commits so each leaves the repo green. Historical `docs/superpowers/specs/*` and `docs/superpowers/plans/*` are NOT touched. Pre-1.0 — no compat fallback for the old default DB path.

**Tech Stack:** Python (uv, hatchling, typer, FastAPI, pytest, mypy, ruff), Svelte + Vite web frontend, Makefile-driven workflow.

**Spec:** `docs/superpowers/specs/2026-04-13-rename-to-idrisi-design.md`

---

## Working Directory

All commands run from `.claude/worktrees/rename-to-idrisi` unless otherwise specified. Branch is `chore/rename-to-idrisi`.

```bash
cd /Users/donaldalbrecht/Projects/Voyages/.claude/worktrees/rename-to-idrisi
git status  # should show: On branch chore/rename-to-idrisi
```

---

## Task 1: Move Python package and rewrite imports

**Goal:** Move `src/voyages/` → `src/idrisi/`, rewrite every `voyages` identifier in Python source + tests, update `pyproject.toml`, update CLI strings, update default DB URL. After this task, `make ci` passes.

**Files affected:**
- Move: `src/voyages/` → `src/idrisi/`
- Modify: every `.py` file under `src/` and `tests/` that references `voyages`
- Modify: `pyproject.toml` ([project] name, [project.scripts], [[tool.mypy.overrides]] paths, description)

- [ ] **Step 1: Move the package directory**

```bash
git mv src/voyages src/idrisi
git status  # should show renames
```

- [ ] **Step 2: Rewrite Python imports and identifiers in src/**

Use `perl -i -pe` (not `sed`) because macOS BSD sed does not support `\b` word boundaries:

```bash
find src -name '*.py' -print0 | xargs -0 perl -i -pe 's/\bvoyages\b/idrisi/g; s/\bVoyages\b/Idrisi/g'
```

Word-boundary matching keeps substrings safe (none exist today, but it's the right tool).

- [ ] **Step 3: Rewrite Python imports and identifiers in tests/**

```bash
find tests -name '*.py' -print0 | xargs -0 perl -i -pe 's/\bvoyages\b/idrisi/g; s/\bVoyages\b/Idrisi/g'
```

- [ ] **Step 4: Update default DB URL strings in renamed package**

The `_DB_URL` constants in each `src/idrisi/cli/*_commands.py` and in `src/idrisi/server/__init__.py:create_app` still contain `sqlite:///voyages.db`. The sed in steps 2-3 only rewrites identifiers, not inside string literals (word-boundary match matches `voyages` inside the string too — but verify):

```bash
grep -rn "voyages.db\|sqlite:///voyages" src/idrisi/ tests/
```

Expected: zero matches (the word-boundary perl sub in step 2 already caught them — `voyages` in `sqlite:///voyages.db` and `voyages.db` are word-boundary matches). If any remain, fix with:

```bash
grep -rl "voyages\.db\|sqlite:///voyages" src/idrisi/ tests/ | xargs perl -i -pe 's/voyages\.db/idrisi.db/g; s{sqlite:///voyages}{sqlite:///idrisi}g'
```

- [ ] **Step 5: Update pyproject.toml**

Edit `pyproject.toml`:

Change `[project] name = "voyages"` → `name = "idrisi"`.

Leave `description` unchanged — the project is still a map generation toolbox for travel cartography; the name is the only thing changing.

Change `[project.scripts]`:
```toml
[project.scripts]
idrisi = "idrisi.cli:app"
```

Change any `[[tool.mypy.overrides]]` that has `module = ["voyages.*"]` → `module = ["idrisi.*"]`. Check with:

```bash
grep -A 1 'tool.mypy.overrides' pyproject.toml
```

Also check `[tool.coverage.run]` / `[tool.coverage.report]` / `[tool.pytest.ini_options]` for `voyages` source paths — update if present.

- [ ] **Step 6: Verify no stale `voyages` references remain in Python code or pyproject**

```bash
grep -rnE "voyages|Voyages|VOYAGES" src/ tests/ pyproject.toml
```

Expected: zero matches (binary `.pyc` cache files are acceptable false positives; only source file hits count).

> **Note:** Use an unbounded grep (no `\b` word boundaries) — word-boundary patterns miss compound identifiers like `VoyagesError` or method names like `test_help_shows_voyages_description`.

- [ ] **Step 7: Reinstall and run full CI locally**

```bash
uv pip install -e ".[dev]"
uv run ruff check src tests
uv run mypy src
uv run ruff format --check src tests
uv run pytest -m "not e2e and not macos" --cov=idrisi --cov-fail-under=95 -q
```

Expected: all green. If `ruff format --check` fails, run `uv run ruff format src tests` and re-check.

- [ ] **Step 8: Verify the new CLI installs and help works**

```bash
uv run idrisi --help
```

Expected: the typer help output shows `Usage: idrisi [OPTIONS] COMMAND [ARGS]...` and lists `album`, `place`, `project`, `trip`, `import`, `render`, `serve`.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
chore(rename): move python package to idrisi and rewrite imports

- git mv src/voyages → src/idrisi
- Rewrite all voyages/Voyages identifiers in src/ and tests/
- pyproject.toml: project name, console_script, mypy overrides
- Default DB URL: sqlite:///voyages.db → sqlite:///idrisi.db
- Typer app name: voyages → idrisi

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Update web package and UI copy

**Goal:** Rename `voyages-web` → `idrisi-web`, retarget the Vite build output to the renamed Python package's static dir, update UI copy. After this task, `make build-web` produces assets in `src/idrisi/server/static/`.

**Files affected:**
- Modify: `web/package.json`
- Modify: `web/package-lock.json` (regenerated)
- Modify: `web/vite.config.ts`
- Modify: `web/index.html`
- Modify: `web/src/App.svelte`
- Modify: any other `web/src/**/*.svelte` / `web/src/**/*.ts` with Voyages copy

- [ ] **Step 1: Update web/package.json name**

Edit `web/package.json`:
```json
{
  "name": "idrisi-web",
  ...
}
```

- [ ] **Step 2: Update Vite build outDir**

Edit `web/vite.config.ts`:
```ts
build: {
  outDir: '../src/idrisi/server/static',
  emptyOutDir: true,
},
```

- [ ] **Step 3: Update UI copy**

Edit `web/index.html`:
```html
<title>Idrisi</title>
```

Edit `web/src/App.svelte` (line 18):
```html
<h1>Idrisi</h1>
```

Scan for any other occurrences:
```bash
grep -rn "voyages\|Voyages" web/src/ web/index.html
```

Fix each match. Use `Idrisi` for display copy, `idrisi` for package/URL-style tokens.

- [ ] **Step 4: Regenerate lockfile**

```bash
cd web
rm -rf node_modules package-lock.json
npm install
cd ..
```

A full `npm install` (not `--package-lock-only`) is required to include all platform-optional bindings for rolldown (the prior vite-8 merge had this same gotcha).

- [ ] **Step 5: Build and verify output**

```bash
cd web && npm run build && cd ..
ls src/idrisi/server/static/
```

Expected: `index.html` and an `assets/` directory with hashed JS + CSS.

- [ ] **Step 6: Verify no stale references in web/**

```bash
grep -rnE "voyages|Voyages" web/src/ web/index.html web/vite.config.ts web/package.json
```

Expected: zero matches. `web/package-lock.json` is allowed to have no matches either (it's a fresh generate with the new name).

- [ ] **Step 7: Commit**

```bash
git add web/ src/idrisi/server/static/
git commit -m "$(cat <<'EOF'
chore(rename): update web package and UI copy to Idrisi

- web/package.json: voyages-web → idrisi-web
- web/vite.config.ts outDir → src/idrisi/server/static
- UI copy in index.html and App.svelte
- Regenerated package-lock.json with all platform bindings

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Update Makefile and .gitignore

**Goal:** Rewrite build/CI scripts to reference the renamed package.

**Files affected:**
- Modify: `Makefile`
- Modify: `.gitignore`

- [ ] **Step 1: Update Makefile**

Edit `Makefile`. Apply these substitutions (preserving everything else):

- `test:` target: `--cov=voyages` → `--cov=idrisi`
- `serve:` target: `voyages.server:create_app` → `idrisi.server:create_app`
- `run:` target: `uv run voyages` → `uv run idrisi`
- `clean:` target: `rm -rf src/voyages/server/static` → `rm -rf src/idrisi/server/static`
- `ci-domain:` target: `--cov=voyages.domain` → `--cov=idrisi.domain`

Quick reference — run this to find remaining spots (should be five lines):
```bash
grep -n "voyages" Makefile
```

After edits:
```bash
grep -n "voyages\|Voyages" Makefile
```

Expected: zero matches.

- [ ] **Step 2: Update .gitignore**

```bash
grep -n "voyages" .gitignore
```

For each match (the three lines are `voyages.db` and `voyages.db-journal` style entries under a comment that mentions "Voyages"), replace `voyages` with `idrisi` and `Voyages` with `Idrisi`.

- [ ] **Step 3: Run full CI**

```bash
make ci
make build-web
```

Expected: both green.

- [ ] **Step 4: Commit**

```bash
git add Makefile .gitignore
git commit -m "$(cat <<'EOF'
chore(rename): update Makefile and .gitignore for idrisi

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Rewrite active documentation

**Goal:** Update every user-facing doc to reflect the new name. Historical specs/plans under `docs/superpowers/` are deliberately left alone.

**Files affected:**
- Modify: `README.md`
- Modify: every file under `docs/getting-started/`
- Modify: every file under `docs/guides/`
- Modify: every file under `docs/reference/`
- Modify: `docs/album-import.md`
- Modify: every file under `docs/development/`

- [ ] **Step 1: Rewrite Voyages/voyages in all active doc files**

```bash
find README.md docs/getting-started docs/guides docs/reference docs/album-import.md docs/development -type f \( -name '*.md' -o -name '*.txt' \) -print0 | xargs -0 perl -i -pe 's/\bvoyages\b/idrisi/g; s/\bVoyages\b/Idrisi/g'
```

- [ ] **Step 2: Review a representative doc manually**

Open `README.md` and skim the first 50 lines. Look for:
- Broken sentences ("installing voyages" became "installing idrisi" — grammatically fine)
- Shell commands still work (`voyages list` became `idrisi list`)
- URLs in code fences haven't been mangled (word-boundary sed shouldn't touch them, but confirm)

Sample:
```bash
head -60 README.md
```

Fix any awkward phrasing inline. The goal is "reads naturally," not "passes the grep."

- [ ] **Step 3: Check every other rewritten doc for obvious breakage**

```bash
for f in $(find README.md docs/getting-started docs/guides docs/reference docs/album-import.md docs/development -type f -name '*.md'); do
  echo "=== $f ==="
  head -20 "$f"
done | less
```

This is a visual scan — just make sure each doc still opens with a coherent first paragraph.

- [ ] **Step 4: Verify no residual references in rewritten scope**

```bash
grep -rnE "voyages|Voyages|VOYAGES" README.md docs/getting-started docs/guides docs/reference docs/album-import.md docs/development
```

Expected: zero matches.

- [ ] **Step 5: Confirm historical docs are untouched**

```bash
git status docs/superpowers/
```

Expected: no changes in `docs/superpowers/plans/` or `docs/superpowers/specs/` from this task's edits (the new rename spec was committed earlier in the branch and is allowed).

- [ ] **Step 6: Commit**

```bash
git add README.md docs/getting-started docs/guides docs/reference docs/album-import.md docs/development
git commit -m "$(cat <<'EOF'
docs(rename): rewrite active docs for Idrisi

Leaves docs/superpowers/specs and docs/superpowers/plans untouched as
historical artifacts.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Add the al-Idrisi naming post

**Goal:** Add `docs/about/naming.md` explaining the name origin, and link it from `README.md`.

**Files affected:**
- Create: `docs/about/naming.md`
- Modify: `README.md` (add link)

- [ ] **Step 1: Create the naming post**

Write `docs/about/naming.md` with this content:

```markdown
# Why "Idrisi"?

Idrisi is named after [Muhammad al-Idrisi](https://en.wikipedia.org/wiki/Muhammad_al-Idrisi) (1100–1165), an Arab geographer and cartographer at the court of King Roger II of Sicily.

Al-Idrisi spent roughly fifteen years compiling what became the *Kitab Nuzhat al-Mushtaq* — "The Book of Pleasant Journeys into Faraway Lands" — accompanying an engraved silver planisphere and a set of seventy regional maps known collectively as the *Tabula Rogeriana*. The result was one of the most accurate world maps produced in the medieval era, synthesizing Greek geographic texts, Islamic scholarship, and firsthand accounts collected from travelers who passed through the Sicilian court.

The *Tabula* is, in a sense, exactly what a modern trip-planning tool is: a visual reference built by gathering accounts from people who've been somewhere, cross-referencing them, and producing something a traveler can actually use to plan their journey. The methodology is nearly a millennium old, and the name is a nod to a cartographer whose work was the travel-planning infrastructure of its time.

## Further reading

- [Muhammad al-Idrisi — Wikipedia](https://en.wikipedia.org/wiki/Muhammad_al-Idrisi)
- [Tabula Rogeriana — Wikipedia](https://en.wikipedia.org/wiki/Tabula_Rogeriana)
```

- [ ] **Step 2: Add a link from README.md**

Near the top of `README.md` (under the project title/blurb, before the installation section), add:

```markdown
The name comes from the 12th-century geographer Muhammad al-Idrisi — see [About the name](docs/about/naming.md).
```

Exact placement is the reader's call: after the short description but before "Installation" or equivalent.

- [ ] **Step 3: Final sanity check**

```bash
grep -rnE "\bvoyages\b|\bVoyages\b|\bVOYAGES\b" src/ tests/ web/src/ web/index.html web/vite.config.ts web/package.json docs/getting-started docs/guides docs/reference docs/about docs/album-import.md docs/development README.md pyproject.toml Makefile .gitignore
```

Expected: zero matches.

```bash
grep -rnE "\bvoyages\b|\bVoyages\b" docs/superpowers/
```

Expected: matches in historical specs/plans (this is correct — those are left alone).

- [ ] **Step 4: Run full CI and web build one final time**

```bash
make ci
make build-web
```

Expected: green.

- [ ] **Step 5: Commit**

```bash
git add docs/about/naming.md README.md
git commit -m "$(cat <<'EOF'
docs: add al-Idrisi naming origin post

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Push and open the PR

- [ ] **Step 1: Push the branch**

```bash
git push -u origin chore/rename-to-idrisi
```

- [ ] **Step 2: Open the PR**

```bash
gh pr create --title "chore: rename Voyages → Idrisi" --body "$(cat <<'EOF'
## Summary

Renames the application from "Voyages" to "Idrisi" across code, packaging, UI, and active documentation. Adds a naming-origin post linking to the Wikipedia article about Muhammad al-Idrisi (1100–1165), the 12th-century Arab cartographer this project is named for.

Pre-1.0 rename — no compat fallback for the old default DB path. Users with a local `voyages.db` can `mv voyages.db idrisi.db`.

## Commits

1. Python package moved `src/voyages/` → `src/idrisi/`; all imports rewritten; `pyproject.toml`, CLI name, and default DB URL updated.
2. Web package renamed to `idrisi-web`; Vite outDir retargeted; UI copy updated; lockfile regenerated.
3. `Makefile` and `.gitignore` updated.
4. Active documentation rewritten (historical `docs/superpowers/specs|plans/` left intact).
5. Added `docs/about/naming.md` and README link.

## Test plan

- [ ] CI green (lint, mypy, format, pytest ≥95%, web build)
- [ ] `idrisi --help` works locally
- [ ] `grep -rE "\bvoyages\b|\bVoyages\b" src/ tests/ web/src/ README.md pyproject.toml Makefile` returns zero matches

Spec: `docs/superpowers/specs/2026-04-13-rename-to-idrisi-design.md`
Plan: `docs/superpowers/plans/2026-04-13-rename-to-idrisi.md`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 3: Watch CI and merge when green**

```bash
gh pr checks --watch
```

When CI passes, merge with:
```bash
gh pr merge --merge --delete-branch
```
