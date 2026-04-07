# Voyages

A Python map generation toolbox for travel cartography.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

Voyages combines a CLI and an interactive web UI to help you curate travel
data and render publication-quality cartographic maps. Import geotagged photos,
organize trips, choose from multiple styles and projections, and export to
SVG, PDF, PNG, WebP, or EPS.

## Features

- **Map rendering** — Generate travel, region, and route maps with Cartopy and Matplotlib
- **Multiple output formats** — SVG, PDF, PNG, WebP, EPS for print and web
- **Interactive web UI** — Svelte-based SPA with Leaflet map preview
- **Photo import** — Extract GPS coordinates and timestamps from EXIF data
- **Geocoding** — Search and reverse-geocode places via Nominatim (OpenStreetMap)
- **Built-in styles** — Default, vintage, minimal, and dark map themes with custom YAML support
- **Multiple projections** — EqualEarth for world views, PlateCarree for regional detail
- **Clean architecture** — Domain-driven design with protocol-based interfaces

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 18+ (for building the web UI)
- System libraries for Cartopy: GEOS and PROJ

macOS:
```bash
brew install geos proj
```

Ubuntu/Debian:
```bash
sudo apt install libgeos-dev libproj-dev
```

### Install

```bash
git clone https://github.com/dalbrecht/Voyages.git
cd Voyages
make repo-setup    # Initialize git submodules
make bootstrap     # Create venv and install dependencies
make build-web     # Build the Svelte frontend
```

### CLI

```bash
# Add places to the database
voyages place add --name "Paris" --lat 48.8566 --lon 2.3522
voyages place add --name "Rome" --lat 41.9028 --lon 12.4964

# Create a project
voyages project create "My Map" --map-type travel

# Associate places with the project via the API, then render
voyages render "My Map" --style vintage --format png
```

> **Note:** There is no CLI command to associate places with a project. Use the web UI or
> the REST API (`POST /api/projects/{id}`) to add `place_ids` to a project before rendering.

### Web UI

```bash
voyages serve
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser to access
the dashboard, manage places and trips, and compose maps interactively.

## Screenshots

_Sample map outputs will be added here._

## Documentation

| Section | Description |
|---------|-------------|
| [Installation](docs/getting-started/installation.md) | Prerequisites, platform-specific setup, install from source |
| [Quick Start](docs/getting-started/quickstart.md) | First map in 5 minutes — CLI and web tracks |
| [Configuration](docs/getting-started/configuration.md) | Database, styles, server settings |
| [CLI Workflow](docs/guides/cli-workflow.md) | End-to-end tutorial using the command line |
| [Web Workflow](docs/guides/web-workflow.md) | End-to-end tutorial using the browser UI |
| [Importing Photos](docs/guides/importing-photos.md) | EXIF extraction, geocoding, linking to trips |
| [Map Styles](docs/guides/map-styles.md) | Built-in themes and custom YAML styles |
| [Rendering & Output](docs/guides/rendering-output.md) | Formats, projections, print settings |
| [CLI Reference](docs/reference/cli-commands.md) | All commands, flags, and options |
| [API Overview](docs/reference/api-overview.md) | REST API conventions and interactive docs |
| [API Endpoints](docs/reference/api-endpoints.md) | Endpoint examples with request/response bodies |
| [Data Model](docs/reference/data-model.md) | Entities, relationships, ER diagram |
| [Map Types](docs/reference/map-types.md) | Travel, region, and route map presets |
| [Contributing](docs/development/contributing.md) | Dev setup, branch workflow, code quality |
| [Architecture](docs/development/architecture.md) | Clean architecture layers and design decisions |
| [Testing](docs/development/testing.md) | Test strategy, coverage targets, conventions |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| CLI | [Typer](https://typer.tiangolo.com/) |
| API Server | [FastAPI](https://fastapi.tiangolo.com/) |
| Database | SQLite via [SQLAlchemy](https://www.sqlalchemy.org/) |
| Map Rendering | [Cartopy](https://scitools.org.uk/cartopy/) + [Matplotlib](https://matplotlib.org/) |
| Geocoding | [Nominatim](https://nominatim.org/) (OpenStreetMap) |
| Frontend | [Svelte 5](https://svelte.dev/) + [Vite](https://vite.dev/) |
| Map Preview | [Leaflet](https://leafletjs.com/) |
| Package Manager | [uv](https://docs.astral.sh/uv/) |
| Linting & Formatting | [Ruff](https://docs.astral.sh/ruff/) |
| Type Checking | [mypy](https://mypy-lang.org/) (strict mode) |

## Development

```bash
make bootstrap     # Set up virtualenv and install all deps
make dev           # Install in editable mode with dev extras
make test          # Run tests
make lint          # Ruff check + mypy
make fmt           # Format code
make ci            # Full CI pipeline (lint + format check + test)
```

See [Contributing](docs/development/contributing.md) for the full development guide.

## License

Voyages is licensed under the [GNU Affero General Public License v3.0](LICENSE).
You are free to use, modify, and distribute this software under the terms of the
AGPL-3.0. If you run a modified version on a server, you must make the source
code available to users of that server.
