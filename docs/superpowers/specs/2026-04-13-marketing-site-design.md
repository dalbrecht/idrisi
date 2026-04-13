# Marketing Site for Idrisi — Design

**Date:** 2026-04-13
**Status:** Approved
**Issue:** dalbrecht/idrisi#22

## Purpose

A public landing site at `idrisi.donalbrecht.com` that introduces the Idrisi project to developers who arrive from GitHub, social links, or search. The primary reader is a developer considering whether to install and try the CLI; the site exists to answer "what does this do" and "how do I get started" in under thirty seconds.

A secondary goal is to give the al-Idrisi naming post its own shareable URL so it can be linked independently of the repo.

## Scope

### In scope

- A new `site/` directory in the repo containing an Astro project that builds a static site.
- Two pages: `/` (landing) and `/about/naming` (al-Idrisi naming post).
- A 404 page.
- A favicon and an Open Graph image, both generated as SVGs using the site's cartographic accent motif.
- A script to render sample maps that populate the example gallery.
- Cloudflare Pages deployment, wired to the repo so pushes to `main` trigger builds.
- Custom domain `idrisi.donalbrecht.com` via Cloudflare DNS.

### Out of scope (intentionally)

- A full docs mirror. Documentation stays in the repo and links go to GitHub.
- A blog beyond the naming post.
- A newsletter, auth, comments, or any backend.
- Interactive map embeds or live demos. The example gallery uses static images only.
- Analytics. Cloudflare Web Analytics can be enabled later with zero code.
- Search.
- Dark-mode toggle. The visual system is a single light theme.

## Audience

Developers. Landing readers are assumed to be comfortable with terminals, `pip`, and reading Python. Copy can reference CLI commands, package managers, and GitHub directly.

## Visual System

- **Ground:** `#ffffff`
- **Text:** `#111217` (body), `#5a5d66` (muted)
- **Accent:** `#8b6b2e` (sepia, used for a compass-rose motif, eyebrow labels, and link underlines)
- **Borders:** `#e6e8ec` (hairline only, used for code blocks and the gallery grid)
- **Display type:** a serif (Google Font `EB Garamond` with a fallback to Georgia) used only on page titles and section headings; everything else is sans.
- **Body type:** Google Font `Inter` with a system-stack fallback (`-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`).
- **Code:** system monospace stack, `#111217` on `#f6f7f9`, 1px border in `#e6e8ec`.
- **Imagery:** rendered maps centered in generous whitespace — no frames, drop shadows, or rounded crops.
- **Ornament:** one sepia compass motif in the hero eyebrow area, used sparingly elsewhere (favicon, OG image). Nothing medieval-pastiche; the accent is a quiet nod, not a theme.

## Landing Page Structure

Top to bottom, single long scroll:

1. **Hero.** Eyebrow "idrisi" with a small compass glyph; serif h1 tagline ("Travel cartography for modern trips."); sans sub-tagline ("A Python toolbox that renders maps from your photos and itineraries."); a primary action row with an install snippet (`pip install idrisi`, with click-to-copy) and a secondary "Read the docs" link to the GitHub repo.
2. **What is it.** Two or three sentences positioning the tool — what it produces, where inputs come from (Photos albums, manual CLI entry, etc.), and what makes it distinctive.
3. **Features grid.** Four to six small cards. Candidates: CLI-first, macOS Photos import (DBSCAN clustering), multiple map types (travel / region / route), pluggable styles, Python library for hacking, web preview server. Each card is an icon (simple SVG glyph, sepia), a short heading, and one sentence.
4. **Install & quickstart.** One `bash` block with install + a minimal end-to-end example showing `idrisi place add`, `idrisi project add`, adding a place to the project, then `idrisi render`. Reads as a script a person could paste and run.
5. **Example gallery.** Three or four rendered map images in a simple grid, each with a one-line caption identifying map type and style.
6. **Footer.** GitHub link, "Docs" link to the GitHub `docs/` tree, "About the name" link to `/about/naming`, license badge (AGPL-3.0).

## `/about/naming` Page

Long-form version of the al-Idrisi naming post. Content is imported from `docs/about/naming.md` at build time so there is a single source of truth. Page has the same header as the landing (compass eyebrow, minimal nav back to `/`) and a return-to-landing link in the footer.

## Technical Architecture

### Stack

- **Astro** 5.x with the default MDX + Markdown integration.
- **TypeScript** for all Astro components.
- **Tailwind** is *not* used. A small hand-written CSS file keeps the visual system in one place.
- **Google Fonts** loaded via `<link rel="preconnect">` with `font-display: swap`.
- **No client-side JS framework.** The one interactive element (copy-to-clipboard on the install snippet) is a short vanilla `<script>`.

### Directory layout

```
site/
  astro.config.mjs
  package.json
  tsconfig.json
  src/
    pages/
      index.astro            # landing
      about/naming.astro     # naming post
      404.astro
    components/
      Hero.astro
      Features.astro
      Quickstart.astro
      Gallery.astro
      Footer.astro
      Compass.astro          # inline SVG motif
    layouts/
      Base.astro             # shared header/footer/meta
    styles/
      global.css             # variables + reset + type scale
    content/
      naming.md              # copied/symlinked at build time from docs/about/naming.md
  public/
    favicon.svg
    og.svg
    gallery/
      travel-default.png
      region-default.png
      route-styled.png
      travel-styled.png
  scripts/
    build-gallery.py         # produces public/gallery/* from a sample project
```

### Content sourcing for `/about/naming`

A small build step copies `docs/about/naming.md` into `site/src/content/naming.md` before Astro builds. The copy happens in the `astro.config.mjs` `onStart`-equivalent hook (or a `prebuild` npm script) so the repo has one canonical copy of the text.

### Gallery generation

`site/scripts/build-gallery.py` is a short Python script that:

1. Uses the main `idrisi` package (not a separate install — it runs from the repo).
2. Builds a sample project in an in-memory SQLite database with a recognizable public route (candidate: an 8-stop loop around Japan using widely-known tourist coordinates; no private data).
3. Calls the render pipeline directly for each combination of map type and style selected for the gallery.
4. Writes output PNGs to `site/public/gallery/`.

The script runs locally before a deploy when gallery content changes; it is *not* part of the Cloudflare build (keeps the Pages build environment dependency-free). Generated PNGs are committed to the repo.

### Deployment

- Cloudflare Pages is connected to the GitHub repo.
- Build command: `cd site && npm ci && npm run build`.
- Output directory: `site/dist`.
- Build only runs when files under `site/`, `docs/about/naming.md`, or the workflow itself change (Cloudflare Pages auto-detects path filters, or we configure an explicit filter).
- Custom domain `idrisi.donalbrecht.com` configured in Cloudflare Pages → Domains. TLS is automatic.

### SEO and sharing

- Each page sets `<title>`, `<meta name="description">`, and Open Graph tags via the `Base.astro` layout.
- A single OG image (`public/og.svg`) is used for both pages; it's the compass motif over the tagline on the site's ground color.
- `sitemap.xml` generated automatically by the `@astrojs/sitemap` integration.
- `robots.txt` served via `public/robots.txt` with a `Sitemap:` line pointing at the generated sitemap.

## Copy

The spec fixes the hero copy to keep scope tight. Everything else is drafted inline in the implementation plan; treat the plan as the content source.

- **Tagline:** "Travel cartography for modern trips."
- **Sub-tagline:** "A Python toolbox that renders maps from your photos and itineraries."
- **Primary CTA text:** "pip install idrisi" (in a code block with a copy button)
- **Secondary CTA text:** "Read the docs →" linking to `https://github.com/dalbrecht/idrisi`

## Verification

- `cd site && npm run build` produces `site/dist` with no errors or warnings.
- Opening `site/dist/index.html` renders with no console errors in Chrome, Firefox, Safari.
- Lighthouse (run locally against `npm run preview`) scores ≥ 95 on Performance and Accessibility, ≥ 90 on Best Practices and SEO.
- Links from landing → `/about/naming` and back work; footer GitHub/docs links point at the right URLs.
- The install snippet's copy button actually copies.
- Cloudflare Pages preview deployment builds successfully on the PR.
- `https://idrisi.donalbrecht.com/` resolves and serves the landing page after merge.

## Risks

- **Rendered-map script reliability.** `build-gallery.py` depends on every moving part of the render pipeline. If it breaks, the build still succeeds (PNGs are committed), but regenerating the gallery requires developer attention. Acceptable for a pre-1.0 site.
- **Custom font performance.** EB Garamond + Inter adds two font requests. Mitigated by `preconnect` and `font-display: swap`; if Lighthouse Performance dips, we drop to system-stack serif + sans.
- **Cloudflare Pages build limits.** Free tier allows 500 builds/month; this will not approach that.
- **Design drift from the repo's `web/` app.** The marketing site and the app share a name but not a visual system. This is intentional — the app is a tool UI, the site is marketing copy — but if the two ever converge on a shared design system, this site's CSS can be refactored onto it without blocking anything else.
