---
title: "Installation"
description: "Install Voyages from source on macOS or Linux"
section: "getting-started"
order: 1
---

# Installation

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) — Python package and environment manager
- Node.js 18+
- GEOS and PROJ — required by Cartopy for map projection support

## System Dependencies

**macOS:**

```bash
brew install geos proj
```

**Ubuntu / Debian:**

```bash
sudo apt install libgeos-dev libproj-dev
```

**Other platforms:** Refer to the [Cartopy installation docs](https://scitools.org.uk/cartopy/docs/latest/installing.html) for platform-specific instructions.

## Install from Source

```bash
git clone https://github.com/dalbrecht/Voyages.git
cd Voyages
```

Initialize git submodules:

```bash
make repo-setup
```

This runs `git submodule update --init` to pull in any vendored dependencies.

Create the virtual environment and install Python dependencies:

```bash
make bootstrap
```

This runs `uv venv && uv pip install -e ".[dev]"`.

Build the web frontend:

```bash
make build-web
```

This runs `cd web && npm ci && npm run build`.

## Verify Installation

Check that the CLI is available:

```bash
voyages --help
```

Expected output shows Typer help with subcommands: `place`, `trip`, `project`, `import`, plus top-level `serve` and `render` commands.

Start the development server and confirm it responds:

```bash
voyages serve
```

Open `http://127.0.0.1:8080` in a browser. You should see the Voyages web UI.

## What's Next

Follow the [Quick Start](quickstart.md) to add your first places and render a map.
