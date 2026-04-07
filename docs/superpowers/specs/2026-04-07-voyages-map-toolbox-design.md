# Voyages — Map Generation Toolbox

**Date:** 2026-04-07
**Status:** Approved

## Purpose

A personal map generation toolbox for producing high-quality cartographic images for print and blog use. Combines a CLI for rendering and batch operations with an embedded web UI for interactive data curation and map preview.

## Architecture

Python monorepo with clean architecture (per c65llc/coding-standards). A single `pip install` yields both the CLI and the web UI. SQLite is the shared data store between CLI and server.

```
voyages/
├── pyproject.toml
├── Makefile
├── src/
│   └── voyages/
│       ├── domain/             # Pure business logic, zero external deps
│       │   ├── entities.py     # Place, Trip, Region, Project, Photo
│       │   ├── value_objects.py# Coordinates, BoundingBox, MapStyle
│       │   └── errors.py       # Domain exceptions
│       ├── application/        # Use cases + interface protocols
│       │   ├── interfaces.py   # PlaceRepository, GeocodingService, etc.
│       │   ├── place_service.py
│       │   ├── trip_service.py
│       │   ├── photo_service.py
│       │   └── render_service.py
│       ├── infrastructure/     # External implementations
│       │   ├── db/             # SQLite via SQLAlchemy
│       │   ├── geocoding/      # Nominatim client
│       │   ├── renderer/       # Cartopy/Matplotlib rendering
│       │   └── exif/           # Photo GPS/timestamp extraction
│       ├── cli/                # Typer CLI entry point
│       │   └── __init__.py
│       └── server/             # FastAPI + serves built SPA
│           ├── __init__.py
│           └── routes/
├── web/                        # Svelte SPA (separate build)
│   ├── package.json
│   └── src/
├── tests/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── e2e/
└── docs/
```

### Layer Rules

- **Domain:** Pure Python. Dataclasses and logic only. Zero external dependencies (not even SQLAlchemy or Pydantic). 100% test coverage.
- **Application:** Defines `Protocol`-based interfaces (e.g., `PlaceRepository`, `GeocodingService`). Orchestrates domain logic. Depends only on domain.
- **Infrastructure:** Implements application interfaces. Holds all heavy dependencies (SQLAlchemy, Cartopy, httpx, Pillow). 95%+ test coverage.
- **CLI:** Thin Typer entry point. Wires up application services with infrastructure implementations. Minimal logic.
- **Server:** Thin FastAPI entry point. Same wiring as CLI. Serves built Svelte assets at `/`.

## Data Model

### Place

The atomic geographic unit.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| name | str | Display name |
| latitude | float | WGS84 |
| longitude | float | WGS84 |
| country | str \| None | Populated via reverse geocoding |
| admin1 | str \| None | State/province, via reverse geocoding |
| category | str \| None | city, landmark, restaurant, park, etc. |
| notes | str \| None | Freeform |
| source | str | manual, photo, gpx, csv |
| created_at | datetime | Auto |
| updated_at | datetime | Auto |

### Trip

An ordered sequence of places with time context.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| name | str | e.g., "Japan 2024" |
| description | str \| None | |
| start_date | date \| None | |
| end_date | date \| None | |

**Trip-Place join:**

| Field | Type | Notes |
|-------|------|-------|
| trip_id | UUID | FK |
| place_id | UUID | FK |
| position | int | Order in itinerary |
| arrived_at | datetime \| None | |
| departed_at | datetime \| None | |

### Region

A country, state, or named area visited.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| name | str | e.g., "France", "California" |
| region_type | str | country, state, park, etc. |
| region_code | str \| None | ISO 3166-1/2 code |

Regions are auto-derived from places (by reverse geocoding country/admin1) and also manually addable.

### Project

A map composition that pulls from places, trips, and regions.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| name | str | |
| description | str \| None | |
| map_type | str | travel, region, route |
| config | dict | Projection, bounds, style, layers (stored as JSON) |

**Project-data joins:** project_places, project_trips, project_regions (many-to-many).

### Photo

Metadata only — image files are not stored in the database.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Primary key |
| file_path | str | Absolute path to image on disk |
| latitude | float \| None | From EXIF |
| longitude | float \| None | From EXIF |
| taken_at | datetime \| None | From EXIF |
| place_id | UUID \| None | FK, assigned after review |
| trip_id | UUID \| None | FK, assigned after review |

## Rendering Pipeline

Composable layer-based pipeline using Cartopy and Matplotlib.

### Layers (applied in order)

1. **Base map** — projection, bounds, background colors (ocean, land)
2. **Shape layers** — country/state boundaries from Natural Earth shapefiles
3. **Data layers** — places (markers), routes (polylines), regions (shaded polygons)
4. **Style layers** — colors, gradients, typography, textures
5. **Annotation layers** — labels, legends, scale bars, title

### Map Types → Layer Presets

- **Travel map:** base + shaded visited regions + place markers + legend
- **Region map:** zoomed base + detailed boundaries + place markers + labels + scale bar
- **Route map:** zoomed base + trip path polylines + stop markers with order + date labels

### Style System

Named style configurations as YAML files:

```yaml
name: vintage
ocean: "#D4E4ED"
land: "#F5F0E8"
visited: "#A01D26"
route: "#2C5F7C"
font: "Playfair Display"
borders: "#CCCCCC"
```

Built-in styles: default, vintage, minimal, dark. Custom styles loaded from YAML files.

### Output Formats

| Format | Use Case |
|--------|----------|
| SVG | Vector, blog embedding, further editing |
| PDF | Print-ready with proper DPI/bleed |
| PNG | Raster, configurable resolution (web 2x, print 300dpi) |
| WebP | Optimized web images for Astro blog |
| EPS | Print workflows |

## CLI

The CLI is the primary interface for rendering and batch operations.

```
voyages render <project-name>
  --format svg|pdf|png|webp|eps
  --style vintage|minimal|dark|<custom.yml>
  --dpi 300
  --width 1200
  --output ./maps/

voyages import photos <path>
  --trip "Japan 2024"
  --dry-run

voyages import gpx <file.gpx>
  --trip "PCT Section A"

voyages import csv <file.csv>

voyages serve
  --port 8080

voyages project list
voyages project create <name>
voyages project show <name>

voyages trip list
voyages trip create <name>
voyages trip show <name>

voyages place search "Kyoto"
voyages place add --name "Kyoto" --lat 35.01 --lon 135.77
voyages place list
```

### Photo Import Workflow

1. `voyages import photos ./album/ --trip "Japan 2024"` scans for JPEG/HEIC/PNG files
2. Extracts EXIF GPS coordinates and timestamps
3. Reverse geocodes via Nominatim to get place names
4. Groups by proximity and time to suggest stops
5. `--dry-run` previews without saving; without it, creates places and assigns to trip
6. Web UI provides interactive review and curation of imported data

## Web UI

Svelte SPA served by FastAPI at `/`. Used for data curation and map preview — not final rendering.

### Views

- **Dashboard** — project overview, recent trips, place count, quick actions
- **Places** — searchable list/table. Search via Nominatim, add, edit metadata, assign to trips. Bulk actions.
- **Trips** — list, create/edit, reorder stops, set dates. Visual timeline.
- **Regions** — countries/states visited. Auto-derived from places + manual.
- **Map Composer** — select map type, pick trips/places/regions to include, choose style/projection/bounds. Leaflet preview of approximate layout. "Export" button triggers server-side Cartopy render.
- **Photo Import** — drag-and-drop or folder select. Shows extracted GPS points on Leaflet map. Review, assign to trip, confirm.

### Map Preview (Leaflet + OpenStreetMap tiles)

The preview is intentionally lower fidelity than the final render. It shows:

- Place markers
- Trip routes as polylines
- Shaded regions via GeoJSON overlays
- Approximate bounding box of the final render

Purpose: composition check ("does this map include the right data and framing?"). Pretty output comes from the rendering pipeline.

### API (FastAPI)

RESTful with auto-generated OpenAPI docs. All request/response models typed with Pydantic.

| Endpoint | Methods | Purpose |
|----------|---------|---------|
| `/api/places` | GET, POST, PUT, DELETE | Place CRUD + Nominatim search |
| `/api/trips` | GET, POST, PUT, DELETE | Trip CRUD + manage stops |
| `/api/regions` | GET, POST, PUT, DELETE | Region CRUD + auto-derive |
| `/api/projects` | GET, POST, PUT, DELETE | Project CRUD |
| `/api/photos/import` | POST | Upload/extract EXIF, return preview |
| `/api/render/{project_id}` | POST | Trigger render, return file |

## Tech Stack

| Concern | Tool |
|---------|------|
| Package management | uv |
| Formatting + linting | ruff format, ruff check |
| Type checking | mypy --strict |
| CLI framework | Typer |
| API server | FastAPI |
| Database | SQLite via SQLAlchemy |
| Geocoding | Nominatim (OpenStreetMap) |
| Map rendering | Cartopy + Matplotlib |
| EXIF extraction | Pillow / exifread |
| HTTP client | httpx |
| Web frontend | Svelte |
| Web map preview | Leaflet + OpenStreetMap tiles |
| Testing | pytest (TDD, 95%+ coverage, 100% domain) |
| Automation | GNU Make |
| Standards | c65llc/coding-standards (submodule) |

## Scope Boundaries

**In scope for v1:**
- Data model and SQLite persistence
- Place search via Nominatim
- Photo EXIF import (CLI + web)
- GPX and CSV import (CLI)
- Travel map rendering (shaded countries/states + markers)
- Region map rendering (zoomed area)
- Route map rendering (trip paths)
- Style system with 4 built-in styles
- SVG, PDF, PNG, WebP, EPS output
- Web UI for data curation and Leaflet preview
- Export from web UI (triggers server-side render)

**Out of scope for v1 (future consideration):**
- User authentication (single-user tool)
- Map tile hosting (using OSM tiles for preview)
- Elevation/terrain rendering
- Satellite imagery layers
- Animation / interactive web map export
- Multi-user collaboration
- Cloud deployment
