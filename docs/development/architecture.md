---
title: "Architecture"
description: "Clean architecture layers, design decisions, and directory structure for Voyages"
section: "development"
order: 2
---

# Architecture

## Overview

Voyages follows clean architecture with four concentric layers. The fundamental rule is that **inner layers never import from outer layers** — dependencies flow inward only. This keeps the domain and application logic independent of infrastructure choices and delivery mechanisms.

## Layer Diagram

```
┌──────────────────────────────────────────┐
│           Entry Points                   │
│        (CLI / Server)                    │
│  ┌────────────────────────────────────┐  │
│  │         Infrastructure             │  │
│  │  (DB, Renderer, Geocoding, EXIF)   │  │
│  │  ┌──────────────────────────────┐  │  │
│  │  │        Application           │  │  │
│  │  │  (Services, Protocols)       │  │  │
│  │  │  ┌────────────────────────┐  │  │  │
│  │  │  │        Domain          │  │  │  │
│  │  │  │  (Entities, Values,    │  │  │  │
│  │  │  │   Enums, Exceptions)   │  │  │  │
│  │  │  └────────────────────────┘  │  │  │
│  │  └──────────────────────────────┘  │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘

Dependencies flow inward: Entry Points → Infrastructure → Application → Domain
```

## Domain Layer

**Location:** `src/voyages/domain/`

Pure Python with zero external dependencies. The domain layer defines the core concepts of the application.

**Entities (dataclasses):**
- `Place` — a geographic location with a name and coordinates
- `Trip` — a journey composed of ordered stops
- `TripStop` — a single stop within a trip
- `Region` — a named geographic area with a bounding box
- `Project` — a map project combining trips, places, and rendering settings
- `Photo` — a photo with optional geolocation metadata

**Value Objects:**
- `Coordinates` — latitude/longitude pair with range validation
- `BoundingBox` — rectangular geographic bounds

**Enums:**
- `MapType` — `travel | region | route`
- `OutputFormat` — `svg | pdf | png | webp | eps`

**Domain Exceptions:**
- `VoyagesError` — base exception for all domain errors
- `EntityNotFoundError` — base for not-found errors
- `PlaceNotFoundError`
- `TripNotFoundError`
- `ProjectNotFoundError`
- `RegionNotFoundError`
- `RenderError`

## Application Layer

**Location:** `src/voyages/application/`

Orchestrates domain objects through service classes. Depends only on the domain layer — infrastructure is accessed exclusively through protocols (interfaces).

**Service Classes:**
- `PlaceService` — place lookup, creation, and geocoding coordination
- `TripService` — trip and stop management
- `ProjectService` — project lifecycle and render coordination
- `RegionService` — region creation and bounding box management
- `PhotoService` — photo ingestion and EXIF metadata handling

**Repository Protocols** (defined here, implemented in infrastructure):
- `PlaceRepository`, `TripRepository`, `ProjectRepository`, `RegionRepository`, `PhotoRepository`

**External Service Protocols:**
- `GeocodingService` — geocode a place name to coordinates
- `ExifService` — extract metadata from photo files
- `MapRenderer` — render a project to an output format

## Infrastructure Layer

**Location:** `src/voyages/infrastructure/`

Concrete implementations of the protocols defined in the application layer.

**`db/`** — persistence:
- SQLAlchemy ORM models for all entities
- SQLite repository implementations of the repository protocols

**`renderer/`** — map rendering:
- `RenderEngine` — Cartopy + Matplotlib rendering pipeline
- `MapStyle` — dataclass capturing visual style settings
- Style loader utilities: `load_style`, `get_builtin_styles`

**`geocoding/`** — place search:
- Nominatim client implemented via `httpx`

**`exif/`** — photo metadata:
- EXIF extraction via Pillow

## Entry Points

**CLI:** `src/voyages/cli/` — built with [Typer](https://typer.tiangolo.com/). Each command creates the necessary infrastructure instances, injects them into application services, and delegates.

**Server:** `src/voyages/server/` — built with [FastAPI](https://fastapi.tiangolo.com/). Route handlers are thin wrappers: create infrastructure instances, inject into services, return results.

Neither entry point contains business logic. They are responsible only for parsing inputs, wiring dependencies, and formatting outputs.

## Key Design Decisions

**Protocol-based interfaces instead of ABCs** — `typing.Protocol` provides structural subtyping. Infrastructure classes satisfy protocols without explicit inheritance, making them easier to swap and test.

**SQLite as the embedded default** — no external database server required. The `db/` infrastructure implementation uses an in-memory SQLite database for tests and a file-based database for production use.

**Layer-based rendering pipeline** — the renderer composes a map by applying layers in order:
1. Base map (projection and background)
2. Shape layers (coastlines, borders, terrain)
3. Data layers (trips, places, regions)
4. Style layers (colors, line weights, fonts)
5. Annotation layers (labels, legends, scale bars)

## Directory Map

```
src/voyages/
├── __init__.py
├── domain/                    # Domain Layer
│   ├── __init__.py
│   ├── entities.py            # Place, Trip, TripStop, Region, Project, Photo
│   ├── value_objects.py       # Coordinates, BoundingBox, MapType, OutputFormat
│   └── errors.py              # VoyagesError, EntityNotFoundError, etc.
├── application/               # Application Layer
│   ├── __init__.py
│   ├── interfaces.py          # All protocols: PlaceRepository, TripRepository, etc., MapRenderer, GeocodingService, ExifService
│   ├── place_service.py
│   ├── trip_service.py
│   ├── project_service.py
│   ├── region_service.py
│   └── photo_service.py
├── infrastructure/            # Infrastructure Layer
│   ├── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   └── repository.py      # Repository implementations
│   ├── renderer/
│   │   ├── __init__.py
│   │   ├── engine.py          # RenderEngine (Cartopy + Matplotlib)
│   │   └── styles.py          # MapStyle, load_style(), get_builtin_styles()
│   ├── geocoding/
│   │   ├── __init__.py
│   │   └── nominatim.py       # Nominatim client (httpx)
│   └── exif/
│       ├── __init__.py
│       └── extractor.py       # EXIF GPS/timestamp extraction (Pillow)
├── cli/                       # Entry Point: CLI
│   ├── __init__.py            # Typer app with sub-apps
│   ├── place_commands.py
│   ├── trip_commands.py
│   ├── project_commands.py
│   ├── import_commands.py
│   ├── render_commands.py
│   └── serve_command.py
└── server/                    # Entry Point: API Server
    ├── __init__.py            # FastAPI factory (create_app)
    └── routes/
        ├── __init__.py
        ├── places.py
        ├── trips.py
        ├── projects.py
        ├── regions.py
        └── render.py
```
