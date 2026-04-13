# Marketing Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a static marketing site at `idrisi.donalbrecht.com` built with Astro, deployed on Cloudflare Pages, with a landing page and an `/about/naming` page sourced from `docs/about/naming.md`.

**Architecture:** New `site/` directory in the repo. Astro builds static HTML/CSS/JS to `site/dist`. A short Python script (`site/scripts/build-gallery.py`) renders example map PNGs committed to `site/public/gallery/`. Cloudflare Pages is wired to GitHub and builds `cd site && npm ci && npm run build` on every push to `main`. Custom domain configured in Cloudflare.

**Tech Stack:** Astro 5.x + TypeScript, hand-written CSS (no Tailwind), vanilla JS for one click-to-copy button, Python (uses the main `idrisi` package) for gallery generation.

**Spec:** `docs/superpowers/specs/2026-04-13-marketing-site-design.md`

---

## Working Directory

All commands run from the marketing site worktree:

```bash
cd /Users/donaldalbrecht/Projects/Voyages/.claude/worktrees/marketing-site
git status  # should show: On branch feat/marketing-site
```

---

## Task 1: Scaffold Astro site

**Goal:** A minimal Astro project under `site/` that builds successfully with no content yet.

**Files:**
- Create: `site/package.json`
- Create: `site/astro.config.mjs`
- Create: `site/tsconfig.json`
- Create: `site/.gitignore`
- Create: `site/src/pages/index.astro` (placeholder)

- [ ] **Step 1: Create `site/package.json`**

```json
{
  "name": "idrisi-site",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "prebuild": "node scripts/copy-naming.mjs"
  },
  "devDependencies": {
    "astro": "^5.0.0",
    "@astrojs/sitemap": "^3.0.0",
    "typescript": "^5.7.0"
  }
}
```

Note: `prebuild` will be populated by a script created in Task 5. The script file need not exist for this task (npm only invokes `prebuild` when `build` is run).

- [ ] **Step 2: Create `site/astro.config.mjs`**

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://idrisi.donalbrecht.com',
  integrations: [sitemap()],
  build: {
    format: 'directory',
  },
});
```

- [ ] **Step 3: Create `site/tsconfig.json`**

```json
{
  "extends": "astro/tsconfigs/strict",
  "include": ["src/**/*.astro", "src/**/*.ts", ".astro/**/*.d.ts"]
}
```

- [ ] **Step 4: Create `site/.gitignore`**

```
node_modules/
dist/
.astro/
```

- [ ] **Step 5: Create placeholder `site/src/pages/index.astro`**

```astro
---
---
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Idrisi</title></head>
  <body><h1>Idrisi (scaffold)</h1></body>
</html>
```

- [ ] **Step 6: Install and verify build**

```bash
cd site
npm install
npm run build
ls dist
cd ..
```

Expected: `dist/index.html` exists. `npm install` may take 30-60s. `npm run build` will run `prebuild` (the node script doesn't exist yet) — if that errors, delete the `"prebuild"` line from package.json temporarily and add it back in Task 5.

Actually, cleaner: add `"prebuild"` line in Task 5 when the script is created, not here. Remove `"prebuild": "node scripts/copy-naming.mjs"` from `site/package.json` for now. You'll add it back in Task 5.

- [ ] **Step 7: Commit**

```bash
git add site/
git commit -m "$(cat <<'EOF'
feat(site): scaffold Astro project

Empty Astro 5 scaffold with sitemap integration. Further content
added in subsequent commits.

Refs #22

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Base layout, styles, compass motif, favicon, OG image

**Goal:** A shared `Base.astro` layout containing head metadata (title, description, OG, favicon) and the site's visual system. Placeholder `index.astro` and `404.astro` that render using the layout.

**Files:**
- Create: `site/src/styles/global.css`
- Create: `site/src/components/Compass.astro`
- Create: `site/src/layouts/Base.astro`
- Create: `site/public/favicon.svg`
- Create: `site/public/og.svg`
- Create: `site/src/pages/404.astro`
- Modify: `site/src/pages/index.astro`

- [ ] **Step 1: Create `site/src/styles/global.css`**

```css
:root {
  --color-bg: #ffffff;
  --color-text: #111217;
  --color-muted: #5a5d66;
  --color-accent: #8b6b2e;
  --color-border: #e6e8ec;
  --color-code-bg: #f6f7f9;

  --font-serif: "EB Garamond", Georgia, "Times New Roman", serif;
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

  --measure: 68ch;
  --space-1: 0.5rem;
  --space-2: 1rem;
  --space-3: 1.5rem;
  --space-4: 2.5rem;
  --space-5: 4rem;
  --space-6: 6rem;
}

*, *::before, *::after { box-sizing: border-box; }

html {
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: var(--color-bg);
  line-height: 1.55;
}

body { margin: 0; }

h1, h2, h3 {
  font-family: var(--font-serif);
  font-weight: 500;
  line-height: 1.15;
  margin: 0;
}
h1 { font-size: clamp(2.25rem, 4vw, 3.5rem); letter-spacing: -0.01em; }
h2 { font-size: clamp(1.75rem, 3vw, 2.25rem); }
h3 { font-size: 1.125rem; font-weight: 600; font-family: var(--font-sans); }

p { margin: 0; max-width: var(--measure); }

a {
  color: var(--color-text);
  text-decoration: underline;
  text-decoration-color: var(--color-accent);
  text-underline-offset: 3px;
  text-decoration-thickness: 1px;
}
a:hover { text-decoration-thickness: 2px; }

code, pre {
  font-family: var(--font-mono);
  font-size: 0.9em;
}
pre {
  background: var(--color-code-bg);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: var(--space-2);
  overflow-x: auto;
}
code:not(pre code) {
  background: var(--color-code-bg);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 0.1em 0.35em;
}

.container {
  max-width: 64rem;
  margin: 0 auto;
  padding: 0 var(--space-3);
}

.eyebrow {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-accent);
  font-weight: 600;
}

.muted { color: var(--color-muted); }

.section {
  padding: var(--space-6) 0;
}
.section:not(:last-child) {
  border-bottom: 1px solid var(--color-border);
}

.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0;
  margin: -1px; overflow: hidden; clip: rect(0,0,0,0);
  white-space: nowrap; border: 0;
}
```

- [ ] **Step 2: Create `site/src/components/Compass.astro`**

```astro
---
interface Props {
  size?: number;
  title?: string;
}
const { size = 16, title = "compass" } = Astro.props;
---
<svg
  xmlns="http://www.w3.org/2000/svg"
  width={size}
  height={size}
  viewBox="0 0 24 24"
  role="img"
  aria-label={title}
  fill="none"
  stroke="currentColor"
  stroke-width="1.25"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  <circle cx="12" cy="12" r="9" />
  <polygon points="12,4 14,12 12,20 10,12" fill="currentColor" stroke="none" />
  <polygon points="4,12 12,10 20,12 12,14" fill="currentColor" stroke="none" opacity="0.45" />
</svg>
```

- [ ] **Step 3: Create `site/public/favicon.svg`**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="#ffffff"/>
  <g transform="translate(4 4)" stroke="#8b6b2e" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="11"/>
    <polygon points="12,3 14.5,12 12,21 9.5,12" fill="#8b6b2e" stroke="none"/>
    <polygon points="3,12 12,9.5 21,12 12,14.5" fill="#8b6b2e" stroke="none" opacity="0.45"/>
  </g>
</svg>
```

- [ ] **Step 4: Create `site/public/og.svg`**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <rect width="1200" height="630" fill="#ffffff"/>
  <g transform="translate(100 265)" stroke="#8b6b2e" stroke-width="2" fill="none">
    <circle cx="50" cy="50" r="46"/>
    <polygon points="50,12 60,50 50,88 40,50" fill="#8b6b2e" stroke="none"/>
    <polygon points="12,50 50,40 88,50 50,60" fill="#8b6b2e" stroke="none" opacity="0.45"/>
  </g>
  <text x="220" y="290" font-family="EB Garamond, Georgia, serif" font-size="72" fill="#111217" font-weight="500">Idrisi</text>
  <text x="220" y="355" font-family="Inter, -apple-system, sans-serif" font-size="28" fill="#5a5d66">Travel cartography for modern trips.</text>
  <text x="220" y="400" font-family="Inter, -apple-system, sans-serif" font-size="20" fill="#8b6b2e" letter-spacing="2">A PYTHON TOOLBOX · CLI-FIRST · OPEN SOURCE</text>
</svg>
```

- [ ] **Step 5: Create `site/src/layouts/Base.astro`**

```astro
---
import "../styles/global.css";

interface Props {
  title: string;
  description?: string;
  path?: string;
}

const {
  title,
  description = "A Python toolbox that renders maps from your photos and itineraries.",
  path = "/",
} = Astro.props;

const canonical = new URL(path, Astro.site).toString();
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <meta name="description" content={description} />
    <link rel="canonical" href={canonical} />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />

    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
    <meta property="og:type" content="website" />
    <meta property="og:url" content={canonical} />
    <meta property="og:image" content={new URL("/og.svg", Astro.site).toString()} />
    <meta name="twitter:card" content="summary_large_image" />

    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&family=Inter:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <slot />
  </body>
</html>
```

- [ ] **Step 6: Replace `site/src/pages/index.astro` with a minimal version using Base**

```astro
---
import Base from "../layouts/Base.astro";
---
<Base title="Idrisi — Travel cartography for modern trips." path="/">
  <main class="container">
    <div class="section">
      <p class="eyebrow">idrisi</p>
      <h1>Travel cartography for modern trips.</h1>
      <p class="muted">More content coming in the next tasks.</p>
    </div>
  </main>
</Base>
```

- [ ] **Step 7: Create `site/src/pages/404.astro`**

```astro
---
import Base from "../layouts/Base.astro";
import Compass from "../components/Compass.astro";
---
<Base title="Not found — Idrisi" description="The page you were looking for doesn't exist." path="/404">
  <main class="container">
    <div class="section" style="text-align:center">
      <p class="eyebrow" style="display:inline-flex;align-items:center;gap:0.5em">
        <Compass size={14} /> idrisi
      </p>
      <h1 style="margin-top:var(--space-2)">Off the map.</h1>
      <p class="muted" style="margin:var(--space-3) auto 0">
        That page doesn't exist. Try the <a href="/">landing page</a>.
      </p>
    </div>
  </main>
</Base>
```

- [ ] **Step 8: Build and preview**

```bash
cd site
npm run build
npm run preview -- --host 127.0.0.1 --port 4321 &
sleep 2
curl -s http://127.0.0.1:4321/ | grep -i "travel cartography"
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4321/404
kill %1
cd ..
```

Expected: build succeeds with no errors, the `curl` for `/` prints the heading line, and the 404 page returns 404 (Astro's preview server maps 404.html to actual 404 responses).

- [ ] **Step 9: Commit**

```bash
git add site/
git commit -m "$(cat <<'EOF'
feat(site): base layout, styles, favicon, OG image, 404

Sets the visual system (sepia accent over white ground, serif display
type, sans body) and provides shared head metadata for every page.

Refs #22

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Hero + Features + Quickstart + Footer

**Goal:** All landing content except the gallery (which needs generated images — Task 4). After this task, the landing renders the full top-to-footer scroll minus the gallery section.

**Files:**
- Create: `site/src/components/Hero.astro`
- Create: `site/src/components/Features.astro`
- Create: `site/src/components/Quickstart.astro`
- Create: `site/src/components/Footer.astro`
- Modify: `site/src/pages/index.astro`

- [ ] **Step 1: Create `site/src/components/Hero.astro`**

```astro
---
import Compass from "./Compass.astro";
---
<section class="hero section">
  <p class="eyebrow" aria-label="idrisi">
    <Compass size={14} />
    <span>idrisi</span>
  </p>
  <h1>Travel cartography for modern trips.</h1>
  <p class="sub muted">A Python toolbox that renders maps from your photos and itineraries.</p>

  <div class="cta-row">
    <div class="install" role="group" aria-label="Install command">
      <code id="install-cmd">pip install idrisi</code>
      <button class="copy" type="button" aria-label="Copy install command" data-copy-target="install-cmd">Copy</button>
    </div>
    <a class="docs-link" href="https://github.com/dalbrecht/idrisi">Read the docs →</a>
  </div>
</section>

<style>
  .hero { padding-top: var(--space-6); padding-bottom: var(--space-5); }
  .hero .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.5em;
    margin-bottom: var(--space-3);
  }
  .hero h1 { max-width: 22ch; }
  .hero .sub { margin-top: var(--space-2); font-size: 1.125rem; max-width: 52ch; }
  .cta-row {
    margin-top: var(--space-4);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-3);
  }
  .install {
    display: inline-flex;
    align-items: stretch;
    background: var(--color-code-bg);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    overflow: hidden;
  }
  .install code {
    padding: 0.5rem 0.9rem;
    background: transparent;
    border: none;
    border-radius: 0;
  }
  .copy {
    font-family: var(--font-sans);
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0 0.9rem;
    border: none;
    border-left: 1px solid var(--color-border);
    background: #fff;
    color: var(--color-accent);
    cursor: pointer;
  }
  .copy:hover { background: var(--color-code-bg); }
  .copy.copied { color: var(--color-text); }
  .docs-link {
    font-weight: 500;
    text-decoration: none;
    border-bottom: 1px solid var(--color-accent);
    padding-bottom: 2px;
  }
</style>

<script>
  document.querySelectorAll<HTMLButtonElement>("button[data-copy-target]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.copyTarget!;
      const el = document.getElementById(id);
      if (!el) return;
      try {
        await navigator.clipboard.writeText(el.textContent ?? "");
        const original = btn.textContent;
        btn.textContent = "Copied";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = original;
          btn.classList.remove("copied");
        }, 1400);
      } catch {
        /* clipboard blocked — fall through silently */
      }
    });
  });
</script>
```

- [ ] **Step 2: Create `site/src/components/Features.astro`**

```astro
---
const features = [
  {
    title: "CLI-first",
    body: "A Typer-based command line for managing places, trips, projects, and renders.",
  },
  {
    title: "macOS Photos import",
    body: "Read a Photos.app album and cluster geotagged shots into logical stops with DBSCAN.",
  },
  {
    title: "Multiple map types",
    body: "Travel maps, region maps, and route maps — each tuned for a different story.",
  },
  {
    title: "Pluggable styles",
    body: "YAML-defined styles change colors, fonts, and decorations without touching code.",
  },
  {
    title: "Python library",
    body: "Hack on the primitives. Every CLI command is thin glue over documented services.",
  },
  {
    title: "Local web preview",
    body: "`idrisi serve` spins up a FastAPI + Svelte UI for editing projects interactively.",
  },
];
---
<section class="features section">
  <h2>What you get.</h2>
  <div class="grid">
    {features.map((f) => (
      <article class="feature">
        <h3>{f.title}</h3>
        <p class="muted">{f.body}</p>
      </article>
    ))}
  </div>
</section>

<style>
  .features h2 { max-width: 20ch; margin-bottom: var(--space-4); }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
    gap: var(--space-4) var(--space-3);
  }
  .feature h3 { margin-bottom: var(--space-1); }
  .feature p { font-size: 0.95rem; }
</style>
```

- [ ] **Step 3: Create `site/src/components/Quickstart.astro`**

```astro
---
---
<section class="quickstart section">
  <h2>Install and run.</h2>
  <p class="muted">Two common entry points — a full programmatic path and an interactive path.</p>

  <pre aria-label="Shell session"><code><span class="c"># 1. Install</span>
pip install idrisi

<span class="c"># 2a. Import a macOS Photos album and render it (macOS only)</span>
idrisi album import "Japan 2024"
idrisi render "Japan 2024" --style default

<span class="c"># 2b. Or launch the interactive web UI</span>
idrisi serve
<span class="c"># → http://localhost:8080</span>
</code></pre>

  <p class="muted small">
    See the <a href="https://github.com/dalbrecht/idrisi/tree/main/docs">full docs on GitHub</a>
    for the CLI reference, map types, and style options.
  </p>
</section>

<style>
  .quickstart h2 { margin-bottom: var(--space-2); }
  .quickstart .muted { margin-bottom: var(--space-3); }
  .quickstart pre { margin: 0 0 var(--space-3) 0; }
  .quickstart .c { color: var(--color-accent); }
  .small { font-size: 0.875rem; }
</style>
```

- [ ] **Step 4: Create `site/src/components/Footer.astro`**

```astro
---
import Compass from "./Compass.astro";
---
<footer class="site-footer">
  <div class="container inner">
    <p class="brand">
      <Compass size={14} />
      <span>Idrisi</span>
    </p>
    <nav aria-label="Footer">
      <a href="https://github.com/dalbrecht/idrisi">GitHub</a>
      <a href="https://github.com/dalbrecht/idrisi/tree/main/docs">Docs</a>
      <a href="/about/naming">About the name</a>
    </nav>
    <p class="license muted">AGPL-3.0-or-later · © 2026 Don Albrecht</p>
  </div>
</footer>

<style>
  .site-footer {
    border-top: 1px solid var(--color-border);
    padding: var(--space-4) 0 var(--space-5);
    margin-top: var(--space-5);
  }
  .inner {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
  }
  .brand {
    display: inline-flex;
    align-items: center;
    gap: 0.5em;
    font-weight: 600;
    margin: 0;
  }
  nav {
    display: flex;
    gap: var(--space-3);
    flex-wrap: wrap;
  }
  nav a { text-decoration: none; border-bottom: 1px solid var(--color-accent); }
  .license { font-size: 0.85rem; margin: 0; }
</style>
```

- [ ] **Step 5: Wire everything into `site/src/pages/index.astro`**

Replace the current contents with:

```astro
---
import Base from "../layouts/Base.astro";
import Hero from "../components/Hero.astro";
import Features from "../components/Features.astro";
import Quickstart from "../components/Quickstart.astro";
import Footer from "../components/Footer.astro";
---
<Base
  title="Idrisi — Travel cartography for modern trips."
  description="A Python toolbox that renders maps from your photos and itineraries."
  path="/"
>
  <main class="container">
    <Hero />
    <section class="intro section">
      <h2>A small toolbox for making maps of journeys.</h2>
      <p class="muted">
        Idrisi turns a list of places — typed in, imported from a Photos album, or assembled
        interactively — into a rendered map you can print, share, or keep for yourself.
        It's a CLI, a Python library, and a local web UI, in that order of emphasis.
      </p>
    </section>
    <Features />
    <Quickstart />
  </main>
  <Footer />
</Base>

<style>
  .intro h2 { max-width: 28ch; margin-bottom: var(--space-2); }
</style>
```

- [ ] **Step 6: Build and smoke-test**

```bash
cd site
npm run build
grep -q "Travel cartography for modern trips" dist/index.html
grep -q "pip install idrisi" dist/index.html
grep -q "About the name" dist/index.html
cd ..
```

All three `grep -q` commands should succeed (no output, exit 0).

- [ ] **Step 7: Commit**

```bash
git add site/
git commit -m "$(cat <<'EOF'
feat(site): hero, features, quickstart, footer

Everything on the landing page except the example gallery.

Refs #22

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Gallery generation script + rendered images + Gallery component

**Goal:** A Python script that uses the installed `idrisi` package to render three example maps into `site/public/gallery/`, plus the Astro `Gallery.astro` component that displays them on the landing page.

**Files:**
- Create: `site/scripts/build-gallery.py`
- Create: `site/scripts/README.md`
- Create: `site/public/gallery/kyushu-travel.png`
- Create: `site/public/gallery/kyushu-route.png`
- Create: `site/public/gallery/kyushu-region.png`
- Create: `site/src/components/Gallery.astro`
- Modify: `site/src/pages/index.astro`

- [ ] **Step 1: Create `site/scripts/build-gallery.py`**

This script builds a sample project in an in-memory SQLite DB with a recognizable Kyushu (Japan) loop and renders three maps.

```python
"""Render example maps for the marketing-site gallery.

Runs from the repo root. Uses the installed idrisi package. Writes PNGs
to site/public/gallery/. Re-run whenever the render pipeline or sample
data changes.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from idrisi.application.place_service import PlaceService
from idrisi.application.project_service import ProjectService
from idrisi.domain.value_objects import MapType, OutputFormat
from idrisi.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlProjectRepository,
)
from idrisi.infrastructure.db.session import create_engine_and_tables, get_session
from idrisi.infrastructure.renderer.engine import RenderEngine
from idrisi.infrastructure.renderer.styles import load_style


# A recognizable Kyushu, Japan loop — widely-documented tourist coordinates.
KYUSHU_LOOP = [
    ("Fukuoka",     33.5904, 130.4017),
    ("Nagasaki",    32.7503, 129.8777),
    ("Kumamoto",    32.8032, 130.7079),
    ("Mount Aso",   32.8842, 131.1042),
    ("Beppu",       33.2846, 131.4910),
    ("Kagoshima",   31.5966, 130.5571),
    ("Miyazaki",    31.9077, 131.4202),
]


class NoopGeocoding:
    """No-network stub for PlaceService."""

    def search(self, query: str):  # type: ignore[no-untyped-def]
        return []

    def reverse_geocode(self, coords):  # type: ignore[no-untyped-def]
        return None


def build_sample_project(name: str, map_type: MapType):
    engine = create_engine_and_tables("sqlite:///:memory:")
    session = get_session(engine)

    place_repo = SqlPlaceRepository(session)
    project_repo = SqlProjectRepository(session)

    place_svc = PlaceService(place_repo=place_repo, geocoding=NoopGeocoding())
    project_svc = ProjectService(project_repo=project_repo)

    project = project_svc.create(name=name, map_type=map_type)
    for title, lat, lon in KYUSHU_LOOP:
        p = place_svc.create(name=title, lat=lat, lon=lon, source="manual", country="Japan")
        project = project_svc.add_place(project.id, p.id)

    return place_svc.list_all(), project, session


def render_one(out_path: Path, map_type: MapType, style_name: str = "default") -> None:
    places, _, session = build_sample_project(f"Kyushu ({map_type.value})", map_type)
    style = load_style(style_name)
    engine = RenderEngine(style=style)

    if map_type is MapType.ROUTE:
        engine.render_route_map(
            places=places, output_path=str(out_path), output_format=OutputFormat.PNG,
        )
    elif map_type is MapType.REGION:
        engine.render_region_map(
            places=places, regions=[], output_path=str(out_path), output_format=OutputFormat.PNG,
        )
    else:
        engine.render_travel_map(
            places=places, regions=[], output_path=str(out_path), output_format=OutputFormat.PNG,
        )
    session.close()


def main() -> None:
    gallery = Path("site/public/gallery")
    if gallery.exists():
        shutil.rmtree(gallery)
    gallery.mkdir(parents=True)

    render_one(gallery / "kyushu-travel.png", MapType.TRAVEL)
    render_one(gallery / "kyushu-route.png", MapType.ROUTE)
    render_one(gallery / "kyushu-region.png", MapType.REGION)

    print("Wrote:")
    for p in sorted(gallery.glob("*.png")):
        print(f"  {p}  ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
```

If the render engine's method names differ, adjust them by inspecting `src/idrisi/infrastructure/renderer/engine.py` — the three public methods on `RenderEngine` are what to call. The script above uses `render_travel_map`, `render_route_map`, `render_region_map`; verify via `grep -n "def render_" src/idrisi/infrastructure/renderer/engine.py` before running.

- [ ] **Step 2: Create `site/scripts/README.md`**

```markdown
# site/scripts

Build-time scripts for the marketing site. Run these manually from the
repo root when their inputs change. Their outputs are committed.

## build-gallery.py

Renders example map PNGs into `site/public/gallery/`.

    uv run python site/scripts/build-gallery.py

Re-run when the render pipeline or the Kyushu sample changes. The
Cloudflare Pages build does *not* invoke Python — it ships the
already-committed PNGs.
```

- [ ] **Step 3: Run the script and verify output**

```bash
cd /Users/donaldalbrecht/Projects/Voyages/.claude/worktrees/marketing-site
UV_NO_SYNC=1 uv run python site/scripts/build-gallery.py
ls -la site/public/gallery/
```

Expected: three PNGs, each > 10 KB.

If the script fails because `add_place` / method names differ from what's in the spec, fix them based on the actual `ProjectService` / `RenderEngine` code in `src/idrisi/`. Do not invent APIs that don't exist. If the failure is deeper than a method name — for example, `render_route_map` requires additional arguments — fix the script to pass them, or fall back to only generating the two map types that do work and drop the third image from the gallery component.

- [ ] **Step 4: Create `site/src/components/Gallery.astro`**

```astro
---
const items = [
  {
    src: "/gallery/kyushu-travel.png",
    caption: "Kyushu loop · travel map, default style",
  },
  {
    src: "/gallery/kyushu-route.png",
    caption: "Kyushu loop · route map, default style",
  },
  {
    src: "/gallery/kyushu-region.png",
    caption: "Kyushu loop · region map, default style",
  },
];
---
<section class="gallery section">
  <h2>Examples.</h2>
  <p class="muted">A seven-stop Kyushu loop rendered three ways.</p>
  <div class="grid">
    {items.map((item) => (
      <figure>
        <img src={item.src} alt={item.caption} loading="lazy" />
        <figcaption class="muted">{item.caption}</figcaption>
      </figure>
    ))}
  </div>
</section>

<style>
  .gallery h2 { margin-bottom: var(--space-2); }
  .gallery .muted { margin-bottom: var(--space-4); }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
    gap: var(--space-4) var(--space-3);
  }
  figure { margin: 0; }
  figure img {
    display: block;
    width: 100%;
    height: auto;
    border: 1px solid var(--color-border);
    border-radius: 4px;
  }
  figcaption { margin-top: var(--space-1); font-size: 0.875rem; }
</style>
```

- [ ] **Step 5: Wire Gallery into `site/src/pages/index.astro`**

Insert `<Gallery />` between `<Quickstart />` and `<Footer />`:

```astro
---
import Base from "../layouts/Base.astro";
import Hero from "../components/Hero.astro";
import Features from "../components/Features.astro";
import Quickstart from "../components/Quickstart.astro";
import Gallery from "../components/Gallery.astro";
import Footer from "../components/Footer.astro";
---
<Base
  title="Idrisi — Travel cartography for modern trips."
  description="A Python toolbox that renders maps from your photos and itineraries."
  path="/"
>
  <main class="container">
    <Hero />
    <section class="intro section">
      <h2>A small toolbox for making maps of journeys.</h2>
      <p class="muted">
        Idrisi turns a list of places — typed in, imported from a Photos album, or assembled
        interactively — into a rendered map you can print, share, or keep for yourself.
        It's a CLI, a Python library, and a local web UI, in that order of emphasis.
      </p>
    </section>
    <Features />
    <Quickstart />
    <Gallery />
  </main>
  <Footer />
</Base>

<style>
  .intro h2 { max-width: 28ch; margin-bottom: var(--space-2); }
</style>
```

- [ ] **Step 6: Rebuild and verify PNG paths resolve**

```bash
cd site
npm run build
grep -o "/gallery/kyushu-[a-z]*\.png" dist/index.html | sort -u
ls dist/gallery/
cd ..
```

Expected: `grep` shows 3 unique paths, `ls` shows the 3 PNGs copied into `dist/gallery/`.

- [ ] **Step 7: Commit**

```bash
git add site/
git commit -m "$(cat <<'EOF'
feat(site): example gallery with three rendered Kyushu maps

Includes site/scripts/build-gallery.py which regenerates the PNGs.
The script is run manually; generated images are committed.

Refs #22

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: `/about/naming` page + markdown sourcing

**Goal:** A dedicated page at `/about/naming` that renders the contents of `docs/about/naming.md` with the site's layout. Copy is pulled at build time so there's a single source of truth.

**Files:**
- Create: `site/scripts/copy-naming.mjs`
- Create: `site/src/pages/about/naming.astro`
- Create: `site/src/content/naming.md` (produced by the copy script; also committed so Astro can type-check without running the script)
- Modify: `site/package.json` (re-add `prebuild` hook)
- Modify: `site/.gitignore` (the copied naming.md is *not* ignored — it's committed)

- [ ] **Step 1: Create `site/scripts/copy-naming.mjs`**

```js
#!/usr/bin/env node
// Copies docs/about/naming.md into site/src/content/naming.md so Astro
// can import it. Run as site's prebuild step.

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, "..", "..", "docs", "about", "naming.md");
const dest = resolve(here, "..", "src", "content", "naming.md");

mkdirSync(dirname(dest), { recursive: true });
copyFileSync(src, dest);
console.log(`copied ${src} → ${dest}`);
```

- [ ] **Step 2: Re-add `prebuild` hook in `site/package.json`**

Change the `"scripts"` block to include `prebuild`:

```json
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "prebuild": "node scripts/copy-naming.mjs"
  },
```

- [ ] **Step 3: Run the copy script once manually and commit the result**

```bash
cd site
node scripts/copy-naming.mjs
ls src/content/naming.md
cd ..
```

Expected: `site/src/content/naming.md` exists and matches `docs/about/naming.md`.

- [ ] **Step 4: Create `site/src/pages/about/naming.astro`**

```astro
---
import Base from "../../layouts/Base.astro";
import Footer from "../../components/Footer.astro";
import Compass from "../../components/Compass.astro";

// Astro glob-imports markdown at build time. No runtime fetching.
// The file is kept in sync with docs/about/naming.md by the prebuild hook.
const mod = await import("../../content/naming.md");
const { Content } = mod;
---
<Base
  title="Why Idrisi? — About the name"
  description="How Idrisi got its name, and why a 12th-century Arab cartographer was the right namesake."
  path="/about/naming"
>
  <main class="container">
    <nav class="topnav" aria-label="Site">
      <a href="/" class="home">
        <Compass size={14} />
        <span>Idrisi</span>
      </a>
    </nav>
    <article class="prose">
      <Content />
    </article>
  </main>
  <Footer />
</Base>

<style>
  .topnav {
    padding: var(--space-4) 0 var(--space-3);
  }
  .topnav .home {
    display: inline-flex;
    align-items: center;
    gap: 0.4em;
    font-weight: 600;
    text-decoration: none;
    border-bottom: 1px solid var(--color-accent);
    padding-bottom: 2px;
  }
  .prose {
    max-width: 60ch;
    padding: var(--space-3) 0 var(--space-5);
  }
  .prose :global(h1) { margin-bottom: var(--space-3); }
  .prose :global(h2) { margin-top: var(--space-4); margin-bottom: var(--space-2); font-size: 1.25rem; }
  .prose :global(p) { margin-bottom: var(--space-2); }
  .prose :global(ul) { margin: var(--space-2) 0 var(--space-3) 1.25rem; }
  .prose :global(li) { margin-bottom: 0.5rem; }
</style>
```

- [ ] **Step 5: Verify `docs/about/naming.md` exists and build**

```bash
ls docs/about/naming.md  # sanity check
cd site
npm run build
grep -q "Why \"Idrisi\"" dist/about/naming/index.html
grep -q "Muhammad al-Idrisi" dist/about/naming/index.html
cd ..
```

Both `grep -q` commands should succeed.

- [ ] **Step 6: Commit**

```bash
git add site/
git commit -m "$(cat <<'EOF'
feat(site): /about/naming page sourced from docs/about/naming.md

A Node prebuild script copies the canonical markdown into
site/src/content/ so Astro can render it without duplicating the text.

Refs #22

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: robots.txt + sitemap + deploy README

**Goal:** SEO plumbing (sitemap is auto-generated by `@astrojs/sitemap`; robots points at it), plus a `site/README.md` documenting the Cloudflare Pages setup so future contributors can recreate it.

**Files:**
- Create: `site/public/robots.txt`
- Create: `site/README.md`

- [ ] **Step 1: Create `site/public/robots.txt`**

```
User-agent: *
Allow: /

Sitemap: https://idrisi.donalbrecht.com/sitemap-index.xml
```

(Astro's sitemap integration generates `sitemap-index.xml` at the site root by default.)

- [ ] **Step 2: Create `site/README.md`**

```markdown
# Idrisi Marketing Site

Static site served at <https://idrisi.donalbrecht.com>. Built with Astro,
deployed on Cloudflare Pages.

## Local development

    cd site
    npm install
    npm run dev          # http://localhost:4321
    npm run build        # writes dist/
    npm run preview      # serves dist/

## Example gallery

PNG renders under `public/gallery/` are produced by a Python script that
uses the main `idrisi` package. Re-run when the render pipeline or the
Kyushu sample coordinates change:

    uv run python site/scripts/build-gallery.py

Generated images are committed. Cloudflare's build does not run Python.

## /about/naming sourcing

The naming post's canonical copy lives in `docs/about/naming.md`. An npm
`prebuild` hook (`scripts/copy-naming.mjs`) copies it into
`src/content/naming.md` before each Astro build so the content stays in
sync without duplication.

## Deployment (Cloudflare Pages)

One-time setup, performed via the Cloudflare dashboard:

1. Pages → Create a project → Connect to Git → select `dalbrecht/idrisi`.
2. Build settings:
   - Framework preset: Astro
   - Build command: `cd site && npm ci && npm run build`
   - Build output directory: `site/dist`
   - Root directory: `/` (repo root)
3. Environment variables: none required.
4. Branch: `main` deploys to production; PR branches auto-deploy as
   preview URLs.
5. Custom domain: `idrisi.donalbrecht.com` → add under Pages → Custom
   domains. Cloudflare issues a TLS cert automatically if DNS is on
   Cloudflare.

Once connected, pushes to `main` under `site/**` or `docs/about/naming.md`
trigger a rebuild. The free tier allows 500 builds/month — far beyond
typical usage.
```

- [ ] **Step 3: Build one more time and verify sitemap exists**

```bash
cd site
npm run build
ls dist/sitemap*.xml
cat dist/robots.txt
cd ..
```

Expected: `sitemap-index.xml` (and one or more `sitemap-0.xml` files) are present; `robots.txt` prints with the Sitemap line.

- [ ] **Step 4: Commit**

```bash
git add site/
git commit -m "$(cat <<'EOF'
chore(site): add robots.txt, sitemap wiring docs, and deploy README

Refs #22

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Lighthouse + link check + push + PR

**Goal:** Final verification (local Lighthouse run against the preview server, internal link check), push the branch, open the PR.

- [ ] **Step 1: Start the preview server in the background and run smoke checks**

```bash
cd site
npm run build
npm run preview -- --host 127.0.0.1 --port 4321 > /tmp/idrisi-preview.log 2>&1 &
PREVIEW_PID=$!
sleep 2

# Every internal link on the landing resolves
for url in / /about/naming/ /404 /robots.txt /sitemap-index.xml; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:4321$url")
  echo "$code  $url"
done

kill $PREVIEW_PID 2>/dev/null
cd ..
```

Expected: 200 for every URL except `/404` (which should be 404 since we're hitting the 404 resource as a request, not getting redirected to it). If the 404 URL returns 200 instead, check that Astro generated `dist/404.html` as expected.

- [ ] **Step 2: Run Lighthouse against the preview (optional, local-only)**

If the Lighthouse CLI is available, run it; otherwise skip this step and rely on the CI preview deployment.

```bash
cd site
npm run build
npm run preview -- --host 127.0.0.1 --port 4321 > /dev/null 2>&1 &
PREVIEW_PID=$!
sleep 2
npx -y lighthouse http://127.0.0.1:4321 --quiet --chrome-flags="--headless=new" --only-categories=performance,accessibility,best-practices,seo --output=json --output-path=/tmp/idrisi-lh.json || true
kill $PREVIEW_PID 2>/dev/null
node -e "const r = JSON.parse(require('fs').readFileSync('/tmp/idrisi-lh.json')); for (const k of Object.keys(r.categories)) console.log(k, Math.round(r.categories[k].score * 100))"
cd ..
```

Expected thresholds: Performance ≥ 95, Accessibility ≥ 95, Best Practices ≥ 90, SEO ≥ 90. Fix anything below threshold before proceeding — the most likely offender is font loading; if Performance dips, drop the Google Fonts and use the system stack only (remove the `<link>` tags from `Base.astro` and simplify the `--font-sans` / `--font-serif` variables in `global.css`).

- [ ] **Step 3: Push the branch**

```bash
git push -u origin feat/marketing-site
```

- [ ] **Step 4: Open the PR**

```bash
gh pr create --title "feat: marketing site at idrisi.donalbrecht.com" --body "$(cat <<'EOF'
## Summary

Adds a static marketing site under `site/` built with Astro and deployed on Cloudflare Pages to <https://idrisi.donalbrecht.com>. Includes a landing page (hero, features, install snippet, three-map example gallery, footer) and a dedicated `/about/naming` page sourced from `docs/about/naming.md`.

Closes #22.

## Commits

1. Scaffold Astro project under `site/`.
2. Base layout, styles, favicon, OG image, 404.
3. Hero, Features, Quickstart, Footer components on the landing.
4. `build-gallery.py` + three rendered Kyushu loop PNGs + `Gallery.astro` component.
5. `/about/naming` page, sourced from `docs/about/naming.md` via a prebuild hook.
6. `robots.txt`, sitemap, and `site/README.md` deploy docs.

## Cloudflare Pages setup

After merge, configure Cloudflare Pages (one-time, via dashboard) with:

- Build command: `cd site && npm ci && npm run build`
- Output: `site/dist`
- Custom domain: `idrisi.donalbrecht.com`

Full instructions in `site/README.md`.

## Test plan

- [ ] `cd site && npm ci && npm run build` exits 0
- [ ] `npm run preview` serves the landing with no console errors
- [ ] Landing renders hero / features / quickstart / three gallery images / footer
- [ ] `/about/naming` renders the naming post with working back-to-home link
- [ ] `sitemap-index.xml` and `robots.txt` exist in `dist/`
- [ ] Cloudflare Pages preview URL (auto-created from this PR) loads cleanly

Spec: `docs/superpowers/specs/2026-04-13-marketing-site-design.md`
Plan: `docs/superpowers/plans/2026-04-13-marketing-site.md`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 5: Watch CI and merge when green**

```bash
gh pr checks --watch
```

When CI is green, merge with:

```bash
gh pr merge --merge --delete-branch
```

After merge, perform the Cloudflare Pages one-time setup documented in `site/README.md`.
