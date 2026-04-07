# Test Hardening PR 1: Fix Gaps (P0 + P1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix API error handling bugs (500→400/404) via TDD and add missing error path tests across services, API, and CLI.

**Architecture:** Register shared FastAPI exception handlers in `create_app()` for `ValueError`→400 and `EntityNotFoundError`→404. Add error path tests for all API endpoints, application services, and CLI commands. TDD throughout — write failing tests first.

**Tech Stack:** pytest, FastAPI TestClient, Typer CliRunner, unittest.mock

**Spec:** `docs/superpowers/specs/2026-04-07-test-hardening-design.md` (PR 1 section)
**Issue:** dalbrecht/Voyages#4

---

**Important context for all tasks:**
- Server test pattern: `TestClient(create_app(database_url="sqlite://"))` — uses in-memory SQLite
- Application test pattern: Fake repositories with `_store: dict[uuid.UUID, Entity]`, wired in `setup_method()`
- CLI test pattern: `@patch("voyages.cli.<module>.get_<service>")` with `CliRunner().invoke(app, [...])`
- Domain errors: `EntityNotFoundError(entity_type: str, entity_id: UUID)` base, with `PlaceNotFoundError`, `TripNotFoundError`, `ProjectNotFoundError`, `RegionNotFoundError` subclasses
- All in `src/voyages/domain/errors.py`

---

### Task 1: API Exception Handlers (TDD)

**Files:**
- Modify: `src/voyages/server/__init__.py` (add exception handlers after line 72)
- Create: `tests/server/test_api_error_handling.py`

This task establishes the shared error handling that all subsequent API tests depend on.

- [ ] **Step 1: Write failing tests for ValueError → 400 and EntityNotFoundError → 404**

Create `tests/server/test_api_error_handling.py`:

```python
"""Tests for API error handling — invalid input and missing entities."""

from __future__ import annotations

import uuid

from starlette.testclient import TestClient

from voyages.server import create_app

EXPECTED_BAD_REQUEST = 400
EXPECTED_NOT_FOUND = 404
EXPECTED_NO_CONTENT = 204
EXPECTED_CREATED = 201


def _make_client() -> TestClient:
    app = create_app(database_url="sqlite://")
    return TestClient(app)


class TestInvalidUUID:
    """DELETE with malformed UUID string should return 400, not 500."""

    def test_delete_place_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.delete("/api/places/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()

    def test_delete_trip_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.delete("/api/trips/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()

    def test_delete_project_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.delete("/api/projects/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()

    def test_delete_region_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.delete("/api/regions/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()

    def test_render_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.post("/api/render/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()


class TestEntityNotFound:
    """DELETE/POST with valid but nonexistent UUID should return 404."""

    def test_delete_place_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/places/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()

    def test_delete_trip_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/trips/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()

    def test_delete_project_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/projects/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()

    def test_delete_region_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/regions/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()

    def test_render_project_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.post(f"/api/render/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/server/test_api_error_handling.py -v
```

Expected: All `TestInvalidUUID` tests fail with 500 instead of 400. `TestEntityNotFound` tests may fail with 204 (silent deletion) or 500.

- [ ] **Step 3: Add exception handlers in create_app()**

In `src/voyages/server/__init__.py`, add these imports at the top:

```python
from fastapi import Request as FastAPIRequest
from fastapi.responses import JSONResponse
from voyages.domain.errors import EntityNotFoundError
```

Then add exception handlers inside `create_app()`, after the router includes (after line 72):

```python
    @app.exception_handler(ValueError)
    async def value_error_handler(request: FastAPIRequest, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        request: FastAPIRequest, exc: EntityNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
```

- [ ] **Step 4: Add not-found raises in route DELETE handlers**

The DELETE handlers currently call `repo.delete(uuid.UUID(id))` silently — they don't check if the entity exists. Each needs to fetch first, then raise if not found.

**`src/voyages/server/routes/places.py`** — replace the delete handler body (lines 105-107):

```python
@router.delete("/places/{place_id}", status_code=204)
def delete_place(request: Request, place_id: str) -> Response:
    svc = _get_service(request)
    pid = uuid.UUID(place_id)
    place = svc.get(pid)
    if place is None:
        from voyages.domain.errors import PlaceNotFoundError
        raise PlaceNotFoundError(pid)
    svc.delete(pid)
    return Response(status_code=204)
```

Apply the same pattern to trips, projects, regions, and render routes. Each DELETE handler should:
1. Parse UUID (ValueError caught by handler if invalid)
2. Fetch entity, raise specific NotFoundError if None
3. Delete and return 204

For the render route, the fetch-and-raise-if-missing is for the project lookup.

Note: If the service classes don't have a `get()` method, you may need to use the repository directly or add the check. Read the actual service to determine the right approach — if `svc.delete()` silently ignores missing entities, the fetch+raise pattern above is correct.

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/server/test_api_error_handling.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Run full test suite to check for regressions**

```bash
uv run pytest -v
```

Expected: All existing tests still pass. The ValueError handler should not break existing valid requests because those don't raise ValueError.

- [ ] **Step 7: Commit**

```bash
git add src/voyages/server/__init__.py src/voyages/server/routes/ tests/server/test_api_error_handling.py
git commit -m "fix(api): return proper 400/404 errors instead of 500

Add shared FastAPI exception handlers for ValueError (400) and
EntityNotFoundError (404). Add entity existence checks in DELETE
handlers. TDD: tests written first, then fixed."
```

---

### Task 2: API Validation Error Tests (422)

**Files:**
- Modify: `tests/server/test_api_error_handling.py`

These test that FastAPI/Pydantic returns 422 for invalid request bodies. These should already pass without code changes (FastAPI handles validation automatically).

- [ ] **Step 1: Add 422 validation tests**

Append to `tests/server/test_api_error_handling.py`:

```python
EXPECTED_UNPROCESSABLE = 422


class TestValidationErrors:
    """POST with invalid request bodies should return 422."""

    def test_create_place_missing_name(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/places",
            json={"lat": 48.85, "lon": 2.35, "source": "manual"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_place_invalid_lat_type(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/places",
            json={"name": "Paris", "lat": "not-a-number", "lon": 2.35, "source": "manual"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_trip_missing_name(self) -> None:
        client = _make_client()
        response = client.post("/api/trips", json={})
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_project_missing_name(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/projects",
            json={"map_type": "travel"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_project_invalid_map_type(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/projects",
            json={"name": "Test", "map_type": "invalid_type"},
        )
        # MapType("invalid_type") raises ValueError, caught by handler → 400
        # OR if Pydantic validates → 422
        # Either way, it should NOT be 500
        assert response.status_code in (EXPECTED_BAD_REQUEST, EXPECTED_UNPROCESSABLE)

    def test_create_region_missing_name(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/regions",
            json={"region_type": "country"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_region_missing_region_type(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/regions",
            json={"name": "France"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/server/test_api_error_handling.py::TestValidationErrors -v
```

Expected: All pass (FastAPI/Pydantic handles validation). The `invalid_map_type` test accepts either 400 (ValueError handler) or 422 (if Pydantic validates). If any fail with 500, the ValueError handler from Task 1 needs adjustment.

- [ ] **Step 3: Commit**

```bash
git add tests/server/test_api_error_handling.py
git commit -m "test(api): add validation error tests (422) for all POST endpoints"
```

---

### Task 3: Application Service Error Path Tests — PhotoService

**Files:**
- Modify: `tests/application/test_photo_service.py`

- [ ] **Step 1: Add failing tests for assign_to_trip/place with nonexistent photo**

Append to the `TestPhotoService` class in `tests/application/test_photo_service.py`:

```python
    def test_assign_to_trip_photo_not_found(self) -> None:
        nonexistent_id = uuid.uuid4()
        trip_id = uuid.uuid4()
        with pytest.raises(ValueError, match="not found"):
            self.service.assign_to_trip(nonexistent_id, trip_id)

    def test_assign_to_place_photo_not_found(self) -> None:
        nonexistent_id = uuid.uuid4()
        place_id = uuid.uuid4()
        with pytest.raises(ValueError, match="not found"):
            self.service.assign_to_place(nonexistent_id, place_id)
```

Make sure `import pytest` is at the top of the file.

- [ ] **Step 2: Run tests to verify they pass (or fail — document which)**

```bash
uv run pytest tests/application/test_photo_service.py::TestPhotoService::test_assign_to_trip_photo_not_found tests/application/test_photo_service.py::TestPhotoService::test_assign_to_place_photo_not_found -v
```

Expected: These should PASS because the source code already raises `ValueError` at lines 48-49 and 57-58 of `photo_service.py`. If the `match` pattern doesn't match, adjust it to match the actual error message.

- [ ] **Step 3: Commit**

```bash
git add tests/application/test_photo_service.py
git commit -m "test(service): add error path tests for PhotoService assign methods"
```

---

### Task 4: Application Service Error Path Tests — TripService & RegionService

**Files:**
- Modify: `tests/application/test_trip_service.py`
- Modify: `tests/application/test_region_service.py`

- [ ] **Step 1: Add TripService reorder_stops edge case tests**

Append to the test class in `tests/application/test_trip_service.py`:

```python
    def test_reorder_stops_with_unknown_place_id(self) -> None:
        """Reorder with place_ids not in the trip — document actual behavior."""
        trip = self.service.create(name="Test Trip")
        # Add a real stop first
        known_place = uuid.uuid4()
        self.service.add_stop(trip.id, known_place)
        # Reorder with an unknown place_id
        unknown_place = uuid.uuid4()
        updated = self.service.reorder_stops(trip.id, [unknown_place, known_place])
        # The unknown place won't be in the existing stops map,
        # so it gets skipped. Document this behavior:
        positions = [s.position for s in updated.stops]
        # Verify at least the known place is still there
        known_stops = [s for s in updated.stops if s.place_id == known_place]
        assert len(known_stops) == 1

    def test_reorder_stops_trip_not_found(self) -> None:
        with pytest.raises(TripNotFoundError):
            self.service.reorder_stops(uuid.uuid4(), [uuid.uuid4()])
```

Make sure `TripNotFoundError` is imported. Check existing imports at the top of the file and add if needed:
```python
from voyages.domain.errors import TripNotFoundError
```

- [ ] **Step 2: Add RegionService case-sensitivity test**

Append to the test class in `tests/application/test_region_service.py`:

```python
    def test_derive_from_places_case_sensitive(self) -> None:
        """Verify that 'France' and 'france' are treated as different countries."""
        places = [
            Place(
                id=uuid.uuid4(),
                name="Paris",
                latitude=48.85,
                longitude=2.35,
                source="manual",
                country="France",
            ),
            Place(
                id=uuid.uuid4(),
                name="Lyon",
                latitude=45.76,
                longitude=4.83,
                source="manual",
                country="france",  # lowercase
            ),
        ]
        self.place_repo = FakePlaceRepository(places=places)
        self.service = RegionService(
            region_repo=self.region_repo, place_repo=self.place_repo
        )

        regions = self.service.derive_from_places()
        region_names = {r.name for r in regions}
        # Current behavior: case-sensitive — both create separate regions
        assert "France" in region_names
        assert "france" in region_names
        assert len(regions) == 2  # noqa: PLR2004
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/application/test_trip_service.py tests/application/test_region_service.py -v
```

Expected: All pass (tests document existing behavior).

- [ ] **Step 4: Commit**

```bash
git add tests/application/test_trip_service.py tests/application/test_region_service.py
git commit -m "test(service): add error path tests for TripService and RegionService"
```

---

### Task 5: Application Service Error Path Tests — ProjectService

**Files:**
- Modify: `tests/application/test_project_service.py`

Note: `test_add_place_avoids_duplicates` and `test_add_place_project_not_found_raises` already exist. We need the same tests for `add_trip` and `add_region`.

- [ ] **Step 1: Add add_trip and add_region error path tests**

Append to the test class in `tests/application/test_project_service.py`:

```python
    def test_add_trip_to_project(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        updated = self.service.add_trip(project.id, TRIP_ID)
        assert TRIP_ID in updated.trip_ids

    def test_add_trip_avoids_duplicates(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        self.service.add_trip(project.id, TRIP_ID)
        updated = self.service.add_trip(project.id, TRIP_ID)
        assert updated.trip_ids.count(TRIP_ID) == 1

    def test_add_trip_project_not_found_raises(self) -> None:
        with pytest.raises(ProjectNotFoundError):
            self.service.add_trip(uuid.uuid4(), TRIP_ID)

    def test_add_region_to_project(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        updated = self.service.add_region(project.id, REGION_ID)
        assert REGION_ID in updated.region_ids

    def test_add_region_avoids_duplicates(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        self.service.add_region(project.id, REGION_ID)
        updated = self.service.add_region(project.id, REGION_ID)
        assert updated.region_ids.count(REGION_ID) == 1

    def test_add_region_project_not_found_raises(self) -> None:
        with pytest.raises(ProjectNotFoundError):
            self.service.add_region(uuid.uuid4(), REGION_ID)
```

Verify that `TRIP_ID` and `REGION_ID` constants already exist at the top of the file (they should — the exploration found them at lines 15-18). Also verify `ProjectNotFoundError` is imported.

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/application/test_project_service.py -v
```

Expected: All pass.

- [ ] **Step 3: Commit**

```bash
git add tests/application/test_project_service.py
git commit -m "test(service): add error path tests for ProjectService add_trip and add_region"
```

---

### Task 6: CLI Error Path Tests

**Files:**
- Modify: `tests/cli/test_cli_commands.py`

Note: `test_render_project_not_found` already exists in `test_cli_render.py`. `test_import_photos_invalid_dir` already exists in `test_cli_import.py`. We need: missing required flags, invalid map-type, and invalid coordinates.

- [ ] **Step 1: Add CLI error tests**

Append to `tests/cli/test_cli_commands.py`:

```python
class TestCliErrorPaths:
    """Test CLI commands with invalid input."""

    def test_place_add_missing_name(self) -> None:
        result = runner.invoke(app, ["place", "add", "--lat", "48.85", "--lon", "2.35"])
        assert result.exit_code != 0

    def test_place_add_missing_lat(self) -> None:
        result = runner.invoke(app, ["place", "add", "--name", "Paris", "--lon", "2.35"])
        assert result.exit_code != 0

    def test_place_add_missing_lon(self) -> None:
        result = runner.invoke(app, ["place", "add", "--name", "Paris", "--lat", "48.85"])
        assert result.exit_code != 0

    @patch("voyages.cli.project_commands.get_project_service")
    def test_project_create_invalid_map_type(self, mock_get_svc: MagicMock) -> None:
        svc = MagicMock()
        svc.create.side_effect = ValueError("'invalid' is not a valid MapType")
        mock_get_svc.return_value = svc
        result = runner.invoke(app, ["project", "create", "Test", "--map-type", "invalid"])
        # MapType("invalid") raises ValueError in the command handler
        assert result.exit_code != 0

    def test_trip_create_missing_name(self) -> None:
        result = runner.invoke(app, ["trip", "create"])
        assert result.exit_code != 0

    @patch("voyages.cli.place_commands.get_place_service")
    def test_place_add_invalid_coordinates(self, mock_get_svc: MagicMock) -> None:
        """Document behavior when lat > 90 — CLI has no validation."""
        svc = MagicMock()
        place = Place(
            id=uuid.uuid4(), name="Bad", latitude=999.0, longitude=0.0, source="cli"
        )
        svc.create.return_value = place
        mock_get_svc.return_value = svc
        result = runner.invoke(
            app, ["place", "add", "--name", "Bad", "--lat", "999", "--lon", "0"]
        )
        # CLI currently accepts any float — no coordinate validation
        # This documents the gap: invalid coords are passed through to service
        assert result.exit_code == 0
```

Make sure `MagicMock`, `patch`, `Place`, and `uuid` imports are at the top of the file. Check existing imports — `MagicMock`, `patch`, `Place`, and `uuid` should already be there since other tests in this file use them.

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/cli/test_cli_commands.py::TestCliErrorPaths -v
```

Expected: Most should pass — Typer auto-validates required options and arguments. The `invalid_map_type` test may need adjustment depending on whether the ValueError is caught by Typer or propagates. If the CLI command catches it and prints an error, adjust the assertion.

- [ ] **Step 3: Fix any failing tests**

If `test_project_create_invalid_map_type` fails because the command doesn't catch the `ValueError`, the test needs to verify the actual behavior (Typer prints a traceback and exits nonzero, or the ValueError propagates). Read the actual command at `src/voyages/cli/project_commands.py:45` — `mt = MapType(map_type)` is called without try/except. If this causes a traceback:

Option A: The test is correct — the CLI has a bug (uncaught ValueError). Document this as expected current behavior (exit_code != 0 from unhandled exception).

Option B: If Typer catches it gracefully, adjust assertion to match.

- [ ] **Step 4: Commit**

```bash
git add tests/cli/test_cli_commands.py
git commit -m "test(cli): add error path tests for missing flags and invalid input"
```

---

### Task 7: Run Full Suite and Create PR

**Files:**
- Modify: `Makefile` (no changes needed for PR 1)
- Modify: `pyproject.toml` (no changes needed for PR 1)

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest -v
```

Expected: All tests pass — both old and new.

- [ ] **Step 2: Run linting**

```bash
uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src
```

Expected: All pass. If ruff or mypy flag issues in the new test or source changes, fix them.

- [ ] **Step 3: Review commit history**

```bash
git log --oneline -10
```

Expected: 6 commits covering exception handlers, validation tests, and service/CLI error tests.

- [ ] **Step 4: Push and create PR**

```bash
git push -u origin <branch-name>
gh pr create \
  --title "fix(api): add error handling and missing error path tests (P0+P1)" \
  --body "$(cat <<'EOF'
## Summary

Fixes dalbrecht/Voyages#4 (P0 + P1)

- **P0 Bug Fix:** API routes now return proper error responses instead of 500:
  - `ValueError` (invalid UUID) → 400 Bad Request
  - `EntityNotFoundError` (missing entity) → 404 Not Found
  - Implemented via shared FastAPI exception handlers in `create_app()`
  - DELETE handlers now check entity existence before deleting
- **P1 Error Path Tests:**
  - API: 422 validation tests for all POST endpoints (missing fields, invalid types)
  - Services: PhotoService assign not-found, TripService reorder edge cases, RegionService case sensitivity, ProjectService add_trip/add_region
  - CLI: Missing required flags, invalid map-type

## Test plan

- [ ] `uv run pytest -v` — all tests pass
- [ ] `uv run ruff check src tests` — no lint issues
- [ ] `uv run mypy src` — no type errors
- [ ] Manual: `curl -X DELETE http://127.0.0.1:8080/api/places/bad-uuid` returns 400
- [ ] Manual: `curl -X DELETE http://127.0.0.1:8080/api/places/<random-uuid>` returns 404

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
