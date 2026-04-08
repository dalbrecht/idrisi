# Coverage 95% Design Spec

**Date:** 2026-04-07
**Status:** Draft
**Issue:** dalbrecht/Voyages#9

## Overview

Increase overall test coverage from 89% to 95% and bump the CI enforcement threshold. Every new test is justified by a specific uncovered line. Mix of E2E subprocess tests (CLI wiring), real integration tests (renderer, DB, EXIF), and API tests (routes).

## Coverage Gaps and Test Strategy

### CLI Command Wiring — E2E Subprocess Tests

These files have uncovered `get_*_service()` factory functions that create real database connections and service instances. Testing via E2E subprocess exercises the full wiring path.

| File | Current | Missing | Strategy |
|------|---------|---------|----------|
| `cli/serve_command.py` | 43% | Lines 13-18: `uvicorn.run()` call | E2E: start server, HTTP request, terminate |
| `cli/render_commands.py` | 69% | Lines 28-37: `get_render_dependencies()` wiring; 53-54: style loading; 84-85, 90-91: region/route render branches | E2E: create project, render with each map type |
| `cli/place_commands.py` | 86% | Lines 19-23: `get_place_service()` wiring | E2E: already covered by `test_place_add_and_list` |
| `cli/trip_commands.py` | 85% | Lines 18-21: `get_trip_service()` wiring | E2E: trip create + trip list |
| `cli/project_commands.py` | 90% | Lines 19-22: `get_project_service()` wiring | E2E: project create + project list + project show |

### Infrastructure — Real Integration Tests

| File | Current | Missing | Strategy |
|------|---------|---------|----------|
| `renderer/engine.py` | 79% | Lines 106, 116-120, 131, 142-143: region map rendering; 185-225: route map rendering; 257: close figure | Real render: region map with places + config, route map with trip + stops |
| `exif/extractor.py` | 80% | Lines 36-37, 41: file open error handling; 50, 55, 68: GPS tag parsing; 92: directory iteration; 115, 118, 125, 127-128: south/west coordinate refs; 141, 144-145: datetime parsing errors | Real test images: south hemisphere photo, photo with corrupt EXIF, photo with no datetime |
| `db/repository.py` | 91% | Lines 144-160: trip save with stops (upsert path); 229-231: region upsert; 381-386: photo list_by_trip empty | Real SQLite: save trip with stops then update, region upsert, photo list_by_trip with no results |

### Server Routes — API TestClient Tests

| File | Current | Missing | Strategy |
|------|---------|---------|----------|
| `routes/regions.py` | 82% | Lines 49, 63-64, 68-74, 84-85: create region with all fields, delete with existence check | TestClient: create region, delete region |
| `routes/render.py` | 64% | Lines 59-110: region and route render branches | TestClient: render project with region/route map types |

### Styles — Unit Test

| File | Current | Missing | Strategy |
|------|---------|---------|----------|
| `renderer/styles.py` | 95% | Lines 70-71: TypeError when YAML content is not a dict | Unit test: load a YAML file containing a list instead of a dict |

### Coverage Exclusions

Add to `pyproject.toml` `[tool.coverage.run]` omit:
- `src/voyages/__main__.py` — trivial 4-line entry point, untestable without subprocess

### Threshold Bump

After all tests pass, change `Makefile` `--cov-fail-under` from 89 to 95.

## E2E Test Details

### serve command E2E

Start `voyages serve` as a subprocess, wait briefly for startup, make an HTTP request to the health/places endpoint, verify 200, then terminate the process. Use a random available port to avoid conflicts.

### render command E2E (region + route)

1. Create a place via `voyages place add`
2. Create a trip via `voyages trip create`
3. Create a project with `--map-type region`, then render — verify output file exists
4. Create a project with `--map-type route`, then render — verify output file exists

These cover the render_commands.py branches for region and route map types.

### trip/project command E2E

- `voyages trip create "Test" && voyages trip list` — verify output contains "Test"
- `voyages project create "Map" && voyages project list && voyages project show "Map"` — verify output

## Infrastructure Test Details

### Renderer: Region and Route Maps

Add tests to `tests/infrastructure/test_renderer.py`:
- `test_render_region_with_places_and_config`: render region map with places, config (center_lat, center_lon, extent). Verify file exists, PNG magic bytes.
- `test_render_route_with_trip`: render route map with trip containing 3+ stops. Verify file exists, PNG magic bytes.
- These paths exercise lines 106-225 in engine.py.

### EXIF: South/West Coordinates and Error Cases

Create additional test fixtures:
- A JPEG with south hemisphere GPS (latitude ref "S") — test negative latitude extraction
- Test the `_parse_gps_coord` method with west reference ("W") for negative longitude
- Test with corrupt/missing EXIF tags — verify graceful None return
- Test `_parse_datetime` with invalid datetime string — verify None return

### DB: Trip Stop Persistence and Edge Cases

Add tests to `tests/infrastructure/test_db_repository.py`:
- Save a trip with stops, then update the trip (change stops) — verify the upsert deletes old stops and inserts new ones (lines 144-160)
- Region upsert — save region, update name, verify (lines 229-231)
- `list_by_trip` with no matching photos — verify empty list (lines 381-386)

## Out of Scope

- Refactoring production code for testability (we test what exists)
- Adding new features
- Changing the coverage tool or adding Codecov
- Testing web frontend (Svelte)

## Success Criteria

1. Overall coverage ≥ 95%
2. Domain coverage remains 100%
3. `--cov-fail-under=95` in Makefile
4. `__main__.py` excluded from coverage
5. All new tests pass in CI
6. No existing tests broken
