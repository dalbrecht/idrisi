# site/scripts

Build-time scripts for the marketing site. Run these manually from the
worktree root when their inputs change. Their outputs are committed.

## build-gallery.py

Renders example map PNGs into `site/public/gallery/`.

    /Users/donaldalbrecht/Projects/Voyages/.venv/bin/python \
        site/scripts/build-gallery.py

Or from the repo root with `UV_NO_SYNC=1`:

    UV_NO_SYNC=1 uv run python \
        .claude/worktrees/marketing-site/site/scripts/build-gallery.py

Re-run when the render pipeline or the Kyushu sample changes. The
Cloudflare Pages build does *not* invoke Python — it ships the
already-committed PNGs.
