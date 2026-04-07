# Test Hardening Design Spec

**Date:** 2026-04-07
**Status:** Draft
**Issue:** dalbrecht/Voyages#4

## Overview

Address test suite gaps identified by adversarial review. Two PRs: PR 1 fixes broken behavior and adds missing error path tests (P0+P1). PR 2 strengthens existing tests and adds integration/E2E coverage (P2+P3). TDD approach throughout — failing tests first, then fixes.

## Goals

1. API routes return proper error responses (400/422/404) instead of 500 on invalid input
2. Every service method error path has a test
3. Every API endpoint has error response tests (400, 404, 422)
4. CLI error cases are tested
5. Domain edge cases (NaN, Infinity, empty strings, boundaries) are covered
6. DB round-trip tests assert all fields
7. Renderer tests validate output content (magic bytes, dimensions, marker presence)
8. Full-stack integration tests exist (in-process and subprocess)
9. Tautological mock tests are replaced with meaningful assertions

## PR 1: Fix Gaps (P0 + P1)

### P0: API Error Handling Bug Fixes (TDD)

**The bug:** Route handlers have unguarded `uuid.UUID()` and `MapType()` calls that raise `ValueError`, producing 500 responses instead of proper HTTP errors.

**Affected routes:**
- `routes/places.py` — `uuid.UUID(place_id)` on DELETE
- `routes/trips.py` — `uuid.UUID(trip_id)` on DELETE
- `routes/projects.py` — `uuid.UUID(project_id)` on DELETE, `MapType(body.map_type)` on POST
- `routes/regions.py` — `uuid.UUID(region_id)` on DELETE
- `routes/render.py` — `uuid.UUID(project_id)` on POST

**Fix strategy:** Register shared FastAPI exception handlers at the app level in `create_app()` rather than adding try/except blocks in every route:
- `ValueError` → 400 Bad Request with `{"detail": "..."}` body
- `EntityNotFoundError` (domain exception) → 404 Not Found with `{"detail": "..."}` body

This prevents future routes from having the same bug and follows FastAPI conventions.

**TDD sequence per endpoint:**
1. Write test: invalid UUID string → assert 400
2. Write test: well-formed but nonexistent UUID → assert 404
3. Write test (projects only): invalid `map_type` value → assert 422
4. Run tests → confirm they fail (currently get 500 or no 404 handling)
5. Implement exception handlers in `create_app()`
6. Add `EntityNotFoundError` raises in service methods where missing
7. Run tests → confirm they pass

**Expected error responses:**
- `400 Bad Request`: `{"detail": "Invalid UUID: <value>"}`
- `404 Not Found`: `{"detail": "<EntityType> <id> not found"}`
- `422 Unprocessable Entity`: FastAPI auto-generates from Pydantic validation or we add explicit validation for `map_type`

### P1: Missing Error Path Tests

#### Application Service Tests

New tests added to existing test files:

**`tests/application/test_photo_service.py`:**
- `test_assign_to_trip_photo_not_found` — call `assign_to_trip()` with nonexistent photo_id → assert `ValueError` raised
- `test_assign_to_place_photo_not_found` — call `assign_to_place()` with nonexistent photo_id → assert `ValueError` raised
- `test_import_nonexistent_directory` — call `import_from_directory()` with bad path → assert appropriate error

**`tests/application/test_trip_service.py`:**
- `test_reorder_stops_invalid_place_ids` — call `reorder_stops()` with place_ids not in the trip → document and assert current behavior
- `test_add_stop_place_not_validated` — add a stop with arbitrary UUID → verify it's accepted (FK not validated at domain level, document this)

**`tests/application/test_region_service.py`:**
- `test_derive_from_places_case_sensitivity` — places with "France" and "france" → verify case-sensitive matching (both create separate regions, or one is deduped — document actual behavior)

**`tests/application/test_project_service.py`:**
- `test_add_duplicate_place` — add same place_id twice → verify idempotent or duplicate behavior
- `test_add_duplicate_trip` — same for trip_id
- `test_add_duplicate_region` — same for region_id

#### API Error Response Tests

New test cases in existing API test files, covering every endpoint group:

**Places:**
- POST missing required field (`name` omitted) → 422
- POST invalid field type (`lat: "not-a-number"`) → 422
- DELETE malformed UUID → 400
- DELETE nonexistent UUID → 404

**Trips:**
- POST missing `name` → 422
- DELETE malformed UUID → 400
- DELETE nonexistent UUID → 404

**Projects:**
- POST missing `name` → 422
- POST invalid `map_type` → 422 (after P0 fix adds validation)
- DELETE malformed UUID → 400
- DELETE nonexistent UUID → 404

**Regions:**
- POST missing `name` or `region_type` → 422
- DELETE malformed UUID → 400
- DELETE nonexistent UUID → 404

**Render:**
- POST malformed UUID → 400
- POST nonexistent project UUID → 404

#### CLI Error Path Tests

Expand existing CLI test files:

- `voyages render "nonexistent-project"` → nonzero exit code, error message
- `voyages place add` with missing required `--name` → error + help text
- `voyages project create "test" --map-type invalid` → error message
- `voyages import photos /nonexistent/path` → error handling
- `voyages place add --name "x" --lat 999 --lon 0` → document behavior (no coordinate validation in CLI currently)

## PR 2: Raise the Bar (P2 + P3)

### P2: Strengthen Existing Tests

#### Domain Edge Cases

**`tests/domain/test_value_objects.py`:**
- `Coordinates` with `float('nan')` → assert `ValueError`
- `Coordinates` with `float('inf')` / `float('-inf')` → assert `ValueError`
- `Coordinates` with exact boundaries: `(90.0, 180.0)`, `(-90.0, -180.0)` → assert valid
- `Coordinates` with just-outside boundaries: `(90.1, 0)`, `(0, 180.1)` → assert `ValueError`
- `Coordinates` with `-0.0` → assert valid (equal to `0.0`)
- `BoundingBox.contains()` with point on exact edge → verify behavior
- `BoundingBox.contains()` with NaN point → verify behavior
- `OutputFormat.extension` for all 5 values — verify `.svg`, `.pdf`, `.png`, `.webp`, `.eps`
- `MapType` values match expected strings

**`tests/domain/test_entities.py`:**
- `Place` with `name=""` (empty string) → verify accepted (no validation)
- `Trip` with empty `stops` list → verify default factory independence between instances
- `Project` with empty `config` dict → verify default factory independence
- `Photo` with all optional fields as `None` → verify construction

#### DB Round-Trip Completeness

**`tests/infrastructure/test_db_repository.py`:**
- Expand `test_save_and_get` to assert ALL fields: `id`, `name`, `latitude`, `longitude`, `source`, `country`, `admin1`, `category`, `notes`, `created_at`, `updated_at`
- Test unique constraint on `ProjectModel.name` — save two projects with same name → assert `IntegrityError`
- Test foreign key behavior — delete a Place referenced by a Photo → document behavior (cascade or error)
- Test config JSON round-trip — save project with `config={"key": "value with \"quotes\"", "nested": {"a": 1}, "unicode": "\u00e9"}` → load → assert equal
- Test upsert updates `updated_at` field

#### Renderer Content Validation

**`tests/infrastructure/test_renderer.py`:**

Magic bytes verification:
- PNG output starts with `b'\x89PNG\r\n\x1a\n'`
- PDF output starts with `b'%PDF'`
- SVG output contains `<svg` or starts with `<?xml`
- EPS output starts with `%!PS-Adobe`

Dimensions check (PNG only):
- Use PIL `Image.open()` to verify width matches `--width` config parameter
- Verify DPI is embedded in PNG metadata (EXIF or pHYs chunk)

Spot-check marker presence (PNG only):
- Render a travel map with a single place at known coordinates
- Use PIL to read the rendered image
- Sample the pixel at approximately where the marker should be (calculate from projection)
- Assert it differs from the background color (not an exact color match — just "not background")

Edge cases:
- Empty places list → verify renders without error (blank map)
- Route map with fewer than 2 stops → verify behavior (should handle gracefully)
- Test all output formats (SVG, PDF, PNG, EPS) — currently only PNG is tested
- WebP → verify it produces PNG (OutputFormat.WEBP maps to "png" in renderer)

#### Fix Tautological Tests

**`tests/application/test_place_service.py`:**
- Replace `search()` test: instead of asserting mock returns its configured value, use a fake geocoding service that tracks calls and verify (a) the service actually calls the geocoder, and (b) the results are passed through correctly.

**`tests/infrastructure/test_exif.py`:**
- Add a real test JPEG fixture: create a minimal valid JPEG with EXIF GPS data (committed as `tests/fixtures/gps_photo.jpg`). Test that the extractor reads correct lat/lon from it.
- Add test with a JPEG that has no EXIF data → verify returns None/empty.
- Add test with corrupt/truncated EXIF → verify graceful handling.

**`tests/infrastructure/test_nominatim.py`:**
- Add test for malformed JSON response (missing `lat`/`lon` fields) → verify error handling
- Add test for empty results array → verify returns empty list
- Add test for response with missing `address` field in reverse geocode → verify graceful handling

#### Style Loading Edge Cases

**`tests/infrastructure/test_styles.py`:**
- Load style YAML missing a required field (e.g., no `ocean` key) → assert `KeyError` or meaningful error
- Load from nonexistent file path → assert `FileNotFoundError`
- Load malformed YAML (invalid syntax) → assert error
- Load all 4 built-in styles and verify all fields are populated (no None values)

### P3: Integration Tests

#### In-Process Integration Tests (`tests/integration/`)

Using FastAPI `TestClient` with real in-memory SQLite. No mocks. Tests the full stack: route → service → repository → database.

**`tests/integration/test_place_workflow.py`:**
- Create a place via POST → list via GET → verify created place appears → delete via DELETE → list again → verify gone
- Create multiple places → search by name → verify correct results

**`tests/integration/test_project_workflow.py`:**
- Create places → create project → render → verify response is a valid PNG file (magic bytes check)

**`tests/integration/test_import_workflow.py`:**
- Create a test JPEG with EXIF GPS data → import via PhotoService → verify Place and Photo are created with correct coordinates from EXIF

#### Subprocess E2E Tests (`tests/e2e/`)

Marked with `@pytest.mark.e2e`. Excluded from default test runs.

**`tests/e2e/test_cli_e2e.py`:**
- `voyages place add` → `voyages place list` → verify output contains the place name
- `voyages project create` → `voyages render` → verify output file exists and is a valid image
- `voyages render "nonexistent"` → nonzero exit code

**`tests/e2e/test_server_e2e.py`:**
- Start `voyages serve` in subprocess → HTTP request to `/api/places` → verify 200 → terminate server

Each E2E test uses `tmp_path` for a disposable working directory and SQLite database. The `voyages` command is invoked via `subprocess.run()`.

#### Pytest Configuration Changes

**`pyproject.toml` additions:**
```toml
[tool.pytest.ini_options]
markers = [
    "e2e: end-to-end tests that invoke CLI as subprocess (deselect with '-m not e2e')",
]
```

**`Makefile` changes:**
- `make test` → `uv run pytest -m "not e2e"` (fast, no subprocess overhead)
- Add `make test-e2e` → `uv run pytest -m e2e` (E2E only)
- Add `make test-all` → `uv run pytest` (everything)
- Update `make ci` to use `make test` (excludes E2E, keeps CI fast)

## Test Fixture: Real EXIF JPEG

Both PR 2 (test_exif.py) and PR 2 (integration test) need a real JPEG with EXIF GPS data.

**Create `tests/fixtures/gps_photo.jpg`:**
- Minimal valid JPEG (as small as possible — 1x1 or 2x2 pixel)
- EXIF GPS data embedded: latitude 48.8566, longitude 2.3522 (Paris)
- EXIF timestamp: 2025-06-15T14:30:00
- Generated programmatically in a setup script or committed as a binary fixture

Also create `tests/fixtures/no_gps_photo.jpg`:
- Minimal JPEG with no EXIF GPS data (but valid EXIF header)
- Used to test the "no GPS" handling path

## Out of Scope

- Performance/load testing (not a regression risk at current scale)
- Concurrency testing (SQLite doesn't support it well anyway)
- Network-level API testing (real HTTP server, not TestClient) — subprocess E2E covers this
- Mutation testing (valuable but a separate effort)
- Coverage tooling/reporting setup (use `pytest --cov` directly)

## Success Criteria

1. All API endpoints return proper error responses (400/422/404) — zero unhandled 500s for known error cases
2. Every service method error path has at least one test
3. Every API endpoint group has tests for: missing fields (422), malformed UUID (400), nonexistent UUID (404)
4. Domain `Coordinates` rejects NaN/Infinity with tests proving it
5. DB tests assert all entity fields on round-trip
6. Renderer tests verify output file format (magic bytes) and dimensions for PNG
7. At least one renderer test verifies marker presence via pixel sampling
8. Integration tests cover: place CRUD workflow, project→render workflow, photo import workflow
9. E2E tests cover: CLI place add→list, CLI render, CLI error handling
10. `make test` excludes E2E (fast CI), `make test-all` includes everything
11. No tautological tests remain — mocked service tests verify delegation, not mock return values
