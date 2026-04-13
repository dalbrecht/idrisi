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

    UV_NO_SYNC=1 uv run python site/scripts/build-gallery.py

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
