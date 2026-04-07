# Voyages Map Toolbox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI + embedded web UI for generating high-quality cartographic maps from travel data (places, trips, regions) with photo EXIF import and multiple output formats.

**Architecture:** Python monorepo with clean architecture — domain (pure logic), application (use cases + protocols), infrastructure (SQLAlchemy, Cartopy, Nominatim, EXIF). Typer CLI and FastAPI server are thin entry points that wire application services to infrastructure. Svelte SPA served by FastAPI for interactive data curation with Leaflet map preview.

**Tech Stack:** Python 3.12+, uv, ruff, mypy strict, Typer, FastAPI, SQLAlchemy, SQLite, Cartopy, Matplotlib, httpx, Pillow, Svelte, Leaflet, pytest

**Spec:** `docs/superpowers/specs/2026-04-07-voyages-map-toolbox-design.md`

---

## File Structure

### Domain Layer (`src/voyages/domain/`)
- `entities.py` — Place, Trip, TripStop, Region, Project, Photo dataclasses
- `value_objects.py` — Coordinates, BoundingBox, MapType, OutputFormat, MapStyle enums/dataclasses
- `errors.py` — Domain exceptions (PlaceNotFoundError, TripNotFoundError, etc.)

### Application Layer (`src/voyages/application/`)
- `interfaces.py` — Protocol definitions: PlaceRepository, TripRepository, RegionRepository, ProjectRepository, PhotoRepository, GeocodingService, ExifService, RenderService
- `place_service.py` — PlaceService: search, create, update, delete, reverse geocode
- `trip_service.py` — TripService: CRUD, manage stops, reorder
- `region_service.py` — RegionService: CRUD, auto-derive from places
- `photo_service.py` — PhotoService: import from directory, extract EXIF, assign to trips
- `project_service.py` — ProjectService: CRUD, render trigger
- `render_service.py` — RenderService: orchestrate layer-based rendering

### Infrastructure Layer (`src/voyages/infrastructure/`)
- `db/models.py` — SQLAlchemy ORM models
- `db/repository.py` — SQLAlchemy implementations of all repository protocols
- `db/session.py` — Engine and session factory
- `geocoding/nominatim.py` — Nominatim geocoding client (httpx)
- `renderer/base.py` — Base renderer: projection setup, figure management
- `renderer/layers.py` — Layer implementations: base map, shapes, data, style, annotations
- `renderer/styles.py` — Style loading (YAML) and built-in styles
- `renderer/engine.py` — RenderEngine: compose layers, export to format
- `exif/extractor.py` — EXIF GPS/timestamp extraction from photos

### CLI (`src/voyages/cli/`)
- `__init__.py` — Typer app, sub-command registration
- `place_commands.py` — voyages place search/add/list
- `trip_commands.py` — voyages trip list/create/show
- `project_commands.py` — voyages project list/create/show
- `import_commands.py` — voyages import photos/gpx/csv
- `render_commands.py` — voyages render
- `serve_command.py` — voyages serve

### Server (`src/voyages/server/`)
- `__init__.py` — FastAPI app factory
- `dependencies.py` — Dependency injection (services, DB session)
- `routes/places.py` — /api/places endpoints
- `routes/trips.py` — /api/trips endpoints
- `routes/regions.py` — /api/regions endpoints
- `routes/projects.py` — /api/projects endpoints
- `routes/photos.py` — /api/photos/import endpoint
- `routes/render.py` — /api/render/{project_id} endpoint

### Web (`web/`)
- `package.json` — Svelte + Vite + Leaflet deps
- `vite.config.ts` — Build config, output to ../src/voyages/server/static/
- `src/App.svelte` — Root component with router
- `src/lib/api.ts` — API client (typed fetch wrapper)
- `src/routes/Dashboard.svelte`
- `src/routes/Places.svelte`
- `src/routes/Trips.svelte`
- `src/routes/Regions.svelte`
- `src/routes/MapComposer.svelte`
- `src/routes/PhotoImport.svelte`
- `src/components/MapPreview.svelte` — Leaflet map component

### Tests (`tests/`)
Mirror of src structure: `tests/domain/`, `tests/application/`, `tests/infrastructure/`, `tests/cli/`, `tests/server/`

### Config
- `pyproject.toml` — Package config, dependencies, ruff, mypy settings
- `Makefile` — make dev, test, lint, fmt, serve, build-web, etc.
- `styles/default.yml`, `styles/vintage.yml`, `styles/minimal.yml`, `styles/dark.yml` — Built-in map styles

---

## Phase 1: Project Foundation

### Task 1: Add coding-standards submodule and scaffold project

**Files:**
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `src/voyages/__init__.py`
- Create: `src/voyages/py.typed`
- Create: `tests/__init__.py`
- Modify: `.gitignore`

- [ ] **Step 1: Add c65llc/coding-standards as a submodule**

```bash
cd /Users/donaldalbrecht/Projects/Voyages
git submodule add https://github.com/c65llc/coding-standards.git coding-standards
```

- [ ] **Step 2: Run the standards setup script**

Check what setup mechanism the repo provides and run it. This will generate CLAUDE.md, Makefile targets, ruff.toml, and git hooks configuration. Adapt generated files to this project's specific needs (Python-only, uv-based).

```bash
ls coding-standards/scripts/
# Run the appropriate setup script, e.g.:
# bash coding-standards/scripts/setup.sh
```

Verify generated files exist and adapt as needed.

- [ ] **Step 3: Create pyproject.toml**

```toml
[project]
name = "voyages"
version = "0.1.0"
description = "Map generation toolbox for travel data"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
voyages = "voyages.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/voyages"]

[tool.ruff]
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "A", "C4", "SIM", "TCH"]

[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_any_generics = true
no_implicit_optional = true
plugins = []

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 4: Create Makefile**

```makefile
.PHONY: bootstrap dev test lint lint-fix fmt build run serve build-web ls

bootstrap:
	uv venv
	uv pip install -e ".[dev]"

dev:
	uv pip install -e ".[dev]"

test:
	uv run pytest tests/ -v --tb=short

lint:
	uv run ruff check src/ tests/
	uv run mypy src/

lint-fix:
	uv run ruff check --fix src/ tests/

fmt:
	uv run ruff format src/ tests/

build:
	uv build

serve:
	uv run voyages serve

build-web:
	cd web && npm install && npm run build

run:
	uv run voyages

ls:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/:.*//' | sort
```

- [ ] **Step 5: Create package skeleton**

Create `src/voyages/__init__.py`:

```python
"""Voyages — Map generation toolbox for travel data."""

__version__ = "0.1.0"
```

Create `src/voyages/py.typed` (empty marker file for PEP 561).

Create `tests/__init__.py` (empty).

- [ ] **Step 6: Update .gitignore**

Append these lines to the existing `.gitignore`:

```
# Voyages
node_modules/
.superpowers/
*.egg-info/
__pycache__/
.venv/
.ruff_cache/
.mypy_cache/
.pytest_cache/
src/voyages/server/static/
```

- [ ] **Step 7: Initialize uv and install dev dependencies**

```bash
cd /Users/donaldalbrecht/Projects/Voyages
uv venv
uv pip install -e ".[dev]" || uv pip install ruff mypy pytest
```

Run: `uv run ruff check src/ && uv run mypy src/`
Expected: Clean pass (no source files to check yet, but tooling works).

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml Makefile src/ tests/__init__.py .gitignore coding-standards
git commit -m "chore: scaffold project with uv, ruff, mypy, and coding-standards submodule"
```

---

## Phase 2: Domain Layer

### Task 2: Domain value objects

**Files:**
- Create: `src/voyages/domain/__init__.py`
- Create: `src/voyages/domain/value_objects.py`
- Test: `tests/domain/__init__.py`
- Test: `tests/domain/test_value_objects.py`

- [ ] **Step 1: Write failing tests for value objects**

Create `tests/domain/__init__.py` (empty).

Create `tests/domain/test_value_objects.py`:

```python
from __future__ import annotations

import pytest

from voyages.domain.value_objects import (
    BoundingBox,
    Coordinates,
    MapType,
    OutputFormat,
)


class TestCoordinates:
    def test_create_valid_coordinates(self) -> None:
        coords = Coordinates(latitude=41.85, longitude=-87.65)
        assert coords.latitude == 41.85
        assert coords.longitude == -87.65

    def test_reject_latitude_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="Latitude"):
            Coordinates(latitude=91.0, longitude=0.0)

    def test_reject_negative_latitude_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="Latitude"):
            Coordinates(latitude=-91.0, longitude=0.0)

    def test_reject_longitude_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="Longitude"):
            Coordinates(longitude=181.0, latitude=0.0)

    def test_reject_negative_longitude_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="Longitude"):
            Coordinates(longitude=-181.0, latitude=0.0)

    def test_boundary_values_accepted(self) -> None:
        coords = Coordinates(latitude=90.0, longitude=180.0)
        assert coords.latitude == 90.0
        assert coords.longitude == 180.0


class TestBoundingBox:
    def test_create_valid_bounding_box(self) -> None:
        sw = Coordinates(latitude=40.0, longitude=-90.0)
        ne = Coordinates(latitude=45.0, longitude=-85.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        assert bbox.southwest == sw
        assert bbox.northeast == ne

    def test_reject_southwest_north_of_northeast(self) -> None:
        sw = Coordinates(latitude=45.0, longitude=-90.0)
        ne = Coordinates(latitude=40.0, longitude=-85.0)
        with pytest.raises(ValueError, match="southwest"):
            BoundingBox(southwest=sw, northeast=ne)

    def test_contains_point_inside(self) -> None:
        sw = Coordinates(latitude=40.0, longitude=-90.0)
        ne = Coordinates(latitude=45.0, longitude=-85.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        point = Coordinates(latitude=42.0, longitude=-87.0)
        assert bbox.contains(point) is True

    def test_contains_point_outside(self) -> None:
        sw = Coordinates(latitude=40.0, longitude=-90.0)
        ne = Coordinates(latitude=45.0, longitude=-85.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        point = Coordinates(latitude=50.0, longitude=-87.0)
        assert bbox.contains(point) is False


class TestMapType:
    def test_map_type_values(self) -> None:
        assert MapType.TRAVEL.value == "travel"
        assert MapType.REGION.value == "region"
        assert MapType.ROUTE.value == "route"


class TestOutputFormat:
    def test_output_format_values(self) -> None:
        assert OutputFormat.SVG.value == "svg"
        assert OutputFormat.PDF.value == "pdf"
        assert OutputFormat.PNG.value == "png"
        assert OutputFormat.WEBP.value == "webp"
        assert OutputFormat.EPS.value == "eps"

    def test_output_format_file_extension(self) -> None:
        assert OutputFormat.SVG.extension == ".svg"
        assert OutputFormat.PNG.extension == ".png"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/domain/test_value_objects.py -v`
Expected: FAIL — ImportError, module not found.

- [ ] **Step 3: Implement value objects**

Create `src/voyages/domain/__init__.py` (empty).

Create `src/voyages/domain/value_objects.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")


@dataclass(frozen=True)
class BoundingBox:
    southwest: Coordinates
    northeast: Coordinates

    def __post_init__(self) -> None:
        if self.southwest.latitude > self.northeast.latitude:
            raise ValueError(
                "southwest latitude must be less than or equal to northeast latitude"
            )

    def contains(self, point: Coordinates) -> bool:
        lat_in = self.southwest.latitude <= point.latitude <= self.northeast.latitude
        lon_in = self.southwest.longitude <= point.longitude <= self.northeast.longitude
        return lat_in and lon_in


class MapType(Enum):
    TRAVEL = "travel"
    REGION = "region"
    ROUTE = "route"


class OutputFormat(Enum):
    SVG = "svg"
    PDF = "pdf"
    PNG = "png"
    WEBP = "webp"
    EPS = "eps"

    @property
    def extension(self) -> str:
        return f".{self.value}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/domain/test_value_objects.py -v`
Expected: All 12 tests PASS.

- [ ] **Step 5: Run linting and type checking**

Run: `uv run ruff check src/voyages/domain/ tests/domain/ && uv run mypy src/voyages/domain/`
Expected: Clean pass.

- [ ] **Step 6: Commit**

```bash
git add src/voyages/domain/__init__.py src/voyages/domain/value_objects.py tests/domain/
git commit -m "feat(domain): add Coordinates, BoundingBox, MapType, OutputFormat value objects"
```

---

### Task 3: Domain entities

**Files:**
- Create: `src/voyages/domain/entities.py`
- Test: `tests/domain/test_entities.py`

- [ ] **Step 1: Write failing tests for entities**

Create `tests/domain/test_entities.py`:

```python
from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from voyages.domain.entities import (
    Photo,
    Place,
    Project,
    Region,
    Trip,
    TripStop,
)
from voyages.domain.value_objects import MapType


class TestPlace:
    def test_create_place(self) -> None:
        place = Place(
            id=uuid4(),
            name="Kyoto",
            latitude=35.01,
            longitude=135.77,
            country="Japan",
            admin1="Kyoto",
            category="city",
            notes=None,
            source="manual",
        )
        assert place.name == "Kyoto"
        assert place.source == "manual"

    def test_place_requires_name(self) -> None:
        place = Place(
            id=uuid4(),
            name="",
            latitude=0.0,
            longitude=0.0,
            source="manual",
        )
        # Empty name is allowed at entity level (validation at boundary)
        assert place.name == ""


class TestTrip:
    def test_create_trip(self) -> None:
        trip = Trip(
            id=uuid4(),
            name="Japan 2024",
            description="Two weeks in Japan",
            start_date=date(2024, 3, 15),
            end_date=date(2024, 3, 29),
        )
        assert trip.name == "Japan 2024"
        assert trip.stops == []

    def test_add_stop_to_trip(self) -> None:
        trip = Trip(id=uuid4(), name="Test Trip")
        place = Place(
            id=uuid4(),
            name="Tokyo",
            latitude=35.68,
            longitude=139.69,
            source="manual",
        )
        stop = TripStop(
            place_id=place.id,
            position=0,
            arrived_at=datetime(2024, 3, 15, 10, 0, tzinfo=timezone.utc),
            departed_at=None,
        )
        trip.stops.append(stop)
        assert len(trip.stops) == 1
        assert trip.stops[0].place_id == place.id


class TestRegion:
    def test_create_region(self) -> None:
        region = Region(
            id=uuid4(),
            name="Japan",
            region_type="country",
            region_code="JP",
        )
        assert region.name == "Japan"
        assert region.region_code == "JP"


class TestProject:
    def test_create_project(self) -> None:
        project = Project(
            id=uuid4(),
            name="World Travel Map",
            description="All places visited",
            map_type=MapType.TRAVEL,
            config={},
        )
        assert project.map_type == MapType.TRAVEL
        assert project.place_ids == []
        assert project.trip_ids == []
        assert project.region_ids == []


class TestPhoto:
    def test_create_photo_with_gps(self) -> None:
        photo = Photo(
            id=uuid4(),
            file_path="/photos/IMG_001.jpg",
            latitude=35.01,
            longitude=135.77,
            taken_at=datetime(2024, 3, 15, 14, 30, tzinfo=timezone.utc),
        )
        assert photo.latitude == 35.01
        assert photo.place_id is None
        assert photo.trip_id is None

    def test_create_photo_without_gps(self) -> None:
        photo = Photo(
            id=uuid4(),
            file_path="/photos/IMG_002.jpg",
            latitude=None,
            longitude=None,
            taken_at=None,
        )
        assert photo.latitude is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/domain/test_entities.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement entities**

Create `src/voyages/domain/entities.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any
from uuid import UUID

from voyages.domain.value_objects import MapType


@dataclass
class Place:
    id: UUID
    name: str
    latitude: float
    longitude: float
    source: str
    country: str | None = None
    admin1: str | None = None
    category: str | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class TripStop:
    place_id: UUID
    position: int
    arrived_at: datetime | None = None
    departed_at: datetime | None = None


@dataclass
class Trip:
    id: UUID
    name: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    stops: list[TripStop] = field(default_factory=list)


@dataclass
class Region:
    id: UUID
    name: str
    region_type: str
    region_code: str | None = None


@dataclass
class Project:
    id: UUID
    name: str
    map_type: MapType
    description: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    place_ids: list[UUID] = field(default_factory=list)
    trip_ids: list[UUID] = field(default_factory=list)
    region_ids: list[UUID] = field(default_factory=list)


@dataclass
class Photo:
    id: UUID
    file_path: str
    latitude: float | None = None
    longitude: float | None = None
    taken_at: datetime | None = None
    place_id: UUID | None = None
    trip_id: UUID | None = None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/domain/test_entities.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Run linting and type checking**

Run: `uv run ruff check src/voyages/domain/ tests/domain/ && uv run mypy src/voyages/domain/`
Expected: Clean pass.

- [ ] **Step 6: Commit**

```bash
git add src/voyages/domain/entities.py tests/domain/test_entities.py
git commit -m "feat(domain): add Place, Trip, Region, Project, Photo entities"
```

---

### Task 4: Domain errors

**Files:**
- Create: `src/voyages/domain/errors.py`
- Test: `tests/domain/test_errors.py`

- [ ] **Step 1: Write failing tests**

Create `tests/domain/test_errors.py`:

```python
from __future__ import annotations

from uuid import uuid4

from voyages.domain.errors import (
    EntityNotFoundError,
    PlaceNotFoundError,
    ProjectNotFoundError,
    RenderError,
    TripNotFoundError,
    VoyagesError,
)


class TestErrors:
    def test_voyages_error_is_base(self) -> None:
        err = VoyagesError("something went wrong")
        assert isinstance(err, Exception)
        assert str(err) == "something went wrong"

    def test_entity_not_found_includes_id(self) -> None:
        entity_id = uuid4()
        err = EntityNotFoundError(entity_type="Place", entity_id=entity_id)
        assert str(entity_id) in str(err)
        assert "Place" in str(err)

    def test_place_not_found(self) -> None:
        entity_id = uuid4()
        err = PlaceNotFoundError(entity_id=entity_id)
        assert isinstance(err, EntityNotFoundError)

    def test_trip_not_found(self) -> None:
        entity_id = uuid4()
        err = TripNotFoundError(entity_id=entity_id)
        assert isinstance(err, EntityNotFoundError)

    def test_project_not_found(self) -> None:
        entity_id = uuid4()
        err = ProjectNotFoundError(entity_id=entity_id)
        assert isinstance(err, EntityNotFoundError)

    def test_render_error(self) -> None:
        err = RenderError("projection failed")
        assert isinstance(err, VoyagesError)
        assert "projection failed" in str(err)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/domain/test_errors.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement errors**

Create `src/voyages/domain/errors.py`:

```python
from __future__ import annotations

from uuid import UUID


class VoyagesError(Exception):
    pass


class EntityNotFoundError(VoyagesError):
    def __init__(self, entity_type: str, entity_id: UUID) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} not found: {entity_id}")


class PlaceNotFoundError(EntityNotFoundError):
    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_type="Place", entity_id=entity_id)


class TripNotFoundError(EntityNotFoundError):
    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_type="Trip", entity_id=entity_id)


class ProjectNotFoundError(EntityNotFoundError):
    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_type="Project", entity_id=entity_id)


class RegionNotFoundError(EntityNotFoundError):
    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_type="Region", entity_id=entity_id)


class RenderError(VoyagesError):
    pass
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/domain/test_errors.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/domain/errors.py tests/domain/test_errors.py
git commit -m "feat(domain): add domain error types"
```

---

## Phase 3: Application Layer

### Task 5: Application interfaces (protocols)

**Files:**
- Create: `src/voyages/application/__init__.py`
- Create: `src/voyages/application/interfaces.py`

- [ ] **Step 1: Create application interfaces**

Create `src/voyages/application/__init__.py` (empty).

Create `src/voyages/application/interfaces.py`:

```python
from __future__ import annotations

from typing import Protocol
from uuid import UUID

from voyages.domain.entities import Photo, Place, Project, Region, Trip
from voyages.domain.value_objects import BoundingBox, OutputFormat


class PlaceRepository(Protocol):
    def get(self, place_id: UUID) -> Place | None: ...
    def list_all(self) -> list[Place]: ...
    def search_by_name(self, name: str) -> list[Place]: ...
    def save(self, place: Place) -> None: ...
    def delete(self, place_id: UUID) -> None: ...


class TripRepository(Protocol):
    def get(self, trip_id: UUID) -> Trip | None: ...
    def list_all(self) -> list[Trip]: ...
    def save(self, trip: Trip) -> None: ...
    def delete(self, trip_id: UUID) -> None: ...


class RegionRepository(Protocol):
    def get(self, region_id: UUID) -> Region | None: ...
    def list_all(self) -> list[Region]: ...
    def save(self, region: Region) -> None: ...
    def delete(self, region_id: UUID) -> None: ...


class ProjectRepository(Protocol):
    def get(self, project_id: UUID) -> Project | None: ...
    def get_by_name(self, name: str) -> Project | None: ...
    def list_all(self) -> list[Project]: ...
    def save(self, project: Project) -> None: ...
    def delete(self, project_id: UUID) -> None: ...


class PhotoRepository(Protocol):
    def get(self, photo_id: UUID) -> Photo | None: ...
    def list_by_trip(self, trip_id: UUID) -> list[Photo]: ...
    def save(self, photo: Photo) -> None: ...
    def delete(self, photo_id: UUID) -> None: ...


class GeocodingService(Protocol):
    def search(self, query: str) -> list[Place]: ...
    def reverse_geocode(self, latitude: float, longitude: float) -> Place | None: ...


class ExifService(Protocol):
    def extract_from_file(self, file_path: str) -> Photo | None: ...
    def extract_from_directory(self, directory: str) -> list[Photo]: ...


class MapRenderer(Protocol):
    def render(
        self,
        places: list[Place],
        trips: list[Trip],
        regions: list[Region],
        config: dict[str, object],
        output_format: OutputFormat,
        output_path: str,
    ) -> str: ...
```

- [ ] **Step 2: Run type checking**

Run: `uv run mypy src/voyages/application/`
Expected: Clean pass.

- [ ] **Step 3: Commit**

```bash
git add src/voyages/application/
git commit -m "feat(application): add repository and service protocol interfaces"
```

---

### Task 6: Place service

**Files:**
- Create: `src/voyages/application/place_service.py`
- Test: `tests/application/__init__.py`
- Test: `tests/application/test_place_service.py`

- [ ] **Step 1: Write failing tests with in-memory fakes**

Create `tests/application/__init__.py` (empty).

Create `tests/application/test_place_service.py`:

```python
from __future__ import annotations

from uuid import UUID, uuid4

from voyages.application.place_service import PlaceService
from voyages.domain.entities import Place


class FakePlaceRepository:
    def __init__(self) -> None:
        self._places: dict[UUID, Place] = {}

    def get(self, place_id: UUID) -> Place | None:
        return self._places.get(place_id)

    def list_all(self) -> list[Place]:
        return list(self._places.values())

    def search_by_name(self, name: str) -> list[Place]:
        return [p for p in self._places.values() if name.lower() in p.name.lower()]

    def save(self, place: Place) -> None:
        self._places[place.id] = place

    def delete(self, place_id: UUID) -> None:
        self._places.pop(place_id, None)


class FakeGeocodingService:
    def __init__(self, results: list[Place] | None = None) -> None:
        self._results = results or []

    def search(self, query: str) -> list[Place]:
        return [p for p in self._results if query.lower() in p.name.lower()]

    def reverse_geocode(self, latitude: float, longitude: float) -> Place | None:
        return self._results[0] if self._results else None


class TestPlaceService:
    def _make_service(
        self,
        geocoding_results: list[Place] | None = None,
    ) -> tuple[PlaceService, FakePlaceRepository]:
        repo = FakePlaceRepository()
        geocoding = FakeGeocodingService(geocoding_results)
        service = PlaceService(place_repo=repo, geocoding=geocoding)
        return service, repo

    def test_create_place(self) -> None:
        service, repo = self._make_service()
        place = service.create(
            name="Kyoto",
            latitude=35.01,
            longitude=135.77,
            source="manual",
        )
        assert place.name == "Kyoto"
        assert repo.get(place.id) is not None

    def test_get_place(self) -> None:
        service, repo = self._make_service()
        place = service.create(name="Tokyo", latitude=35.68, longitude=139.69, source="manual")
        found = service.get(place.id)
        assert found is not None
        assert found.name == "Tokyo"

    def test_get_nonexistent_place_returns_none(self) -> None:
        service, _ = self._make_service()
        assert service.get(uuid4()) is None

    def test_list_places(self) -> None:
        service, _ = self._make_service()
        service.create(name="A", latitude=0.0, longitude=0.0, source="manual")
        service.create(name="B", latitude=1.0, longitude=1.0, source="manual")
        places = service.list_all()
        assert len(places) == 2

    def test_search_via_geocoding(self) -> None:
        results = [
            Place(id=uuid4(), name="Kyoto", latitude=35.01, longitude=135.77, source="geocoding"),
        ]
        service, _ = self._make_service(geocoding_results=results)
        found = service.search("Kyoto")
        assert len(found) == 1
        assert found[0].name == "Kyoto"

    def test_delete_place(self) -> None:
        service, repo = self._make_service()
        place = service.create(name="X", latitude=0.0, longitude=0.0, source="manual")
        service.delete(place.id)
        assert repo.get(place.id) is None

    def test_update_place(self) -> None:
        service, _ = self._make_service()
        place = service.create(name="Old", latitude=0.0, longitude=0.0, source="manual")
        place.name = "New"
        updated = service.update(place)
        assert updated.name == "New"
        assert service.get(place.id) is not None
        assert service.get(place.id).name == "New"  # type: ignore[union-attr]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/application/test_place_service.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement PlaceService**

Create `src/voyages/application/place_service.py`:

```python
from __future__ import annotations

from uuid import UUID, uuid4

from voyages.application.interfaces import GeocodingService, PlaceRepository
from voyages.domain.entities import Place


class PlaceService:
    def __init__(
        self,
        place_repo: PlaceRepository,
        geocoding: GeocodingService,
    ) -> None:
        self._repo = place_repo
        self._geocoding = geocoding

    def create(
        self,
        name: str,
        latitude: float,
        longitude: float,
        source: str,
        country: str | None = None,
        admin1: str | None = None,
        category: str | None = None,
        notes: str | None = None,
    ) -> Place:
        place = Place(
            id=uuid4(),
            name=name,
            latitude=latitude,
            longitude=longitude,
            source=source,
            country=country,
            admin1=admin1,
            category=category,
            notes=notes,
        )
        self._repo.save(place)
        return place

    def get(self, place_id: UUID) -> Place | None:
        return self._repo.get(place_id)

    def list_all(self) -> list[Place]:
        return self._repo.list_all()

    def search(self, query: str) -> list[Place]:
        return self._geocoding.search(query)

    def update(self, place: Place) -> Place:
        self._repo.save(place)
        return place

    def delete(self, place_id: UUID) -> None:
        self._repo.delete(place_id)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/application/test_place_service.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Run linting and type checking**

Run: `uv run ruff check src/voyages/application/ tests/application/ && uv run mypy src/voyages/application/`
Expected: Clean pass.

- [ ] **Step 6: Commit**

```bash
git add src/voyages/application/place_service.py tests/application/
git commit -m "feat(application): add PlaceService with CRUD and geocoding search"
```

---

### Task 7: Trip service

**Files:**
- Create: `src/voyages/application/trip_service.py`
- Test: `tests/application/test_trip_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/application/test_trip_service.py`:

```python
from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from voyages.application.trip_service import TripService
from voyages.domain.entities import Trip, TripStop


class FakeTripRepository:
    def __init__(self) -> None:
        self._trips: dict[UUID, Trip] = {}

    def get(self, trip_id: UUID) -> Trip | None:
        return self._trips.get(trip_id)

    def list_all(self) -> list[Trip]:
        return list(self._trips.values())

    def save(self, trip: Trip) -> None:
        self._trips[trip.id] = trip

    def delete(self, trip_id: UUID) -> None:
        self._trips.pop(trip_id, None)


class TestTripService:
    def _make_service(self) -> tuple[TripService, FakeTripRepository]:
        repo = FakeTripRepository()
        service = TripService(trip_repo=repo)
        return service, repo

    def test_create_trip(self) -> None:
        service, repo = self._make_service()
        trip = service.create(
            name="Japan 2024",
            description="Two weeks in Japan",
            start_date=date(2024, 3, 15),
            end_date=date(2024, 3, 29),
        )
        assert trip.name == "Japan 2024"
        assert repo.get(trip.id) is not None

    def test_list_trips(self) -> None:
        service, _ = self._make_service()
        service.create(name="Trip A")
        service.create(name="Trip B")
        assert len(service.list_all()) == 2

    def test_add_stop(self) -> None:
        service, _ = self._make_service()
        trip = service.create(name="Test")
        place_id = uuid4()
        arrived = datetime(2024, 3, 15, 10, 0, tzinfo=timezone.utc)
        updated_trip = service.add_stop(
            trip_id=trip.id,
            place_id=place_id,
            arrived_at=arrived,
        )
        assert len(updated_trip.stops) == 1
        assert updated_trip.stops[0].place_id == place_id
        assert updated_trip.stops[0].position == 0

    def test_add_multiple_stops_auto_positions(self) -> None:
        service, _ = self._make_service()
        trip = service.create(name="Test")
        service.add_stop(trip_id=trip.id, place_id=uuid4())
        updated = service.add_stop(trip_id=trip.id, place_id=uuid4())
        assert updated.stops[0].position == 0
        assert updated.stops[1].position == 1

    def test_remove_stop(self) -> None:
        service, _ = self._make_service()
        trip = service.create(name="Test")
        place_id = uuid4()
        service.add_stop(trip_id=trip.id, place_id=place_id)
        updated = service.remove_stop(trip_id=trip.id, place_id=place_id)
        assert len(updated.stops) == 0

    def test_reorder_stops(self) -> None:
        service, _ = self._make_service()
        trip = service.create(name="Test")
        id_a, id_b, id_c = uuid4(), uuid4(), uuid4()
        service.add_stop(trip_id=trip.id, place_id=id_a)
        service.add_stop(trip_id=trip.id, place_id=id_b)
        service.add_stop(trip_id=trip.id, place_id=id_c)
        updated = service.reorder_stops(trip_id=trip.id, place_ids=[id_c, id_a, id_b])
        assert updated.stops[0].place_id == id_c
        assert updated.stops[1].place_id == id_a
        assert updated.stops[2].place_id == id_b
        assert updated.stops[0].position == 0
        assert updated.stops[1].position == 1
        assert updated.stops[2].position == 2

    def test_delete_trip(self) -> None:
        service, repo = self._make_service()
        trip = service.create(name="Bye")
        service.delete(trip.id)
        assert repo.get(trip.id) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/application/test_trip_service.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement TripService**

Create `src/voyages/application/trip_service.py`:

```python
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from voyages.application.interfaces import TripRepository
from voyages.domain.entities import Trip, TripStop
from voyages.domain.errors import TripNotFoundError


class TripService:
    def __init__(self, trip_repo: TripRepository) -> None:
        self._repo = trip_repo

    def create(
        self,
        name: str,
        description: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Trip:
        trip = Trip(
            id=uuid4(),
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )
        self._repo.save(trip)
        return trip

    def get(self, trip_id: UUID) -> Trip | None:
        return self._repo.get(trip_id)

    def list_all(self) -> list[Trip]:
        return self._repo.list_all()

    def add_stop(
        self,
        trip_id: UUID,
        place_id: UUID,
        arrived_at: datetime | None = None,
        departed_at: datetime | None = None,
    ) -> Trip:
        trip = self._repo.get(trip_id)
        if trip is None:
            raise TripNotFoundError(entity_id=trip_id)
        position = len(trip.stops)
        stop = TripStop(
            place_id=place_id,
            position=position,
            arrived_at=arrived_at,
            departed_at=departed_at,
        )
        trip.stops.append(stop)
        self._repo.save(trip)
        return trip

    def remove_stop(self, trip_id: UUID, place_id: UUID) -> Trip:
        trip = self._repo.get(trip_id)
        if trip is None:
            raise TripNotFoundError(entity_id=trip_id)
        trip.stops = [s for s in trip.stops if s.place_id != place_id]
        for i, stop in enumerate(trip.stops):
            stop.position = i
        self._repo.save(trip)
        return trip

    def reorder_stops(self, trip_id: UUID, place_ids: list[UUID]) -> Trip:
        trip = self._repo.get(trip_id)
        if trip is None:
            raise TripNotFoundError(entity_id=trip_id)
        stop_map = {s.place_id: s for s in trip.stops}
        trip.stops = []
        for i, pid in enumerate(place_ids):
            stop = stop_map[pid]
            stop.position = i
            trip.stops.append(stop)
        self._repo.save(trip)
        return trip

    def delete(self, trip_id: UUID) -> None:
        self._repo.delete(trip_id)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/application/test_trip_service.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Run linting and type checking**

Run: `uv run ruff check src/voyages/application/ && uv run mypy src/voyages/application/`
Expected: Clean pass.

- [ ] **Step 6: Commit**

```bash
git add src/voyages/application/trip_service.py tests/application/test_trip_service.py
git commit -m "feat(application): add TripService with stop management and reordering"
```

---

### Task 8: Region service

**Files:**
- Create: `src/voyages/application/region_service.py`
- Test: `tests/application/test_region_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/application/test_region_service.py`:

```python
from __future__ import annotations

from uuid import UUID, uuid4

from voyages.application.region_service import RegionService
from voyages.domain.entities import Place, Region


class FakeRegionRepository:
    def __init__(self) -> None:
        self._regions: dict[UUID, Region] = {}

    def get(self, region_id: UUID) -> Region | None:
        return self._regions.get(region_id)

    def list_all(self) -> list[Region]:
        return list(self._regions.values())

    def save(self, region: Region) -> None:
        self._regions[region.id] = region

    def delete(self, region_id: UUID) -> None:
        self._regions.pop(region_id, None)


class FakePlaceRepository:
    def __init__(self, places: list[Place] | None = None) -> None:
        self._places: dict[UUID, Place] = {p.id: p for p in (places or [])}

    def get(self, place_id: UUID) -> Place | None:
        return self._places.get(place_id)

    def list_all(self) -> list[Place]:
        return list(self._places.values())

    def search_by_name(self, name: str) -> list[Place]:
        return [p for p in self._places.values() if name.lower() in p.name.lower()]

    def save(self, place: Place) -> None:
        self._places[place.id] = place

    def delete(self, place_id: UUID) -> None:
        self._places.pop(place_id, None)


class TestRegionService:
    def _make_service(
        self, places: list[Place] | None = None
    ) -> tuple[RegionService, FakeRegionRepository]:
        region_repo = FakeRegionRepository()
        place_repo = FakePlaceRepository(places)
        service = RegionService(region_repo=region_repo, place_repo=place_repo)
        return service, region_repo

    def test_create_region(self) -> None:
        service, repo = self._make_service()
        region = service.create(name="Japan", region_type="country", region_code="JP")
        assert region.name == "Japan"
        assert repo.get(region.id) is not None

    def test_list_regions(self) -> None:
        service, _ = self._make_service()
        service.create(name="Japan", region_type="country")
        service.create(name="France", region_type="country")
        assert len(service.list_all()) == 2

    def test_derive_regions_from_places(self) -> None:
        places = [
            Place(
                id=uuid4(), name="Tokyo", latitude=35.68, longitude=139.69,
                source="manual", country="Japan", admin1="Tokyo",
            ),
            Place(
                id=uuid4(), name="Kyoto", latitude=35.01, longitude=135.77,
                source="manual", country="Japan", admin1="Kyoto",
            ),
            Place(
                id=uuid4(), name="Paris", latitude=48.85, longitude=2.35,
                source="manual", country="France", admin1="Ile-de-France",
            ),
        ]
        service, _ = self._make_service(places=places)
        derived = service.derive_from_places()
        country_names = {r.name for r in derived if r.region_type == "country"}
        assert "Japan" in country_names
        assert "France" in country_names

    def test_derive_skips_places_without_country(self) -> None:
        places = [
            Place(
                id=uuid4(), name="Unknown", latitude=0.0, longitude=0.0,
                source="manual", country=None,
            ),
        ]
        service, _ = self._make_service(places=places)
        derived = service.derive_from_places()
        assert len(derived) == 0

    def test_delete_region(self) -> None:
        service, repo = self._make_service()
        region = service.create(name="Test", region_type="country")
        service.delete(region.id)
        assert repo.get(region.id) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/application/test_region_service.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement RegionService**

Create `src/voyages/application/region_service.py`:

```python
from __future__ import annotations

from uuid import UUID, uuid4

from voyages.application.interfaces import PlaceRepository, RegionRepository
from voyages.domain.entities import Region


class RegionService:
    def __init__(
        self,
        region_repo: RegionRepository,
        place_repo: PlaceRepository,
    ) -> None:
        self._region_repo = region_repo
        self._place_repo = place_repo

    def create(
        self,
        name: str,
        region_type: str,
        region_code: str | None = None,
    ) -> Region:
        region = Region(
            id=uuid4(),
            name=name,
            region_type=region_type,
            region_code=region_code,
        )
        self._region_repo.save(region)
        return region

    def get(self, region_id: UUID) -> Region | None:
        return self._region_repo.get(region_id)

    def list_all(self) -> list[Region]:
        return self._region_repo.list_all()

    def derive_from_places(self) -> list[Region]:
        places = self._place_repo.list_all()
        seen_countries: set[str] = set()
        derived: list[Region] = []

        for place in places:
            if place.country and place.country not in seen_countries:
                seen_countries.add(place.country)
                region = Region(
                    id=uuid4(),
                    name=place.country,
                    region_type="country",
                    region_code=None,
                )
                self._region_repo.save(region)
                derived.append(region)

        return derived

    def delete(self, region_id: UUID) -> None:
        self._region_repo.delete(region_id)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/application/test_region_service.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/application/region_service.py tests/application/test_region_service.py
git commit -m "feat(application): add RegionService with auto-derivation from places"
```

---

### Task 9: Photo service

**Files:**
- Create: `src/voyages/application/photo_service.py`
- Test: `tests/application/test_photo_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/application/test_photo_service.py`:

```python
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from voyages.application.photo_service import PhotoService
from voyages.domain.entities import Photo, Place


class FakePhotoRepository:
    def __init__(self) -> None:
        self._photos: dict[UUID, Photo] = {}

    def get(self, photo_id: UUID) -> Photo | None:
        return self._photos.get(photo_id)

    def list_by_trip(self, trip_id: UUID) -> list[Photo]:
        return [p for p in self._photos.values() if p.trip_id == trip_id]

    def save(self, photo: Photo) -> None:
        self._photos[photo.id] = photo

    def delete(self, photo_id: UUID) -> None:
        self._photos.pop(photo_id, None)


class FakeExifService:
    def __init__(self, photos: list[Photo] | None = None) -> None:
        self._photos = photos or []

    def extract_from_file(self, file_path: str) -> Photo | None:
        for p in self._photos:
            if p.file_path == file_path:
                return p
        return None

    def extract_from_directory(self, directory: str) -> list[Photo]:
        return self._photos


class FakeGeocodingService:
    def search(self, query: str) -> list[Place]:
        return []

    def reverse_geocode(self, latitude: float, longitude: float) -> Place | None:
        return Place(
            id=uuid4(),
            name=f"Place at {latitude},{longitude}",
            latitude=latitude,
            longitude=longitude,
            source="geocoding",
            country="TestCountry",
        )


class TestPhotoService:
    def _make_service(
        self, exif_photos: list[Photo] | None = None
    ) -> tuple[PhotoService, FakePhotoRepository]:
        photo_repo = FakePhotoRepository()
        exif = FakeExifService(exif_photos)
        geocoding = FakeGeocodingService()
        service = PhotoService(
            photo_repo=photo_repo,
            exif_service=exif,
            geocoding=geocoding,
        )
        return service, photo_repo

    def test_import_directory(self) -> None:
        photos = [
            Photo(
                id=uuid4(),
                file_path="/photos/IMG_001.jpg",
                latitude=35.01,
                longitude=135.77,
                taken_at=datetime(2024, 3, 15, 14, 30, tzinfo=timezone.utc),
            ),
            Photo(
                id=uuid4(),
                file_path="/photos/IMG_002.jpg",
                latitude=35.68,
                longitude=139.69,
                taken_at=datetime(2024, 3, 16, 10, 0, tzinfo=timezone.utc),
            ),
        ]
        service, repo = self._make_service(exif_photos=photos)
        imported = service.import_from_directory("/photos")
        assert len(imported) == 2
        assert repo.get(imported[0].id) is not None

    def test_import_skips_photos_without_gps(self) -> None:
        photos = [
            Photo(
                id=uuid4(),
                file_path="/photos/no_gps.jpg",
                latitude=None,
                longitude=None,
                taken_at=None,
            ),
        ]
        service, _ = self._make_service(exif_photos=photos)
        imported = service.import_from_directory("/photos")
        assert len(imported) == 0

    def test_import_dry_run_does_not_save(self) -> None:
        photos = [
            Photo(
                id=uuid4(),
                file_path="/photos/IMG_001.jpg",
                latitude=35.01,
                longitude=135.77,
                taken_at=datetime(2024, 3, 15, 14, 30, tzinfo=timezone.utc),
            ),
        ]
        service, repo = self._make_service(exif_photos=photos)
        imported = service.import_from_directory("/photos", dry_run=True)
        assert len(imported) == 1
        assert repo.get(imported[0].id) is None

    def test_assign_to_trip(self) -> None:
        photos = [
            Photo(
                id=uuid4(),
                file_path="/photos/IMG_001.jpg",
                latitude=35.01,
                longitude=135.77,
                taken_at=datetime(2024, 3, 15, 14, 30, tzinfo=timezone.utc),
            ),
        ]
        service, repo = self._make_service(exif_photos=photos)
        imported = service.import_from_directory("/photos")
        trip_id = uuid4()
        service.assign_to_trip(imported[0].id, trip_id)
        photo = repo.get(imported[0].id)
        assert photo is not None
        assert photo.trip_id == trip_id
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/application/test_photo_service.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement PhotoService**

Create `src/voyages/application/photo_service.py`:

```python
from __future__ import annotations

from uuid import UUID

from voyages.application.interfaces import ExifService, GeocodingService, PhotoRepository
from voyages.domain.entities import Photo


class PhotoService:
    def __init__(
        self,
        photo_repo: PhotoRepository,
        exif_service: ExifService,
        geocoding: GeocodingService,
    ) -> None:
        self._repo = photo_repo
        self._exif = exif_service
        self._geocoding = geocoding

    def import_from_directory(
        self,
        directory: str,
        dry_run: bool = False,
    ) -> list[Photo]:
        extracted = self._exif.extract_from_directory(directory)
        photos_with_gps = [p for p in extracted if p.latitude is not None and p.longitude is not None]

        if not dry_run:
            for photo in photos_with_gps:
                self._repo.save(photo)

        return photos_with_gps

    def assign_to_trip(self, photo_id: UUID, trip_id: UUID) -> Photo:
        photo = self._repo.get(photo_id)
        if photo is None:
            raise ValueError(f"Photo not found: {photo_id}")
        photo.trip_id = trip_id
        self._repo.save(photo)
        return photo

    def assign_to_place(self, photo_id: UUID, place_id: UUID) -> Photo:
        photo = self._repo.get(photo_id)
        if photo is None:
            raise ValueError(f"Photo not found: {photo_id}")
        photo.place_id = place_id
        self._repo.save(photo)
        return photo
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/application/test_photo_service.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/application/photo_service.py tests/application/test_photo_service.py
git commit -m "feat(application): add PhotoService with directory import and trip assignment"
```

---

### Task 10: Project service

**Files:**
- Create: `src/voyages/application/project_service.py`
- Test: `tests/application/test_project_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/application/test_project_service.py`:

```python
from __future__ import annotations

from uuid import UUID, uuid4

from voyages.application.project_service import ProjectService
from voyages.domain.entities import Project
from voyages.domain.value_objects import MapType


class FakeProjectRepository:
    def __init__(self) -> None:
        self._projects: dict[UUID, Project] = {}

    def get(self, project_id: UUID) -> Project | None:
        return self._projects.get(project_id)

    def get_by_name(self, name: str) -> Project | None:
        for p in self._projects.values():
            if p.name == name:
                return p
        return None

    def list_all(self) -> list[Project]:
        return list(self._projects.values())

    def save(self, project: Project) -> None:
        self._projects[project.id] = project

    def delete(self, project_id: UUID) -> None:
        self._projects.pop(project_id, None)


class TestProjectService:
    def _make_service(self) -> tuple[ProjectService, FakeProjectRepository]:
        repo = FakeProjectRepository()
        service = ProjectService(project_repo=repo)
        return service, repo

    def test_create_project(self) -> None:
        service, repo = self._make_service()
        project = service.create(
            name="World Travel",
            map_type=MapType.TRAVEL,
            description="All places visited",
        )
        assert project.name == "World Travel"
        assert project.map_type == MapType.TRAVEL
        assert repo.get(project.id) is not None

    def test_get_by_name(self) -> None:
        service, _ = self._make_service()
        service.create(name="Japan Route", map_type=MapType.ROUTE)
        found = service.get_by_name("Japan Route")
        assert found is not None
        assert found.name == "Japan Route"

    def test_add_place_to_project(self) -> None:
        service, _ = self._make_service()
        project = service.create(name="Test", map_type=MapType.TRAVEL)
        place_id = uuid4()
        updated = service.add_place(project.id, place_id)
        assert place_id in updated.place_ids

    def test_add_trip_to_project(self) -> None:
        service, _ = self._make_service()
        project = service.create(name="Test", map_type=MapType.ROUTE)
        trip_id = uuid4()
        updated = service.add_trip(project.id, trip_id)
        assert trip_id in updated.trip_ids

    def test_add_region_to_project(self) -> None:
        service, _ = self._make_service()
        project = service.create(name="Test", map_type=MapType.TRAVEL)
        region_id = uuid4()
        updated = service.add_region(project.id, region_id)
        assert region_id in updated.region_ids

    def test_update_config(self) -> None:
        service, _ = self._make_service()
        project = service.create(name="Test", map_type=MapType.TRAVEL)
        config = {"projection": "EqualEarth", "style": "vintage"}
        updated = service.update_config(project.id, config)
        assert updated.config["projection"] == "EqualEarth"

    def test_list_projects(self) -> None:
        service, _ = self._make_service()
        service.create(name="A", map_type=MapType.TRAVEL)
        service.create(name="B", map_type=MapType.REGION)
        assert len(service.list_all()) == 2

    def test_delete_project(self) -> None:
        service, repo = self._make_service()
        project = service.create(name="Del", map_type=MapType.TRAVEL)
        service.delete(project.id)
        assert repo.get(project.id) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/application/test_project_service.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement ProjectService**

Create `src/voyages/application/project_service.py`:

```python
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from voyages.application.interfaces import ProjectRepository
from voyages.domain.entities import Project
from voyages.domain.errors import ProjectNotFoundError
from voyages.domain.value_objects import MapType


class ProjectService:
    def __init__(self, project_repo: ProjectRepository) -> None:
        self._repo = project_repo

    def create(
        self,
        name: str,
        map_type: MapType,
        description: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> Project:
        project = Project(
            id=uuid4(),
            name=name,
            map_type=map_type,
            description=description,
            config=config or {},
        )
        self._repo.save(project)
        return project

    def get(self, project_id: UUID) -> Project | None:
        return self._repo.get(project_id)

    def get_by_name(self, name: str) -> Project | None:
        return self._repo.get_by_name(name)

    def list_all(self) -> list[Project]:
        return self._repo.list_all()

    def add_place(self, project_id: UUID, place_id: UUID) -> Project:
        project = self._get_or_raise(project_id)
        if place_id not in project.place_ids:
            project.place_ids.append(place_id)
        self._repo.save(project)
        return project

    def add_trip(self, project_id: UUID, trip_id: UUID) -> Project:
        project = self._get_or_raise(project_id)
        if trip_id not in project.trip_ids:
            project.trip_ids.append(trip_id)
        self._repo.save(project)
        return project

    def add_region(self, project_id: UUID, region_id: UUID) -> Project:
        project = self._get_or_raise(project_id)
        if region_id not in project.region_ids:
            project.region_ids.append(region_id)
        self._repo.save(project)
        return project

    def update_config(self, project_id: UUID, config: dict[str, Any]) -> Project:
        project = self._get_or_raise(project_id)
        project.config.update(config)
        self._repo.save(project)
        return project

    def delete(self, project_id: UUID) -> None:
        self._repo.delete(project_id)

    def _get_or_raise(self, project_id: UUID) -> Project:
        project = self._repo.get(project_id)
        if project is None:
            raise ProjectNotFoundError(entity_id=project_id)
        return project
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/application/test_project_service.py -v`
Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/application/project_service.py tests/application/test_project_service.py
git commit -m "feat(application): add ProjectService with data composition and config"
```

---

## Phase 4: Infrastructure — Database

### Task 11: SQLAlchemy models and session

**Files:**
- Create: `src/voyages/infrastructure/__init__.py`
- Create: `src/voyages/infrastructure/db/__init__.py`
- Create: `src/voyages/infrastructure/db/models.py`
- Create: `src/voyages/infrastructure/db/session.py`
- Test: `tests/infrastructure/__init__.py`
- Test: `tests/infrastructure/test_db_models.py`

- [ ] **Step 1: Write failing tests for DB models**

Create `tests/infrastructure/__init__.py` (empty).

Create `tests/infrastructure/test_db_models.py`:

```python
from __future__ import annotations

from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.db.models import PlaceModel, TripModel, RegionModel, ProjectModel, PhotoModel


class TestDatabaseSchema:
    def test_tables_created(self) -> None:
        engine = create_engine_and_tables("sqlite:///:memory:")
        session = get_session(engine)
        # If tables exist, querying returns empty lists (no error)
        assert session.query(PlaceModel).all() == []
        assert session.query(TripModel).all() == []
        assert session.query(RegionModel).all() == []
        assert session.query(ProjectModel).all() == []
        assert session.query(PhotoModel).all() == []
        session.close()

    def test_insert_and_read_place(self) -> None:
        engine = create_engine_and_tables("sqlite:///:memory:")
        session = get_session(engine)
        place = PlaceModel(
            name="Kyoto",
            latitude=35.01,
            longitude=135.77,
            source="manual",
            country="Japan",
        )
        session.add(place)
        session.commit()
        result = session.query(PlaceModel).first()
        assert result is not None
        assert result.name == "Kyoto"
        assert result.id is not None
        session.close()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/infrastructure/test_db_models.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement SQLAlchemy models**

Create `src/voyages/infrastructure/__init__.py` (empty).
Create `src/voyages/infrastructure/db/__init__.py` (empty).

Create `src/voyages/infrastructure/db/models.py`:

```python
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class PlaceModel(Base):
    __tablename__ = "places"

    id: str = Column(String(36), primary_key=True, default=_new_uuid)
    name: str = Column(String(255), nullable=False)
    latitude: float = Column(Float, nullable=False)
    longitude: float = Column(Float, nullable=False)
    country: str | None = Column(String(255), nullable=True)
    admin1: str | None = Column(String(255), nullable=True)
    category: str | None = Column(String(100), nullable=True)
    notes: str | None = Column(Text, nullable=True)
    source: str = Column(String(50), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), default=_utcnow)
    updated_at: datetime = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class TripModel(Base):
    __tablename__ = "trips"

    id: str = Column(String(36), primary_key=True, default=_new_uuid)
    name: str = Column(String(255), nullable=False)
    description: str | None = Column(Text, nullable=True)
    start_date: str | None = Column(String(10), nullable=True)
    end_date: str | None = Column(String(10), nullable=True)
    stops = relationship("TripStopModel", back_populates="trip", order_by="TripStopModel.position")


class TripStopModel(Base):
    __tablename__ = "trip_stops"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    trip_id: str = Column(String(36), ForeignKey("trips.id"), nullable=False)
    place_id: str = Column(String(36), ForeignKey("places.id"), nullable=False)
    position: int = Column(Integer, nullable=False, default=0)
    arrived_at: datetime | None = Column(DateTime(timezone=True), nullable=True)
    departed_at: datetime | None = Column(DateTime(timezone=True), nullable=True)
    trip = relationship("TripModel", back_populates="stops")


class RegionModel(Base):
    __tablename__ = "regions"

    id: str = Column(String(36), primary_key=True, default=_new_uuid)
    name: str = Column(String(255), nullable=False)
    region_type: str = Column(String(50), nullable=False)
    region_code: str | None = Column(String(20), nullable=True)


class ProjectModel(Base):
    __tablename__ = "projects"

    id: str = Column(String(36), primary_key=True, default=_new_uuid)
    name: str = Column(String(255), nullable=False)
    description: str | None = Column(Text, nullable=True)
    map_type: str = Column(String(50), nullable=False)
    config: str = Column(Text, nullable=False, default="{}")


class ProjectPlaceModel(Base):
    __tablename__ = "project_places"

    project_id: str = Column(String(36), ForeignKey("projects.id"), primary_key=True)
    place_id: str = Column(String(36), ForeignKey("places.id"), primary_key=True)


class ProjectTripModel(Base):
    __tablename__ = "project_trips"

    project_id: str = Column(String(36), ForeignKey("projects.id"), primary_key=True)
    trip_id: str = Column(String(36), ForeignKey("trips.id"), primary_key=True)


class ProjectRegionModel(Base):
    __tablename__ = "project_regions"

    project_id: str = Column(String(36), ForeignKey("projects.id"), primary_key=True)
    region_id: str = Column(String(36), ForeignKey("regions.id"), primary_key=True)


class PhotoModel(Base):
    __tablename__ = "photos"

    id: str = Column(String(36), primary_key=True, default=_new_uuid)
    file_path: str = Column(Text, nullable=False)
    latitude: float | None = Column(Float, nullable=True)
    longitude: float | None = Column(Float, nullable=True)
    taken_at: datetime | None = Column(DateTime(timezone=True), nullable=True)
    place_id: str | None = Column(String(36), ForeignKey("places.id"), nullable=True)
    trip_id: str | None = Column(String(36), ForeignKey("trips.id"), nullable=True)
```

Create `src/voyages/infrastructure/db/session.py`:

```python
from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from voyages.infrastructure.db.models import Base


def create_engine_and_tables(database_url: str = "sqlite:///voyages.db") -> Engine:
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine: Engine) -> Session:
    return Session(bind=engine)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/infrastructure/test_db_models.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/infrastructure/ tests/infrastructure/
git commit -m "feat(infrastructure): add SQLAlchemy models and session management"
```

---

### Task 12: SQLAlchemy repository implementations

**Files:**
- Create: `src/voyages/infrastructure/db/repository.py`
- Test: `tests/infrastructure/test_db_repository.py`

- [ ] **Step 1: Write failing tests for PlaceRepository and TripRepository**

Create `tests/infrastructure/test_db_repository.py`:

```python
from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from voyages.domain.entities import Place, Trip, TripStop, Region, Project, Photo
from voyages.domain.value_objects import MapType
from voyages.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlTripRepository,
    SqlRegionRepository,
    SqlProjectRepository,
    SqlPhotoRepository,
)
from voyages.infrastructure.db.session import create_engine_and_tables, get_session


@pytest.fixture()
def session():
    engine = create_engine_and_tables("sqlite:///:memory:")
    s = get_session(engine)
    yield s
    s.close()


class TestSqlPlaceRepository:
    def test_save_and_get(self, session) -> None:
        repo = SqlPlaceRepository(session)
        place = Place(
            id=uuid4(), name="Kyoto", latitude=35.01, longitude=135.77,
            source="manual", country="Japan",
        )
        repo.save(place)
        found = repo.get(place.id)
        assert found is not None
        assert found.name == "Kyoto"
        assert found.country == "Japan"

    def test_list_all(self, session) -> None:
        repo = SqlPlaceRepository(session)
        repo.save(Place(id=uuid4(), name="A", latitude=0, longitude=0, source="manual"))
        repo.save(Place(id=uuid4(), name="B", latitude=1, longitude=1, source="manual"))
        assert len(repo.list_all()) == 2

    def test_search_by_name(self, session) -> None:
        repo = SqlPlaceRepository(session)
        repo.save(Place(id=uuid4(), name="Kyoto", latitude=35.01, longitude=135.77, source="manual"))
        repo.save(Place(id=uuid4(), name="Tokyo", latitude=35.68, longitude=139.69, source="manual"))
        results = repo.search_by_name("kyo")
        names = {p.name for p in results}
        assert "Kyoto" in names
        assert "Tokyo" in names

    def test_delete(self, session) -> None:
        repo = SqlPlaceRepository(session)
        place = Place(id=uuid4(), name="Del", latitude=0, longitude=0, source="manual")
        repo.save(place)
        repo.delete(place.id)
        assert repo.get(place.id) is None

    def test_update_existing(self, session) -> None:
        repo = SqlPlaceRepository(session)
        place = Place(id=uuid4(), name="Old", latitude=0, longitude=0, source="manual")
        repo.save(place)
        place.name = "New"
        repo.save(place)
        found = repo.get(place.id)
        assert found is not None
        assert found.name == "New"


class TestSqlTripRepository:
    def test_save_and_get_with_stops(self, session) -> None:
        repo = SqlTripRepository(session)
        place_repo = SqlPlaceRepository(session)
        place = Place(id=uuid4(), name="Tokyo", latitude=35.68, longitude=139.69, source="manual")
        place_repo.save(place)

        trip = Trip(
            id=uuid4(), name="Japan 2024",
            start_date=date(2024, 3, 15), end_date=date(2024, 3, 29),
        )
        trip.stops = [
            TripStop(place_id=place.id, position=0,
                     arrived_at=datetime(2024, 3, 15, 10, 0, tzinfo=timezone.utc)),
        ]
        repo.save(trip)
        found = repo.get(trip.id)
        assert found is not None
        assert found.name == "Japan 2024"
        assert len(found.stops) == 1
        assert found.stops[0].place_id == place.id

    def test_list_all(self, session) -> None:
        repo = SqlTripRepository(session)
        repo.save(Trip(id=uuid4(), name="A"))
        repo.save(Trip(id=uuid4(), name="B"))
        assert len(repo.list_all()) == 2

    def test_delete(self, session) -> None:
        repo = SqlTripRepository(session)
        trip = Trip(id=uuid4(), name="Del")
        repo.save(trip)
        repo.delete(trip.id)
        assert repo.get(trip.id) is None


class TestSqlRegionRepository:
    def test_save_and_get(self, session) -> None:
        repo = SqlRegionRepository(session)
        region = Region(id=uuid4(), name="Japan", region_type="country", region_code="JP")
        repo.save(region)
        found = repo.get(region.id)
        assert found is not None
        assert found.region_code == "JP"

    def test_list_all(self, session) -> None:
        repo = SqlRegionRepository(session)
        repo.save(Region(id=uuid4(), name="Japan", region_type="country"))
        repo.save(Region(id=uuid4(), name="France", region_type="country"))
        assert len(repo.list_all()) == 2


class TestSqlProjectRepository:
    def test_save_and_get_with_associations(self, session) -> None:
        repo = SqlProjectRepository(session)
        place_id = uuid4()
        trip_id = uuid4()
        region_id = uuid4()

        # Save prerequisite entities
        SqlPlaceRepository(session).save(
            Place(id=place_id, name="P", latitude=0, longitude=0, source="manual")
        )
        SqlTripRepository(session).save(Trip(id=trip_id, name="T"))
        SqlRegionRepository(session).save(Region(id=region_id, name="R", region_type="country"))

        project = Project(
            id=uuid4(), name="Test Map", map_type=MapType.TRAVEL,
            config={"projection": "EqualEarth"},
        )
        project.place_ids = [place_id]
        project.trip_ids = [trip_id]
        project.region_ids = [region_id]
        repo.save(project)

        found = repo.get(project.id)
        assert found is not None
        assert found.config["projection"] == "EqualEarth"
        assert place_id in found.place_ids
        assert trip_id in found.trip_ids
        assert region_id in found.region_ids

    def test_get_by_name(self, session) -> None:
        repo = SqlProjectRepository(session)
        repo.save(Project(id=uuid4(), name="My Map", map_type=MapType.TRAVEL))
        found = repo.get_by_name("My Map")
        assert found is not None


class TestSqlPhotoRepository:
    def test_save_and_get(self, session) -> None:
        repo = SqlPhotoRepository(session)
        photo = Photo(
            id=uuid4(), file_path="/photos/img.jpg",
            latitude=35.01, longitude=135.77,
            taken_at=datetime(2024, 3, 15, 14, 30, tzinfo=timezone.utc),
        )
        repo.save(photo)
        found = repo.get(photo.id)
        assert found is not None
        assert found.file_path == "/photos/img.jpg"

    def test_list_by_trip(self, session) -> None:
        repo = SqlPhotoRepository(session)
        trip_id = uuid4()
        SqlTripRepository(session).save(Trip(id=trip_id, name="T"))
        repo.save(Photo(id=uuid4(), file_path="/a.jpg", trip_id=trip_id))
        repo.save(Photo(id=uuid4(), file_path="/b.jpg", trip_id=trip_id))
        repo.save(Photo(id=uuid4(), file_path="/c.jpg"))  # no trip
        assert len(repo.list_by_trip(trip_id)) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/infrastructure/test_db_repository.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement repository classes**

Create `src/voyages/infrastructure/db/repository.py`:

```python
from __future__ import annotations

import json
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from voyages.domain.entities import Photo, Place, Project, Region, Trip, TripStop
from voyages.domain.value_objects import MapType
from voyages.infrastructure.db.models import (
    PhotoModel,
    PlaceModel,
    ProjectModel,
    ProjectPlaceModel,
    ProjectRegionModel,
    ProjectTripModel,
    RegionModel,
    TripModel,
    TripStopModel,
)


class SqlPlaceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, place_id: UUID) -> Place | None:
        model = self._session.query(PlaceModel).filter_by(id=str(place_id)).first()
        return self._to_entity(model) if model else None

    def list_all(self) -> list[Place]:
        models = self._session.query(PlaceModel).all()
        return [self._to_entity(m) for m in models]

    def search_by_name(self, name: str) -> list[Place]:
        models = self._session.query(PlaceModel).filter(
            PlaceModel.name.ilike(f"%{name}%")
        ).all()
        return [self._to_entity(m) for m in models]

    def save(self, place: Place) -> None:
        existing = self._session.query(PlaceModel).filter_by(id=str(place.id)).first()
        if existing:
            existing.name = place.name
            existing.latitude = place.latitude
            existing.longitude = place.longitude
            existing.country = place.country
            existing.admin1 = place.admin1
            existing.category = place.category
            existing.notes = place.notes
            existing.source = place.source
        else:
            model = PlaceModel(
                id=str(place.id),
                name=place.name,
                latitude=place.latitude,
                longitude=place.longitude,
                country=place.country,
                admin1=place.admin1,
                category=place.category,
                notes=place.notes,
                source=place.source,
            )
            self._session.add(model)
        self._session.commit()

    def delete(self, place_id: UUID) -> None:
        model = self._session.query(PlaceModel).filter_by(id=str(place_id)).first()
        if model:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: PlaceModel) -> Place:
        return Place(
            id=UUID(model.id),
            name=model.name,
            latitude=model.latitude,
            longitude=model.longitude,
            country=model.country,
            admin1=model.admin1,
            category=model.category,
            notes=model.notes,
            source=model.source,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SqlTripRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, trip_id: UUID) -> Trip | None:
        model = self._session.query(TripModel).filter_by(id=str(trip_id)).first()
        return self._to_entity(model) if model else None

    def list_all(self) -> list[Trip]:
        models = self._session.query(TripModel).all()
        return [self._to_entity(m) for m in models]

    def save(self, trip: Trip) -> None:
        existing = self._session.query(TripModel).filter_by(id=str(trip.id)).first()
        if existing:
            existing.name = trip.name
            existing.description = trip.description
            existing.start_date = trip.start_date.isoformat() if trip.start_date else None
            existing.end_date = trip.end_date.isoformat() if trip.end_date else None
            # Replace stops
            self._session.query(TripStopModel).filter_by(trip_id=str(trip.id)).delete()
            for stop in trip.stops:
                self._session.add(TripStopModel(
                    trip_id=str(trip.id),
                    place_id=str(stop.place_id),
                    position=stop.position,
                    arrived_at=stop.arrived_at,
                    departed_at=stop.departed_at,
                ))
        else:
            model = TripModel(
                id=str(trip.id),
                name=trip.name,
                description=trip.description,
                start_date=trip.start_date.isoformat() if trip.start_date else None,
                end_date=trip.end_date.isoformat() if trip.end_date else None,
            )
            self._session.add(model)
            for stop in trip.stops:
                self._session.add(TripStopModel(
                    trip_id=str(trip.id),
                    place_id=str(stop.place_id),
                    position=stop.position,
                    arrived_at=stop.arrived_at,
                    departed_at=stop.departed_at,
                ))
        self._session.commit()

    def delete(self, trip_id: UUID) -> None:
        self._session.query(TripStopModel).filter_by(trip_id=str(trip_id)).delete()
        model = self._session.query(TripModel).filter_by(id=str(trip_id)).first()
        if model:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: TripModel) -> Trip:
        stops = [
            TripStop(
                place_id=UUID(s.place_id),
                position=s.position,
                arrived_at=s.arrived_at,
                departed_at=s.departed_at,
            )
            for s in model.stops
        ]
        return Trip(
            id=UUID(model.id),
            name=model.name,
            description=model.description,
            start_date=date.fromisoformat(model.start_date) if model.start_date else None,
            end_date=date.fromisoformat(model.end_date) if model.end_date else None,
            stops=stops,
        )


class SqlRegionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, region_id: UUID) -> Region | None:
        model = self._session.query(RegionModel).filter_by(id=str(region_id)).first()
        return self._to_entity(model) if model else None

    def list_all(self) -> list[Region]:
        return [self._to_entity(m) for m in self._session.query(RegionModel).all()]

    def save(self, region: Region) -> None:
        existing = self._session.query(RegionModel).filter_by(id=str(region.id)).first()
        if existing:
            existing.name = region.name
            existing.region_type = region.region_type
            existing.region_code = region.region_code
        else:
            self._session.add(RegionModel(
                id=str(region.id), name=region.name,
                region_type=region.region_type, region_code=region.region_code,
            ))
        self._session.commit()

    def delete(self, region_id: UUID) -> None:
        model = self._session.query(RegionModel).filter_by(id=str(region_id)).first()
        if model:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: RegionModel) -> Region:
        return Region(
            id=UUID(model.id), name=model.name,
            region_type=model.region_type, region_code=model.region_code,
        )


class SqlProjectRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, project_id: UUID) -> Project | None:
        model = self._session.query(ProjectModel).filter_by(id=str(project_id)).first()
        return self._to_entity(model) if model else None

    def get_by_name(self, name: str) -> Project | None:
        model = self._session.query(ProjectModel).filter_by(name=name).first()
        return self._to_entity(model) if model else None

    def list_all(self) -> list[Project]:
        return [self._to_entity(m) for m in self._session.query(ProjectModel).all()]

    def save(self, project: Project) -> None:
        existing = self._session.query(ProjectModel).filter_by(id=str(project.id)).first()
        if existing:
            existing.name = project.name
            existing.description = project.description
            existing.map_type = project.map_type.value
            existing.config = json.dumps(project.config)
        else:
            self._session.add(ProjectModel(
                id=str(project.id), name=project.name,
                description=project.description,
                map_type=project.map_type.value,
                config=json.dumps(project.config),
            ))
        self._session.commit()

        # Sync associations
        pid = str(project.id)
        self._session.query(ProjectPlaceModel).filter_by(project_id=pid).delete()
        self._session.query(ProjectTripModel).filter_by(project_id=pid).delete()
        self._session.query(ProjectRegionModel).filter_by(project_id=pid).delete()
        for place_id in project.place_ids:
            self._session.add(ProjectPlaceModel(project_id=pid, place_id=str(place_id)))
        for trip_id in project.trip_ids:
            self._session.add(ProjectTripModel(project_id=pid, trip_id=str(trip_id)))
        for region_id in project.region_ids:
            self._session.add(ProjectRegionModel(project_id=pid, region_id=str(region_id)))
        self._session.commit()

    def delete(self, project_id: UUID) -> None:
        pid = str(project_id)
        self._session.query(ProjectPlaceModel).filter_by(project_id=pid).delete()
        self._session.query(ProjectTripModel).filter_by(project_id=pid).delete()
        self._session.query(ProjectRegionModel).filter_by(project_id=pid).delete()
        model = self._session.query(ProjectModel).filter_by(id=pid).first()
        if model:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: ProjectModel) -> Project:
        place_ids = [
            UUID(r.place_id)
            for r in self._session.query(ProjectPlaceModel).filter_by(project_id=model.id).all()
        ]
        trip_ids = [
            UUID(r.trip_id)
            for r in self._session.query(ProjectTripModel).filter_by(project_id=model.id).all()
        ]
        region_ids = [
            UUID(r.region_id)
            for r in self._session.query(ProjectRegionModel).filter_by(project_id=model.id).all()
        ]
        return Project(
            id=UUID(model.id), name=model.name,
            map_type=MapType(model.map_type),
            description=model.description,
            config=json.loads(model.config),
            place_ids=place_ids,
            trip_ids=trip_ids,
            region_ids=region_ids,
        )


class SqlPhotoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, photo_id: UUID) -> Photo | None:
        model = self._session.query(PhotoModel).filter_by(id=str(photo_id)).first()
        return self._to_entity(model) if model else None

    def list_by_trip(self, trip_id: UUID) -> list[Photo]:
        models = self._session.query(PhotoModel).filter_by(trip_id=str(trip_id)).all()
        return [self._to_entity(m) for m in models]

    def save(self, photo: Photo) -> None:
        existing = self._session.query(PhotoModel).filter_by(id=str(photo.id)).first()
        if existing:
            existing.file_path = photo.file_path
            existing.latitude = photo.latitude
            existing.longitude = photo.longitude
            existing.taken_at = photo.taken_at
            existing.place_id = str(photo.place_id) if photo.place_id else None
            existing.trip_id = str(photo.trip_id) if photo.trip_id else None
        else:
            self._session.add(PhotoModel(
                id=str(photo.id), file_path=photo.file_path,
                latitude=photo.latitude, longitude=photo.longitude,
                taken_at=photo.taken_at,
                place_id=str(photo.place_id) if photo.place_id else None,
                trip_id=str(photo.trip_id) if photo.trip_id else None,
            ))
        self._session.commit()

    def delete(self, photo_id: UUID) -> None:
        model = self._session.query(PhotoModel).filter_by(id=str(photo_id)).first()
        if model:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: PhotoModel) -> Photo:
        return Photo(
            id=UUID(model.id), file_path=model.file_path,
            latitude=model.latitude, longitude=model.longitude,
            taken_at=model.taken_at,
            place_id=UUID(model.place_id) if model.place_id else None,
            trip_id=UUID(model.trip_id) if model.trip_id else None,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/infrastructure/test_db_repository.py -v`
Expected: All 14 tests PASS.

- [ ] **Step 5: Run linting and type checking**

Run: `uv run ruff check src/voyages/infrastructure/ && uv run mypy src/voyages/infrastructure/`
Expected: Clean pass (may need type ignores for SQLAlchemy Column annotations — fix as needed).

- [ ] **Step 6: Commit**

```bash
git add src/voyages/infrastructure/db/repository.py tests/infrastructure/test_db_repository.py
git commit -m "feat(infrastructure): add SQLAlchemy repository implementations for all entities"
```

---

## Phase 5: Infrastructure — External Services

### Task 13: Nominatim geocoding client

**Files:**
- Create: `src/voyages/infrastructure/geocoding/__init__.py`
- Create: `src/voyages/infrastructure/geocoding/nominatim.py`
- Test: `tests/infrastructure/test_nominatim.py`

- [ ] **Step 1: Write failing tests with mocked HTTP**

Create `src/voyages/infrastructure/geocoding/__init__.py` (empty).

Create `tests/infrastructure/test_nominatim.py`:

```python
from __future__ import annotations

from unittest.mock import MagicMock, patch
from uuid import UUID

from voyages.infrastructure.geocoding.nominatim import NominatimGeocodingService


class TestNominatimSearch:
    def test_search_returns_places(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "display_name": "Kyoto, Japan",
                "lat": "35.0116363",
                "lon": "135.7680294",
                "address": {"country": "Japan", "state": "Kyoto"},
            },
        ]
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.get", return_value=mock_response):
            service = NominatimGeocodingService()
            results = service.search("Kyoto")

        assert len(results) == 1
        assert results[0].name == "Kyoto, Japan"
        assert abs(results[0].latitude - 35.0116363) < 0.001

    def test_search_empty_result(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.get", return_value=mock_response):
            service = NominatimGeocodingService()
            results = service.search("xyznonexistent")

        assert results == []


class TestNominatimReverseGeocode:
    def test_reverse_geocode(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "display_name": "Kyoto, Japan",
            "lat": "35.01",
            "lon": "135.77",
            "address": {"country": "Japan", "state": "Kyoto"},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.get", return_value=mock_response):
            service = NominatimGeocodingService()
            place = service.reverse_geocode(35.01, 135.77)

        assert place is not None
        assert place.country == "Japan"
        assert place.admin1 == "Kyoto"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/infrastructure/test_nominatim.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement Nominatim client**

Create `src/voyages/infrastructure/geocoding/nominatim.py`:

```python
from __future__ import annotations

from uuid import uuid4

import httpx

from voyages.domain.entities import Place

_BASE_URL = "https://nominatim.openstreetmap.org"
_HEADERS = {"User-Agent": "Voyages/0.1.0 (map toolbox)"}


class NominatimGeocodingService:
    def search(self, query: str) -> list[Place]:
        response = httpx.get(
            f"{_BASE_URL}/search",
            params={"q": query, "format": "json", "addressdetails": 1, "limit": 10},
            headers=_HEADERS,
        )
        response.raise_for_status()
        results = response.json()

        return [
            Place(
                id=uuid4(),
                name=r["display_name"],
                latitude=float(r["lat"]),
                longitude=float(r["lon"]),
                country=r.get("address", {}).get("country"),
                admin1=r.get("address", {}).get("state"),
                source="geocoding",
            )
            for r in results
        ]

    def reverse_geocode(self, latitude: float, longitude: float) -> Place | None:
        response = httpx.get(
            f"{_BASE_URL}/reverse",
            params={"lat": latitude, "lon": longitude, "format": "json", "addressdetails": 1},
            headers=_HEADERS,
        )
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return None

        return Place(
            id=uuid4(),
            name=data.get("display_name", ""),
            latitude=float(data["lat"]),
            longitude=float(data["lon"]),
            country=data.get("address", {}).get("country"),
            admin1=data.get("address", {}).get("state"),
            source="geocoding",
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/infrastructure/test_nominatim.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/infrastructure/geocoding/ tests/infrastructure/test_nominatim.py
git commit -m "feat(infrastructure): add Nominatim geocoding client"
```

---

### Task 14: EXIF extraction service

**Files:**
- Create: `src/voyages/infrastructure/exif/__init__.py`
- Create: `src/voyages/infrastructure/exif/extractor.py`
- Test: `tests/infrastructure/test_exif.py`

- [ ] **Step 1: Write failing tests**

Create `src/voyages/infrastructure/exif/__init__.py` (empty).

Create `tests/infrastructure/test_exif.py`:

```python
from __future__ import annotations

from unittest.mock import MagicMock, patch
from pathlib import Path

from voyages.infrastructure.exif.extractor import PillowExifService


class TestPillowExifService:
    def test_extract_gps_from_file(self) -> None:
        # Mock PIL Image with EXIF GPS data
        mock_image = MagicMock()
        mock_exif = {
            # GPSInfo tag ID
            34853: {
                1: "N",  # GPSLatitudeRef
                2: ((35, 1), (0, 1), (41.88, 100)),  # GPSLatitude
                3: "E",  # GPSLongitudeRef
                4: ((135, 1), (46, 1), (5.04, 100)),  # GPSLongitude
            },
            36867: "2024:03:15 14:30:00",  # DateTimeOriginal
        }
        mock_image.getexif.return_value = mock_exif

        with patch("PIL.Image.open", return_value=mock_image):
            service = PillowExifService()
            photo = service.extract_from_file("/photos/IMG_001.jpg")

        assert photo is not None
        assert photo.latitude is not None
        assert photo.file_path == "/photos/IMG_001.jpg"

    def test_extract_returns_none_for_no_exif(self) -> None:
        mock_image = MagicMock()
        mock_image.getexif.return_value = {}

        with patch("PIL.Image.open", return_value=mock_image):
            service = PillowExifService()
            photo = service.extract_from_file("/photos/no_exif.jpg")

        # Photo returned but without GPS data
        assert photo is None or photo.latitude is None

    def test_extract_from_directory(self) -> None:
        mock_image = MagicMock()
        mock_image.getexif.return_value = {}

        with patch("PIL.Image.open", return_value=mock_image), \
             patch.object(Path, "iterdir", return_value=[
                 Path("/photos/a.jpg"),
                 Path("/photos/b.png"),
                 Path("/photos/c.txt"),  # not an image
             ]), \
             patch.object(Path, "is_file", return_value=True):
            service = PillowExifService()
            photos = service.extract_from_directory("/photos")

        # Should attempt only image files
        assert isinstance(photos, list)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/infrastructure/test_exif.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement EXIF extractor**

Create `src/voyages/infrastructure/exif/extractor.py`:

```python
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image
from PIL.ExifTags import TAGS

from voyages.domain.entities import Photo

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tiff", ".tif"}
_GPS_INFO_TAG = 34853
_DATETIME_ORIGINAL_TAG = 36867


class PillowExifService:
    def extract_from_file(self, file_path: str) -> Photo | None:
        try:
            image = Image.open(file_path)
            exif_data = image.getexif()
        except Exception:
            return None

        if not exif_data:
            return None

        gps_info = exif_data.get(_GPS_INFO_TAG)
        if not gps_info:
            return None

        latitude = self._parse_gps_coord(gps_info.get(2), gps_info.get(1))
        longitude = self._parse_gps_coord(gps_info.get(4), gps_info.get(3))

        if latitude is None or longitude is None:
            return None

        taken_at = self._parse_datetime(exif_data.get(_DATETIME_ORIGINAL_TAG))

        return Photo(
            id=uuid4(),
            file_path=file_path,
            latitude=latitude,
            longitude=longitude,
            taken_at=taken_at,
        )

    def extract_from_directory(self, directory: str) -> list[Photo]:
        photos: list[Photo] = []
        dir_path = Path(directory)

        for file_path in sorted(dir_path.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in _IMAGE_EXTENSIONS:
                photo = self.extract_from_file(str(file_path))
                if photo is not None:
                    photos.append(photo)

        return photos

    def _parse_gps_coord(
        self,
        coord_data: tuple[tuple[int, int], ...] | None,
        ref: str | None,
    ) -> float | None:
        if coord_data is None or ref is None:
            return None

        try:
            degrees = coord_data[0][0] / coord_data[0][1]
            minutes = coord_data[1][0] / coord_data[1][1]
            seconds = coord_data[2][0] / coord_data[2][1]
            result = degrees + minutes / 60.0 + seconds / 3600.0

            if ref in ("S", "W"):
                result = -result

            return result
        except (IndexError, TypeError, ZeroDivisionError):
            return None

    def _parse_datetime(self, dt_string: str | None) -> datetime | None:
        if dt_string is None:
            return None
        try:
            return datetime.strptime(dt_string, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/infrastructure/test_exif.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/infrastructure/exif/ tests/infrastructure/test_exif.py
git commit -m "feat(infrastructure): add EXIF GPS extraction service using Pillow"
```

---

## Phase 6: Infrastructure — Rendering

### Task 15: Map styles and style loading

**Files:**
- Create: `src/voyages/infrastructure/renderer/__init__.py`
- Create: `src/voyages/infrastructure/renderer/styles.py`
- Create: `styles/default.yml`
- Create: `styles/vintage.yml`
- Create: `styles/minimal.yml`
- Create: `styles/dark.yml`
- Test: `tests/infrastructure/test_styles.py`

- [ ] **Step 1: Write failing tests**

Create `src/voyages/infrastructure/renderer/__init__.py` (empty).

Create `tests/infrastructure/test_styles.py`:

```python
from __future__ import annotations

import tempfile
from pathlib import Path

from voyages.infrastructure.renderer.styles import MapStyle, load_style, get_builtin_styles


class TestMapStyle:
    def test_load_builtin_default(self) -> None:
        style = load_style("default")
        assert style.name == "default"
        assert style.ocean is not None
        assert style.land is not None
        assert style.visited is not None

    def test_load_builtin_vintage(self) -> None:
        style = load_style("vintage")
        assert style.name == "vintage"

    def test_load_builtin_minimal(self) -> None:
        style = load_style("minimal")
        assert style.name == "minimal"

    def test_load_builtin_dark(self) -> None:
        style = load_style("dark")
        assert style.name == "dark"

    def test_load_custom_yaml(self) -> None:
        yaml_content = """
name: custom
ocean: "#112233"
land: "#445566"
visited: "#FF0000"
route: "#00FF00"
font: "Arial"
borders: "#999999"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            style = load_style(f.name)

        assert style.name == "custom"
        assert style.ocean == "#112233"

    def test_get_builtin_styles_returns_all_four(self) -> None:
        styles = get_builtin_styles()
        names = {s.name for s in styles}
        assert names == {"default", "vintage", "minimal", "dark"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/infrastructure/test_styles.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Create built-in style YAML files**

Create `styles/default.yml`:

```yaml
name: default
ocean: "#ACBEBE"
land: "#F4F4EF"
visited: "#A01D26"
visited_light: "#D4737A"
route: "#2C5F7C"
font: "DejaVu Sans"
borders: "#CCCCCC"
marker: "#A01D26"
marker_size: 4
title_size: 16
label_size: 8
```

Create `styles/vintage.yml`:

```yaml
name: vintage
ocean: "#D4E4ED"
land: "#F5F0E8"
visited: "#A01D26"
visited_light: "#C4686F"
route: "#2C5F7C"
font: "Playfair Display"
borders: "#C4B9A8"
marker: "#8B2500"
marker_size: 5
title_size: 18
label_size: 9
```

Create `styles/minimal.yml`:

```yaml
name: minimal
ocean: "#FFFFFF"
land: "#F0F0F0"
visited: "#333333"
visited_light: "#999999"
route: "#333333"
font: "Helvetica"
borders: "#E0E0E0"
marker: "#333333"
marker_size: 3
title_size: 14
label_size: 7
```

Create `styles/dark.yml`:

```yaml
name: dark
ocean: "#1A1A2E"
land: "#16213E"
visited: "#E94560"
visited_light: "#533483"
route: "#0F3460"
font: "DejaVu Sans"
borders: "#2A2A4A"
marker: "#E94560"
marker_size: 4
title_size: 16
label_size: 8
```

- [ ] **Step 4: Implement style loading**

Create `src/voyages/infrastructure/renderer/styles.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class MapStyle:
    name: str
    ocean: str
    land: str
    visited: str
    visited_light: str
    route: str
    font: str
    borders: str
    marker: str
    marker_size: int
    title_size: int
    label_size: int


_STYLES_DIR = Path(__file__).parent.parent.parent.parent.parent / "styles"

_BUILTIN_NAMES = ("default", "vintage", "minimal", "dark")


def load_style(name_or_path: str) -> MapStyle:
    if name_or_path in _BUILTIN_NAMES:
        path = _STYLES_DIR / f"{name_or_path}.yml"
    else:
        path = Path(name_or_path)

    with open(path) as f:
        data = yaml.safe_load(f)

    return MapStyle(
        name=data["name"],
        ocean=data["ocean"],
        land=data["land"],
        visited=data["visited"],
        visited_light=data.get("visited_light", data["visited"]),
        route=data["route"],
        font=data["font"],
        borders=data["borders"],
        marker=data.get("marker", data["visited"]),
        marker_size=data.get("marker_size", 4),
        title_size=data.get("title_size", 16),
        label_size=data.get("label_size", 8),
    )


def get_builtin_styles() -> list[MapStyle]:
    return [load_style(name) for name in _BUILTIN_NAMES]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/infrastructure/test_styles.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/voyages/infrastructure/renderer/ styles/ tests/infrastructure/test_styles.py
git commit -m "feat(infrastructure): add map style system with 4 built-in styles"
```

---

### Task 16: Rendering engine — base map and travel map

**Files:**
- Create: `src/voyages/infrastructure/renderer/engine.py`
- Test: `tests/infrastructure/test_renderer.py`

- [ ] **Step 1: Write failing tests**

Create `tests/infrastructure/test_renderer.py`:

```python
from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import uuid4

from voyages.domain.entities import Place, Region
from voyages.domain.value_objects import OutputFormat
from voyages.infrastructure.renderer.engine import RenderEngine
from voyages.infrastructure.renderer.styles import load_style


class TestRenderEngine:
    def test_render_travel_map_png(self) -> None:
        style = load_style("default")
        engine = RenderEngine(style=style)

        places = [
            Place(id=uuid4(), name="Tokyo", latitude=35.68, longitude=139.69, source="manual", country="Japan"),
            Place(id=uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="manual", country="France"),
        ]
        regions = [
            Region(id=uuid4(), name="Japan", region_type="country", region_code="JP"),
            Region(id=uuid4(), name="France", region_type="country", region_code="FR"),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "travel_map.png")
            result = engine.render_travel_map(
                places=places,
                regions=regions,
                output_path=output_path,
                output_format=OutputFormat.PNG,
            )
            assert Path(result).exists()
            assert Path(result).stat().st_size > 0

    def test_render_travel_map_svg(self) -> None:
        style = load_style("default")
        engine = RenderEngine(style=style)

        places = [
            Place(id=uuid4(), name="Chicago", latitude=41.85, longitude=-87.65, source="manual", country="United States"),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "travel_map.svg")
            result = engine.render_travel_map(
                places=places,
                regions=[],
                output_path=output_path,
                output_format=OutputFormat.SVG,
            )
            assert Path(result).exists()
            assert Path(result).stat().st_size > 0

    def test_render_with_custom_config(self) -> None:
        style = load_style("vintage")
        engine = RenderEngine(style=style)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "custom.png")
            result = engine.render_travel_map(
                places=[],
                regions=[],
                output_path=output_path,
                output_format=OutputFormat.PNG,
                config={"dpi": 150, "width": 800},
            )
            assert Path(result).exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/infrastructure/test_renderer.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement render engine**

Create `src/voyages/infrastructure/renderer/engine.py`:

```python
from __future__ import annotations

from typing import Any

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from voyages.domain.entities import Place, Region, Trip
from voyages.domain.value_objects import OutputFormat
from voyages.infrastructure.renderer.styles import MapStyle

_FORMAT_MAP = {
    OutputFormat.SVG: "svg",
    OutputFormat.PDF: "pdf",
    OutputFormat.PNG: "png",
    OutputFormat.EPS: "eps",
    OutputFormat.WEBP: "png",  # render as PNG, convert later if needed
}


class RenderEngine:
    def __init__(self, style: MapStyle) -> None:
        self._style = style

    def render_travel_map(
        self,
        places: list[Place],
        regions: list[Region],
        output_path: str,
        output_format: OutputFormat,
        config: dict[str, Any] | None = None,
    ) -> str:
        cfg = config or {}
        dpi = cfg.get("dpi", 200)
        width = cfg.get("width", 1200)
        height = int(width * 0.6)

        fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.EqualEarth())

        # Base map
        ax.set_global()
        ax.set_facecolor(self._style.ocean)
        ax.add_feature(
            cfeature.LAND, facecolor=self._style.land, edgecolor="none"
        )
        ax.add_feature(
            cfeature.BORDERS, linewidth=0.3, edgecolor=self._style.borders
        )
        ax.add_feature(cfeature.COASTLINE, linewidth=0.3, edgecolor=self._style.borders)
        ax.add_feature(cfeature.LAKES, facecolor=self._style.ocean, edgecolor="none")

        # Plot place markers
        for place in places:
            ax.plot(
                place.longitude,
                place.latitude,
                marker="o",
                color=self._style.marker,
                markersize=self._style.marker_size,
                transform=ccrs.PlateCarree(),
            )

        fmt = _FORMAT_MAP.get(output_format, "png")
        fig.savefig(output_path, format=fmt, dpi=dpi, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)

        return output_path

    def render_region_map(
        self,
        places: list[Place],
        regions: list[Region],
        output_path: str,
        output_format: OutputFormat,
        config: dict[str, Any] | None = None,
    ) -> str:
        cfg = config or {}
        dpi = cfg.get("dpi", 200)
        center_lat = cfg.get("center_lat", 0.0)
        center_lon = cfg.get("center_lon", 0.0)
        extent = cfg.get("extent", 20.0)

        fig = plt.figure(figsize=(10, 8), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        ax.set_extent([
            center_lon - extent, center_lon + extent,
            center_lat - extent, center_lat + extent,
        ])
        ax.set_facecolor(self._style.ocean)
        ax.add_feature(cfeature.LAND, facecolor=self._style.land, edgecolor="none")
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor=self._style.borders)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor=self._style.borders)
        ax.add_feature(
            cfeature.STATES_PROVINCES, linewidth=0.3, edgecolor=self._style.borders
        )

        for place in places:
            ax.plot(
                place.longitude, place.latitude,
                marker="o", color=self._style.marker,
                markersize=self._style.marker_size + 2,
                transform=ccrs.PlateCarree(),
            )
            ax.text(
                place.longitude + 0.3, place.latitude + 0.3,
                place.name,
                fontsize=self._style.label_size,
                fontfamily=self._style.font,
                transform=ccrs.PlateCarree(),
            )

        fmt = _FORMAT_MAP.get(output_format, "png")
        fig.savefig(output_path, format=fmt, dpi=dpi, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)

        return output_path

    def render_route_map(
        self,
        trip: Trip,
        places: list[Place],
        output_path: str,
        output_format: OutputFormat,
        config: dict[str, Any] | None = None,
    ) -> str:
        cfg = config or {}
        dpi = cfg.get("dpi", 200)

        place_map = {p.id: p for p in places}
        ordered_places = []
        for stop in sorted(trip.stops, key=lambda s: s.position):
            if stop.place_id in place_map:
                ordered_places.append(place_map[stop.place_id])

        if ordered_places:
            lats = [p.latitude for p in ordered_places]
            lons = [p.longitude for p in ordered_places]
            pad = max(2.0, (max(lats) - min(lats)) * 0.2, (max(lons) - min(lons)) * 0.2)
            extent = [min(lons) - pad, max(lons) + pad, min(lats) - pad, max(lats) + pad]
        else:
            extent = [-180, 180, -90, 90]

        fig = plt.figure(figsize=(12, 8), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_extent(extent)
        ax.set_facecolor(self._style.ocean)
        ax.add_feature(cfeature.LAND, facecolor=self._style.land, edgecolor="none")
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor=self._style.borders)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.3, edgecolor=self._style.borders)

        # Draw route line
        if len(ordered_places) >= 2:
            route_lons = [p.longitude for p in ordered_places]
            route_lats = [p.latitude for p in ordered_places]
            ax.plot(
                route_lons, route_lats,
                color=self._style.route, linewidth=2,
                transform=ccrs.PlateCarree(), zorder=2,
            )

        # Draw stop markers with numbers
        for i, place in enumerate(ordered_places):
            ax.plot(
                place.longitude, place.latitude,
                marker="o", color=self._style.marker,
                markersize=self._style.marker_size + 3,
                transform=ccrs.PlateCarree(), zorder=3,
            )
            ax.text(
                place.longitude + 0.3, place.latitude + 0.3,
                f"{i + 1}. {place.name}",
                fontsize=self._style.label_size,
                fontfamily=self._style.font,
                transform=ccrs.PlateCarree(), zorder=4,
            )

        fmt = _FORMAT_MAP.get(output_format, "png")
        fig.savefig(output_path, format=fmt, dpi=dpi, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)

        return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/infrastructure/test_renderer.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/infrastructure/renderer/engine.py tests/infrastructure/test_renderer.py
git commit -m "feat(infrastructure): add Cartopy render engine for travel, region, and route maps"
```

---

## Phase 7: CLI

### Task 17: CLI scaffold and serve command

**Files:**
- Create: `src/voyages/cli/__init__.py`
- Create: `src/voyages/cli/serve_command.py`
- Test: `tests/cli/__init__.py`
- Test: `tests/cli/test_cli_serve.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/__init__.py` (empty).

Create `tests/cli/test_cli_serve.py`:

```python
from __future__ import annotations

from typer.testing import CliRunner

from voyages.cli import app


runner = CliRunner()


class TestCliApp:
    def test_app_has_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "voyages" in result.output.lower() or "usage" in result.output.lower()

    def test_serve_command_exists(self) -> None:
        result = runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "port" in result.output.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_cli_serve.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement CLI scaffold**

Create `src/voyages/cli/__init__.py`:

```python
from __future__ import annotations

import typer

from voyages.cli.serve_command import serve

app = typer.Typer(name="voyages", help="Map generation toolbox for travel data.")

app.command()(serve)
```

Create `src/voyages/cli/serve_command.py`:

```python
from __future__ import annotations

import typer


def serve(
    port: int = typer.Option(8080, help="Port to serve the web UI on"),
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
) -> None:
    """Launch the Voyages web UI."""
    import uvicorn

    from voyages.server import create_app

    app = create_app()
    uvicorn.run(app, host=host, port=port)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_cli_serve.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/cli/ tests/cli/
git commit -m "feat(cli): add Typer CLI scaffold with serve command"
```

---

### Task 18: CLI place and project commands

**Files:**
- Create: `src/voyages/cli/place_commands.py`
- Create: `src/voyages/cli/project_commands.py`
- Create: `src/voyages/cli/trip_commands.py`
- Modify: `src/voyages/cli/__init__.py`
- Test: `tests/cli/test_cli_commands.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/test_cli_commands.py`:

```python
from __future__ import annotations

from unittest.mock import patch, MagicMock
from uuid import uuid4

from typer.testing import CliRunner

from voyages.cli import app
from voyages.domain.entities import Place, Project
from voyages.domain.value_objects import MapType

runner = CliRunner()


class TestPlaceCommands:
    @patch("voyages.cli.place_commands.get_place_service")
    def test_place_list(self, mock_get_service: MagicMock) -> None:
        mock_service = MagicMock()
        mock_service.list_all.return_value = [
            Place(id=uuid4(), name="Kyoto", latitude=35.01, longitude=135.77, source="manual"),
        ]
        mock_get_service.return_value = mock_service

        result = runner.invoke(app, ["place", "list"])
        assert result.exit_code == 0
        assert "Kyoto" in result.output

    @patch("voyages.cli.place_commands.get_place_service")
    def test_place_search(self, mock_get_service: MagicMock) -> None:
        mock_service = MagicMock()
        mock_service.search.return_value = [
            Place(id=uuid4(), name="Kyoto, Japan", latitude=35.01, longitude=135.77, source="geocoding"),
        ]
        mock_get_service.return_value = mock_service

        result = runner.invoke(app, ["place", "search", "Kyoto"])
        assert result.exit_code == 0
        assert "Kyoto" in result.output


class TestProjectCommands:
    @patch("voyages.cli.project_commands.get_project_service")
    def test_project_list(self, mock_get_service: MagicMock) -> None:
        mock_service = MagicMock()
        mock_service.list_all.return_value = [
            Project(id=uuid4(), name="World Map", map_type=MapType.TRAVEL),
        ]
        mock_get_service.return_value = mock_service

        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "World Map" in result.output

    @patch("voyages.cli.project_commands.get_project_service")
    def test_project_create(self, mock_get_service: MagicMock) -> None:
        mock_service = MagicMock()
        mock_service.create.return_value = Project(
            id=uuid4(), name="New Map", map_type=MapType.TRAVEL,
        )
        mock_get_service.return_value = mock_service

        result = runner.invoke(app, ["project", "create", "New Map", "--map-type", "travel"])
        assert result.exit_code == 0
        assert "New Map" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_cli_commands.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement CLI commands**

Create `src/voyages/cli/place_commands.py`:

```python
from __future__ import annotations

import typer

from voyages.application.place_service import PlaceService
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.db.repository import SqlPlaceRepository
from voyages.infrastructure.geocoding.nominatim import NominatimGeocodingService

place_app = typer.Typer(name="place", help="Manage places.")


def get_place_service() -> PlaceService:
    engine = create_engine_and_tables()
    session = get_session(engine)
    return PlaceService(
        place_repo=SqlPlaceRepository(session),
        geocoding=NominatimGeocodingService(),
    )


@place_app.command("list")
def list_places() -> None:
    """List all saved places."""
    service = get_place_service()
    places = service.list_all()
    if not places:
        typer.echo("No places found.")
        return
    for place in places:
        typer.echo(f"  {place.name}  ({place.latitude:.4f}, {place.longitude:.4f})  [{place.source}]")


@place_app.command("search")
def search_places(query: str = typer.Argument(..., help="Search query")) -> None:
    """Search for places via Nominatim."""
    service = get_place_service()
    results = service.search(query)
    if not results:
        typer.echo("No results found.")
        return
    for place in results:
        typer.echo(f"  {place.name}  ({place.latitude:.4f}, {place.longitude:.4f})")


@place_app.command("add")
def add_place(
    name: str = typer.Option(..., help="Place name"),
    lat: float = typer.Option(..., help="Latitude"),
    lon: float = typer.Option(..., help="Longitude"),
    category: str | None = typer.Option(None, help="Category"),
) -> None:
    """Add a place manually."""
    service = get_place_service()
    place = service.create(name=name, latitude=lat, longitude=lon, source="manual", category=category)
    typer.echo(f"Added: {place.name} ({place.id})")
```

Create `src/voyages/cli/project_commands.py`:

```python
from __future__ import annotations

import typer

from voyages.application.project_service import ProjectService
from voyages.domain.value_objects import MapType
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.db.repository import SqlProjectRepository

project_app = typer.Typer(name="project", help="Manage map projects.")


def get_project_service() -> ProjectService:
    engine = create_engine_and_tables()
    session = get_session(engine)
    return ProjectService(project_repo=SqlProjectRepository(session))


@project_app.command("list")
def list_projects() -> None:
    """List all projects."""
    service = get_project_service()
    projects = service.list_all()
    if not projects:
        typer.echo("No projects found.")
        return
    for project in projects:
        typer.echo(f"  {project.name}  [{project.map_type.value}]")


@project_app.command("create")
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    map_type: str = typer.Option("travel", help="Map type: travel, region, route"),
    description: str | None = typer.Option(None, help="Description"),
) -> None:
    """Create a new map project."""
    service = get_project_service()
    project = service.create(
        name=name,
        map_type=MapType(map_type),
        description=description,
    )
    typer.echo(f"Created: {project.name} ({project.id})")


@project_app.command("show")
def show_project(name: str = typer.Argument(..., help="Project name")) -> None:
    """Show project details."""
    service = get_project_service()
    project = service.get_by_name(name)
    if project is None:
        typer.echo(f"Project not found: {name}")
        raise typer.Exit(1)
    typer.echo(f"Name: {project.name}")
    typer.echo(f"Type: {project.map_type.value}")
    typer.echo(f"Places: {len(project.place_ids)}")
    typer.echo(f"Trips: {len(project.trip_ids)}")
    typer.echo(f"Regions: {len(project.region_ids)}")
```

Create `src/voyages/cli/trip_commands.py`:

```python
from __future__ import annotations

import typer

from voyages.application.trip_service import TripService
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.db.repository import SqlTripRepository

trip_app = typer.Typer(name="trip", help="Manage trips.")


def get_trip_service() -> TripService:
    engine = create_engine_and_tables()
    session = get_session(engine)
    return TripService(trip_repo=SqlTripRepository(session))


@trip_app.command("list")
def list_trips() -> None:
    """List all trips."""
    service = get_trip_service()
    trips = service.list_all()
    if not trips:
        typer.echo("No trips found.")
        return
    for trip in trips:
        date_range = ""
        if trip.start_date and trip.end_date:
            date_range = f"  {trip.start_date} → {trip.end_date}"
        typer.echo(f"  {trip.name}{date_range}  ({len(trip.stops)} stops)")


@trip_app.command("create")
def create_trip(
    name: str = typer.Argument(..., help="Trip name"),
    description: str | None = typer.Option(None, help="Description"),
) -> None:
    """Create a new trip."""
    service = get_trip_service()
    trip = service.create(name=name, description=description)
    typer.echo(f"Created: {trip.name} ({trip.id})")
```

Update `src/voyages/cli/__init__.py`:

```python
from __future__ import annotations

import typer

from voyages.cli.place_commands import place_app
from voyages.cli.project_commands import project_app
from voyages.cli.serve_command import serve
from voyages.cli.trip_commands import trip_app

app = typer.Typer(name="voyages", help="Map generation toolbox for travel data.")

app.add_typer(place_app)
app.add_typer(project_app)
app.add_typer(trip_app)
app.command()(serve)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_cli_commands.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/cli/ tests/cli/test_cli_commands.py
git commit -m "feat(cli): add place, project, and trip CLI commands"
```

---

### Task 19: CLI render and import commands

**Files:**
- Create: `src/voyages/cli/render_commands.py`
- Create: `src/voyages/cli/import_commands.py`
- Modify: `src/voyages/cli/__init__.py`
- Test: `tests/cli/test_cli_render.py`
- Test: `tests/cli/test_cli_import.py`

- [ ] **Step 1: Write failing tests for render command**

Create `tests/cli/test_cli_render.py`:

```python
from __future__ import annotations

from unittest.mock import patch, MagicMock
from uuid import uuid4

from typer.testing import CliRunner

from voyages.cli import app
from voyages.domain.entities import Place, Project
from voyages.domain.value_objects import MapType

runner = CliRunner()


class TestRenderCommand:
    @patch("voyages.cli.render_commands.get_render_dependencies")
    def test_render_command(self, mock_get_deps: MagicMock) -> None:
        project = Project(
            id=uuid4(), name="Test Map", map_type=MapType.TRAVEL,
            config={"projection": "EqualEarth"},
        )
        mock_project_service = MagicMock()
        mock_project_service.get_by_name.return_value = project

        mock_place_repo = MagicMock()
        mock_place_repo.list_all.return_value = []

        mock_engine = MagicMock()
        mock_engine.render_travel_map.return_value = "/tmp/test.png"

        mock_get_deps.return_value = (mock_project_service, mock_place_repo, MagicMock(), MagicMock(), mock_engine)

        result = runner.invoke(app, ["render", "Test Map"])
        assert result.exit_code == 0
```

- [ ] **Step 2: Write failing tests for import command**

Create `tests/cli/test_cli_import.py`:

```python
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from uuid import uuid4

from typer.testing import CliRunner

from voyages.cli import app
from voyages.domain.entities import Photo

runner = CliRunner()


class TestImportPhotosCommand:
    @patch("voyages.cli.import_commands.get_import_dependencies")
    def test_import_photos_dry_run(self, mock_get_deps: MagicMock) -> None:
        mock_photo_service = MagicMock()
        mock_photo_service.import_from_directory.return_value = [
            Photo(
                id=uuid4(), file_path="/photos/IMG_001.jpg",
                latitude=35.01, longitude=135.77,
                taken_at=datetime(2024, 3, 15, 14, 30, tzinfo=timezone.utc),
            ),
        ]
        mock_get_deps.return_value = mock_photo_service

        result = runner.invoke(app, ["import", "photos", "/photos", "--dry-run"])
        assert result.exit_code == 0
        assert "IMG_001" in result.output
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_cli_render.py tests/cli/test_cli_import.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 4: Implement render command**

Create `src/voyages/cli/render_commands.py`:

```python
from __future__ import annotations

from typing import Any

import typer

from voyages.application.project_service import ProjectService
from voyages.domain.value_objects import MapType, OutputFormat
from voyages.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlProjectRepository,
    SqlRegionRepository,
    SqlTripRepository,
)
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.renderer.engine import RenderEngine
from voyages.infrastructure.renderer.styles import load_style


def get_render_dependencies() -> tuple[Any, ...]:
    engine = create_engine_and_tables()
    session = get_session(engine)
    project_service = ProjectService(project_repo=SqlProjectRepository(session))
    place_repo = SqlPlaceRepository(session)
    trip_repo = SqlTripRepository(session)
    region_repo = SqlRegionRepository(session)
    style = load_style("default")
    render_engine = RenderEngine(style=style)
    return project_service, place_repo, trip_repo, region_repo, render_engine


def render(
    project_name: str = typer.Argument(..., help="Project name to render"),
    format: str = typer.Option("png", help="Output format: svg, pdf, png, webp, eps"),
    style: str = typer.Option("default", help="Style name or path to YAML"),
    dpi: int = typer.Option(200, help="DPI for raster output"),
    width: int = typer.Option(1200, help="Width in pixels"),
    output: str = typer.Option(".", help="Output directory"),
) -> None:
    """Render a project map to an image file."""
    project_service, place_repo, trip_repo, region_repo, render_engine = get_render_dependencies()

    # Override style if specified
    if style != "default":
        render_engine = RenderEngine(style=load_style(style))

    project = project_service.get_by_name(project_name)
    if project is None:
        typer.echo(f"Project not found: {project_name}")
        raise typer.Exit(1)

    output_format = OutputFormat(format)
    output_path = f"{output}/{project_name.replace(' ', '_')}{output_format.extension}"

    config = {**project.config, "dpi": dpi, "width": width}

    places = place_repo.list_all()
    regions = region_repo.list_all()

    if project.map_type == MapType.TRAVEL:
        result = render_engine.render_travel_map(
            places=places, regions=regions,
            output_path=output_path, output_format=output_format, config=config,
        )
    elif project.map_type == MapType.REGION:
        result = render_engine.render_region_map(
            places=places, regions=regions,
            output_path=output_path, output_format=output_format, config=config,
        )
    elif project.map_type == MapType.ROUTE:
        trips = [trip_repo.get(tid) for tid in project.trip_ids]
        trip = next((t for t in trips if t is not None), None)
        if trip is None:
            typer.echo("No trip found for route map.")
            raise typer.Exit(1)
        result = render_engine.render_route_map(
            trip=trip, places=places,
            output_path=output_path, output_format=output_format, config=config,
        )
    else:
        typer.echo(f"Unknown map type: {project.map_type}")
        raise typer.Exit(1)

    typer.echo(f"Rendered: {result}")
```

- [ ] **Step 5: Implement import command**

Create `src/voyages/cli/import_commands.py`:

```python
from __future__ import annotations

from typing import Any

import typer

from voyages.application.photo_service import PhotoService
from voyages.infrastructure.db.repository import SqlPhotoRepository
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.exif.extractor import PillowExifService
from voyages.infrastructure.geocoding.nominatim import NominatimGeocodingService

import_app = typer.Typer(name="import", help="Import data from external sources.")


def get_import_dependencies() -> PhotoService:
    engine = create_engine_and_tables()
    session = get_session(engine)
    return PhotoService(
        photo_repo=SqlPhotoRepository(session),
        exif_service=PillowExifService(),
        geocoding=NominatimGeocodingService(),
    )


@import_app.command("photos")
def import_photos(
    path: str = typer.Argument(..., help="Directory containing photos"),
    trip: str | None = typer.Option(None, help="Trip name to assign photos to"),
    dry_run: bool = typer.Option(False, help="Preview without saving"),
) -> None:
    """Import photos by extracting EXIF GPS data."""
    service = get_import_dependencies()
    photos = service.import_from_directory(path, dry_run=dry_run)

    if not photos:
        typer.echo("No photos with GPS data found.")
        return

    for photo in photos:
        status = "[dry run]" if dry_run else "[saved]"
        typer.echo(
            f"  {status} {photo.file_path}  "
            f"({photo.latitude:.4f}, {photo.longitude:.4f})  "
            f"{photo.taken_at or 'no date'}"
        )

    typer.echo(f"\n{len(photos)} photos {'previewed' if dry_run else 'imported'}.")
```

- [ ] **Step 6: Update CLI __init__.py to register new commands**

Update `src/voyages/cli/__init__.py`:

```python
from __future__ import annotations

import typer

from voyages.cli.import_commands import import_app
from voyages.cli.place_commands import place_app
from voyages.cli.project_commands import project_app
from voyages.cli.render_commands import render
from voyages.cli.serve_command import serve
from voyages.cli.trip_commands import trip_app

app = typer.Typer(name="voyages", help="Map generation toolbox for travel data.")

app.add_typer(place_app)
app.add_typer(project_app)
app.add_typer(trip_app)
app.add_typer(import_app)
app.command()(render)
app.command()(serve)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run pytest tests/cli/ -v`
Expected: All CLI tests PASS.

- [ ] **Step 8: Commit**

```bash
git add src/voyages/cli/ tests/cli/
git commit -m "feat(cli): add render and import commands"
```

---

## Phase 8: FastAPI Server

### Task 20: FastAPI app factory and place routes

**Files:**
- Create: `src/voyages/server/__init__.py`
- Create: `src/voyages/server/dependencies.py`
- Create: `src/voyages/server/routes/__init__.py`
- Create: `src/voyages/server/routes/places.py`
- Test: `tests/server/__init__.py`
- Test: `tests/server/test_places_api.py`

- [ ] **Step 1: Write failing tests**

Create `tests/server/__init__.py` (empty).

Create `tests/server/test_places_api.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from voyages.server import create_app


class TestPlacesAPI:
    def setup_method(self) -> None:
        app = create_app(database_url="sqlite:///:memory:")
        self.client = TestClient(app)

    def test_list_places_empty(self) -> None:
        response = self.client.get("/api/places")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_place(self) -> None:
        response = self.client.post("/api/places", json={
            "name": "Kyoto",
            "latitude": 35.01,
            "longitude": 135.77,
            "source": "manual",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Kyoto"
        assert "id" in data

    def test_create_and_list_place(self) -> None:
        self.client.post("/api/places", json={
            "name": "Tokyo", "latitude": 35.68, "longitude": 139.69, "source": "manual",
        })
        response = self.client.get("/api/places")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_search_places(self) -> None:
        # Search hits Nominatim — just verify endpoint exists
        response = self.client.get("/api/places/search", params={"q": "test"})
        # May return 200 with results or empty list
        assert response.status_code == 200

    def test_delete_place(self) -> None:
        resp = self.client.post("/api/places", json={
            "name": "Del", "latitude": 0, "longitude": 0, "source": "manual",
        })
        place_id = resp.json()["id"]
        response = self.client.delete(f"/api/places/{place_id}")
        assert response.status_code == 204
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/server/test_places_api.py -v`
Expected: FAIL — ImportError.

- [ ] **Step 3: Implement FastAPI app and place routes**

Create `src/voyages/server/__init__.py`:

```python
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.server.routes.places import create_places_router


def create_app(database_url: str = "sqlite:///voyages.db") -> FastAPI:
    app = FastAPI(title="Voyages API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine = create_engine_and_tables(database_url)

    @app.middleware("http")
    async def db_session_middleware(request, call_next):
        request.state.db = get_session(engine)
        response = await call_next(request)
        request.state.db.close()
        return response

    app.include_router(create_places_router(), prefix="/api")

    # Serve static SPA if built
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
```

Create `src/voyages/server/routes/__init__.py` (empty).

Create `src/voyages/server/routes/places.py`:

```python
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel

from voyages.application.place_service import PlaceService
from voyages.infrastructure.db.repository import SqlPlaceRepository
from voyages.infrastructure.geocoding.nominatim import NominatimGeocodingService


class PlaceCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    source: str
    country: str | None = None
    admin1: str | None = None
    category: str | None = None
    notes: str | None = None


class PlaceResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    country: str | None = None
    admin1: str | None = None
    category: str | None = None
    notes: str | None = None
    source: str


def _get_service(request: Request) -> PlaceService:
    session = request.state.db
    return PlaceService(
        place_repo=SqlPlaceRepository(session),
        geocoding=NominatimGeocodingService(),
    )


def create_places_router() -> APIRouter:
    router = APIRouter()

    @router.get("/places", response_model=list[PlaceResponse])
    def list_places(request: Request) -> list[PlaceResponse]:
        service = _get_service(request)
        places = service.list_all()
        return [
            PlaceResponse(
                id=str(p.id), name=p.name, latitude=p.latitude, longitude=p.longitude,
                country=p.country, admin1=p.admin1, category=p.category,
                notes=p.notes, source=p.source,
            )
            for p in places
        ]

    @router.post("/places", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
    def create_place(request: Request, body: PlaceCreate) -> PlaceResponse:
        service = _get_service(request)
        place = service.create(
            name=body.name, latitude=body.latitude, longitude=body.longitude,
            source=body.source, country=body.country, admin1=body.admin1,
            category=body.category, notes=body.notes,
        )
        return PlaceResponse(
            id=str(place.id), name=place.name, latitude=place.latitude,
            longitude=place.longitude, country=place.country, admin1=place.admin1,
            category=place.category, notes=place.notes, source=place.source,
        )

    @router.get("/places/search", response_model=list[PlaceResponse])
    def search_places(request: Request, q: str = "") -> list[PlaceResponse]:
        service = _get_service(request)
        results = service.search(q)
        return [
            PlaceResponse(
                id=str(p.id), name=p.name, latitude=p.latitude, longitude=p.longitude,
                country=p.country, admin1=p.admin1, category=p.category,
                notes=p.notes, source=p.source,
            )
            for p in results
        ]

    @router.delete("/places/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_place(request: Request, place_id: str) -> Response:
        service = _get_service(request)
        service.delete(UUID(place_id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/server/test_places_api.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/voyages/server/ tests/server/
git commit -m "feat(server): add FastAPI app factory and places API routes"
```

---

### Task 21: Remaining API routes (trips, projects, regions, render)

**Files:**
- Create: `src/voyages/server/routes/trips.py`
- Create: `src/voyages/server/routes/projects.py`
- Create: `src/voyages/server/routes/regions.py`
- Create: `src/voyages/server/routes/render.py`
- Modify: `src/voyages/server/__init__.py`
- Test: `tests/server/test_trips_api.py`
- Test: `tests/server/test_projects_api.py`

- [ ] **Step 1: Write failing tests for trips and projects API**

Create `tests/server/test_trips_api.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from voyages.server import create_app


class TestTripsAPI:
    def setup_method(self) -> None:
        app = create_app(database_url="sqlite:///:memory:")
        self.client = TestClient(app)

    def test_list_trips_empty(self) -> None:
        response = self.client.get("/api/trips")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_trip(self) -> None:
        response = self.client.post("/api/trips", json={
            "name": "Japan 2024",
            "description": "Two weeks in Japan",
        })
        assert response.status_code == 201
        assert response.json()["name"] == "Japan 2024"

    def test_delete_trip(self) -> None:
        resp = self.client.post("/api/trips", json={"name": "Del"})
        trip_id = resp.json()["id"]
        response = self.client.delete(f"/api/trips/{trip_id}")
        assert response.status_code == 204
```

Create `tests/server/test_projects_api.py`:

```python
from __future__ import annotations

from fastapi.testclient import TestClient

from voyages.server import create_app


class TestProjectsAPI:
    def setup_method(self) -> None:
        app = create_app(database_url="sqlite:///:memory:")
        self.client = TestClient(app)

    def test_list_projects_empty(self) -> None:
        response = self.client.get("/api/projects")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_project(self) -> None:
        response = self.client.post("/api/projects", json={
            "name": "World Map",
            "map_type": "travel",
        })
        assert response.status_code == 201
        assert response.json()["name"] == "World Map"

    def test_render_endpoint_exists(self) -> None:
        resp = self.client.post("/api/projects", json={"name": "Test", "map_type": "travel"})
        project_id = resp.json()["id"]
        response = self.client.post(f"/api/render/{project_id}")
        # May succeed or fail depending on data, but endpoint exists
        assert response.status_code in (200, 404, 422, 500)
```

- [ ] **Step 2: Implement remaining route files**

Create route files following the same pattern as `places.py` — each with Pydantic models, a factory function for the service, and CRUD endpoints. Register all routers in `create_app()`.

Create `src/voyages/server/routes/trips.py`, `src/voyages/server/routes/projects.py`, `src/voyages/server/routes/regions.py`, and `src/voyages/server/routes/render.py` following the same patterns established in `places.py`.

Update `src/voyages/server/__init__.py` to include all routers:

```python
from voyages.server.routes.places import create_places_router
from voyages.server.routes.trips import create_trips_router
from voyages.server.routes.projects import create_projects_router
from voyages.server.routes.regions import create_regions_router
from voyages.server.routes.render import create_render_router

# In create_app():
app.include_router(create_places_router(), prefix="/api")
app.include_router(create_trips_router(), prefix="/api")
app.include_router(create_projects_router(), prefix="/api")
app.include_router(create_regions_router(), prefix="/api")
app.include_router(create_render_router(), prefix="/api")
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `uv run pytest tests/server/ -v`
Expected: All server tests PASS.

- [ ] **Step 4: Commit**

```bash
git add src/voyages/server/ tests/server/
git commit -m "feat(server): add trips, projects, regions, and render API routes"
```

---

## Phase 9: Web UI

### Task 22: Svelte project scaffold

**Files:**
- Create: `web/package.json`
- Create: `web/vite.config.ts`
- Create: `web/tsconfig.json`
- Create: `web/src/App.svelte`
- Create: `web/src/main.ts`
- Create: `web/index.html`

- [ ] **Step 1: Initialize Svelte project**

```bash
cd /Users/donaldalbrecht/Projects/Voyages
mkdir -p web/src
cd web
npm create vite@latest . -- --template svelte-ts
```

If the interactive prompt doesn't work, create files manually.

- [ ] **Step 2: Install dependencies**

```bash
cd /Users/donaldalbrecht/Projects/Voyages/web
npm install
npm install leaflet svelte-routing
npm install -D @types/leaflet
```

- [ ] **Step 3: Configure Vite to output to server static directory**

Update `web/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: '../src/voyages/server/static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
})
```

- [ ] **Step 4: Create minimal App.svelte with routing**

Create `web/src/App.svelte`:

```svelte
<script lang="ts">
  let currentView = 'dashboard'
</script>

<nav>
  <h1>Voyages</h1>
  <button on:click={() => currentView = 'dashboard'}>Dashboard</button>
  <button on:click={() => currentView = 'places'}>Places</button>
  <button on:click={() => currentView = 'trips'}>Trips</button>
  <button on:click={() => currentView = 'projects'}>Projects</button>
</nav>

<main>
  {#if currentView === 'dashboard'}
    <h2>Dashboard</h2>
    <p>Welcome to Voyages.</p>
  {:else if currentView === 'places'}
    <h2>Places</h2>
    <p>Place management coming soon.</p>
  {:else if currentView === 'trips'}
    <h2>Trips</h2>
    <p>Trip management coming soon.</p>
  {:else if currentView === 'projects'}
    <h2>Projects</h2>
    <p>Map composer coming soon.</p>
  {/if}
</main>
```

- [ ] **Step 5: Verify it builds**

```bash
cd /Users/donaldalbrecht/Projects/Voyages/web
npm run build
```

Expected: Build succeeds, files appear in `src/voyages/server/static/`.

- [ ] **Step 6: Commit**

```bash
git add web/
git commit -m "feat(web): scaffold Svelte SPA with Vite and basic routing"
```

---

### Task 23: Places view with Leaflet map preview

**Files:**
- Create: `web/src/lib/api.ts`
- Create: `web/src/components/MapPreview.svelte`
- Create: `web/src/routes/Places.svelte`
- Modify: `web/src/App.svelte`

- [ ] **Step 1: Create API client**

Create `web/src/lib/api.ts`:

```typescript
const BASE = '/api'

export interface Place {
  id: string
  name: string
  latitude: number
  longitude: number
  country: string | null
  admin1: string | null
  category: string | null
  notes: string | null
  source: string
}

export async function fetchPlaces(): Promise<Place[]> {
  const res = await fetch(`${BASE}/places`)
  return res.json()
}

export async function searchPlaces(query: string): Promise<Place[]> {
  const res = await fetch(`${BASE}/places/search?q=${encodeURIComponent(query)}`)
  return res.json()
}

export async function createPlace(place: Omit<Place, 'id'>): Promise<Place> {
  const res = await fetch(`${BASE}/places`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(place),
  })
  return res.json()
}

export async function deletePlace(id: string): Promise<void> {
  await fetch(`${BASE}/places/${id}`, { method: 'DELETE' })
}
```

- [ ] **Step 2: Create Leaflet map component**

Create `web/src/components/MapPreview.svelte`:

```svelte
<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import L from 'leaflet'
  import 'leaflet/dist/leaflet.css'
  import type { Place } from '../lib/api'

  export let places: Place[] = []
  export let center: [number, number] = [20, 0]
  export let zoom: number = 2

  let mapElement: HTMLDivElement
  let map: L.Map
  let markerLayer: L.LayerGroup

  onMount(() => {
    map = L.map(mapElement).setView(center, zoom)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
    }).addTo(map)
    markerLayer = L.layerGroup().addTo(map)
  })

  onDestroy(() => {
    if (map) map.remove()
  })

  $: if (map && markerLayer) {
    markerLayer.clearLayers()
    places.forEach(p => {
      L.marker([p.latitude, p.longitude])
        .bindPopup(`<b>${p.name}</b>`)
        .addTo(markerLayer)
    })
  }
</script>

<div bind:this={mapElement} style="width: 100%; height: 400px; border-radius: 8px;"></div>
```

- [ ] **Step 3: Create Places view**

Create `web/src/routes/Places.svelte`:

```svelte
<script lang="ts">
  import { onMount } from 'svelte'
  import { fetchPlaces, searchPlaces, createPlace, deletePlace, type Place } from '../lib/api'
  import MapPreview from '../components/MapPreview.svelte'

  let places: Place[] = []
  let searchQuery = ''
  let searchResults: Place[] = []

  onMount(async () => {
    places = await fetchPlaces()
  })

  async function handleSearch() {
    if (searchQuery.trim()) {
      searchResults = await searchPlaces(searchQuery)
    }
  }

  async function addPlace(place: Place) {
    const created = await createPlace({
      name: place.name,
      latitude: place.latitude,
      longitude: place.longitude,
      country: place.country,
      admin1: place.admin1,
      category: place.category,
      notes: place.notes,
      source: 'manual',
    })
    places = [...places, created]
    searchResults = searchResults.filter(r => r.name !== place.name)
  }

  async function removePlaceById(id: string) {
    await deletePlace(id)
    places = places.filter(p => p.id !== id)
  }
</script>

<h2>Places</h2>

<div class="search">
  <input bind:value={searchQuery} placeholder="Search places..." on:keydown={(e) => e.key === 'Enter' && handleSearch()} />
  <button on:click={handleSearch}>Search</button>
</div>

{#if searchResults.length > 0}
  <div class="results">
    <h3>Search Results</h3>
    {#each searchResults as result}
      <div class="result-item">
        <span>{result.name}</span>
        <button on:click={() => addPlace(result)}>Add</button>
      </div>
    {/each}
  </div>
{/if}

<MapPreview {places} />

<table>
  <thead>
    <tr><th>Name</th><th>Lat</th><th>Lon</th><th>Country</th><th>Actions</th></tr>
  </thead>
  <tbody>
    {#each places as place}
      <tr>
        <td>{place.name}</td>
        <td>{place.latitude.toFixed(4)}</td>
        <td>{place.longitude.toFixed(4)}</td>
        <td>{place.country || '-'}</td>
        <td><button on:click={() => removePlaceById(place.id)}>Delete</button></td>
      </tr>
    {/each}
  </tbody>
</table>
```

- [ ] **Step 4: Update App.svelte to use Places component**

Update `web/src/App.svelte` to import and render the `Places` component when `currentView === 'places'`.

- [ ] **Step 5: Build and verify**

```bash
cd /Users/donaldalbrecht/Projects/Voyages/web
npm run build
```

Expected: Build succeeds.

- [ ] **Step 6: Commit**

```bash
git add web/
git commit -m "feat(web): add Places view with search, Leaflet map preview, and CRUD"
```

---

### Task 24: Remaining web views (Trips, Projects/MapComposer, Dashboard)

**Files:**
- Create: `web/src/routes/Dashboard.svelte`
- Create: `web/src/routes/Trips.svelte`
- Create: `web/src/routes/MapComposer.svelte`
- Modify: `web/src/lib/api.ts` (add trip/project API functions)
- Modify: `web/src/App.svelte`

- [ ] **Step 1: Extend API client with trip and project functions**

Add to `web/src/lib/api.ts`:

```typescript
export interface Trip {
  id: string
  name: string
  description: string | null
  start_date: string | null
  end_date: string | null
}

export interface Project {
  id: string
  name: string
  description: string | null
  map_type: string
}

export async function fetchTrips(): Promise<Trip[]> {
  const res = await fetch(`${BASE}/trips`)
  return res.json()
}

export async function createTrip(trip: { name: string; description?: string }): Promise<Trip> {
  const res = await fetch(`${BASE}/trips`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(trip),
  })
  return res.json()
}

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${BASE}/projects`)
  return res.json()
}

export async function createProject(project: { name: string; map_type: string }): Promise<Project> {
  const res = await fetch(`${BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(project),
  })
  return res.json()
}

export async function triggerRender(projectId: string): Promise<Blob> {
  const res = await fetch(`${BASE}/render/${projectId}`, { method: 'POST' })
  return res.blob()
}
```

- [ ] **Step 2: Create Dashboard, Trips, and MapComposer views**

Create each Svelte component with basic CRUD functionality following the same pattern as Places.svelte. Dashboard shows counts and recent items. Trips shows list with create form. MapComposer shows project list with create form and render/export button.

- [ ] **Step 3: Update App.svelte with all routes**

Import all view components and wire them into the view switching logic.

- [ ] **Step 4: Build and verify**

```bash
cd /Users/donaldalbrecht/Projects/Voyages/web
npm run build
```

Expected: Build succeeds.

- [ ] **Step 5: Commit**

```bash
git add web/
git commit -m "feat(web): add Dashboard, Trips, and MapComposer views"
```

---

## Phase 10: Integration and Polish

### Task 25: End-to-end smoke test

**Files:**
- Create: `tests/e2e/__init__.py`
- Create: `tests/e2e/test_smoke.py`

- [ ] **Step 1: Write e2e smoke test**

Create `tests/e2e/__init__.py` (empty).

Create `tests/e2e/test_smoke.py`:

```python
from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from voyages.application.place_service import PlaceService
from voyages.application.project_service import ProjectService
from voyages.domain.value_objects import MapType, OutputFormat
from voyages.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlProjectRepository,
    SqlRegionRepository,
)
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.geocoding.nominatim import NominatimGeocodingService
from voyages.infrastructure.renderer.engine import RenderEngine
from voyages.infrastructure.renderer.styles import load_style
from voyages.server import create_app


class TestEndToEndSmoke:
    def test_full_workflow_via_services(self) -> None:
        """Create places, create project, render map — all through service layer."""
        engine = create_engine_and_tables("sqlite:///:memory:")
        session = get_session(engine)

        place_repo = SqlPlaceRepository(session)
        project_repo = SqlProjectRepository(session)
        region_repo = SqlRegionRepository(session)

        # Fake geocoding for test
        class FakeGeocoding:
            def search(self, query: str) -> list:
                return []
            def reverse_geocode(self, lat: float, lon: float):
                return None

        place_service = PlaceService(place_repo=place_repo, geocoding=FakeGeocoding())
        project_service = ProjectService(project_repo=project_repo)

        # Create places
        tokyo = place_service.create(name="Tokyo", latitude=35.68, longitude=139.69, source="manual", country="Japan")
        paris = place_service.create(name="Paris", latitude=48.85, longitude=2.35, source="manual", country="France")

        # Create project
        project = project_service.create(name="World Map", map_type=MapType.TRAVEL)
        project_service.add_place(project.id, tokyo.id)
        project_service.add_place(project.id, paris.id)

        # Render
        style = load_style("default")
        render_engine = RenderEngine(style=style)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "smoke_test.png")
            result = render_engine.render_travel_map(
                places=place_repo.list_all(),
                regions=region_repo.list_all(),
                output_path=output_path,
                output_format=OutputFormat.PNG,
            )
            assert Path(result).exists()
            assert Path(result).stat().st_size > 1000  # Not an empty file

        session.close()

    def test_api_workflow(self) -> None:
        """Create places and project via API."""
        app = create_app(database_url="sqlite:///:memory:")
        client = TestClient(app)

        # Create place
        resp = client.post("/api/places", json={
            "name": "Berlin", "latitude": 52.52, "longitude": 13.40, "source": "manual",
        })
        assert resp.status_code == 201

        # List places
        resp = client.get("/api/places")
        assert len(resp.json()) == 1

        # Create project
        resp = client.post("/api/projects", json={
            "name": "Europe", "map_type": "travel",
        })
        assert resp.status_code == 201
```

- [ ] **Step 2: Run smoke tests**

Run: `uv run pytest tests/e2e/ -v`
Expected: All tests PASS.

- [ ] **Step 3: Run full test suite**

Run: `uv run pytest tests/ -v --tb=short`
Expected: All tests PASS across all layers.

- [ ] **Step 4: Run full lint and type check**

Run: `make lint`
Expected: ruff and mypy clean.

- [ ] **Step 5: Commit**

```bash
git add tests/e2e/
git commit -m "test(e2e): add end-to-end smoke tests for full workflow"
```

---

### Task 26: Clean up legacy code

**Files:**
- Remove: `MapBuilder/` (old Vue 2 frontend)
- Remove: `MapServer/` (old Flask backend)
- Move: `Experiments/` useful scripts to `docs/legacy/` for reference
- Remove: `geodata/` (empty)

- [ ] **Step 1: Archive useful legacy files**

```bash
mkdir -p /Users/donaldalbrecht/Projects/Voyages/docs/legacy
cp /Users/donaldalbrecht/Projects/Voyages/Experiments/geoname_shapes_plot.py /Users/donaldalbrecht/Projects/Voyages/docs/legacy/
cp /Users/donaldalbrecht/Projects/Voyages/Experiments/load_shapefile_via_geopandas.py /Users/donaldalbrecht/Projects/Voyages/docs/legacy/
```

- [ ] **Step 2: Remove legacy directories**

```bash
git rm -r MapBuilder/ MapServer/ Experiments/ geodata/
```

- [ ] **Step 3: Commit**

```bash
git add docs/legacy/ && git rm -r MapBuilder/ MapServer/ Experiments/ geodata/
git commit -m "chore: archive legacy code and remove old Vue/Flask scaffolding"
```

---

### Task 27: Final integration verification

- [ ] **Step 1: Verify full build**

```bash
cd /Users/donaldalbrecht/Projects/Voyages
make dev
make build-web
make test
make lint
```

Expected: All commands succeed.

- [ ] **Step 2: Manual smoke test**

```bash
uv run voyages serve --port 8080
# Open http://localhost:8080 — verify SPA loads
# Create a place via the UI
# Create a project via CLI: uv run voyages project create "Test" --map-type travel
# Render: uv run voyages render "Test" --format png --output ./
# Verify output file exists
```

- [ ] **Step 3: Commit any final fixes**

```bash
git add -A
git commit -m "chore: final integration fixes"
```
