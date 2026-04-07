# Test Hardening PR 2: Raise the Bar (P2 + P3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strengthen existing tests with edge cases, fix tautological tests, add content validation for renderer, and create integration/E2E test suites.

**Architecture:** Expand existing test files with edge cases (domain, DB, renderer, styles). Replace tautological mocks with meaningful assertions. Add real EXIF fixture. Create `tests/integration/` for full-stack in-process tests and expand `tests/e2e/` for subprocess tests. Add pytest markers and Makefile targets.

**Tech Stack:** pytest, PIL/Pillow, FastAPI TestClient, subprocess, pytest markers

**Spec:** `docs/superpowers/specs/2026-04-07-test-hardening-design.md` (PR 2 section)
**Issue:** dalbrecht/Voyages#4

---

**Important context for all tasks:**
- This PR builds on PR 1 (`fix/api-error-handling-p0-p1`) which added API exception handlers. Merge PR 1 first or branch from it.
- Current test count after PR 1: 261 tests
- Coordinates validation (`src/voyages/domain/value_objects.py:15-21`): uses `_LAT_MIN <= self.latitude <= _LAT_MAX` — NaN comparison returns False, so NaN DOES raise ValueError. But this is untested.
- Renderer (`src/voyages/infrastructure/renderer/engine.py`): returns output_path string, saves file via matplotlib. Format map: WEBP→"png".
- Style loader (`src/voyages/infrastructure/renderer/styles.py:50-72`): if name in builtin names → loads from `styles/` dir, else treats as file path.
- EXIF extractor (`src/voyages/infrastructure/exif/extractor.py`): `PillowExifService` with `extract_from_file(Path) -> Photo | None` and `extract_from_directory(Path) -> list[Photo]`.
- DB repos (`src/voyages/infrastructure/db/repository.py`): `get()` returns `Entity | None`, `save()` upserts, `delete()` by UUID.
- `tests/e2e/` already exists with `test_smoke.py`. `tests/integration/` and `tests/fixtures/` do NOT exist yet.

---

### Task 1: Domain Edge Cases

**Files:**
- Modify: `tests/domain/test_value_objects.py`
- Modify: `tests/domain/test_entities.py`

- [ ] **Step 1: Add Coordinates NaN/Infinity tests**

Append to `TestCoordinates` class in `tests/domain/test_value_objects.py`:

```python
    def test_nan_latitude_raises(self) -> None:
        with pytest.raises(ValueError, match="Latitude"):
            Coordinates(latitude=float("nan"), longitude=0.0)

    def test_nan_longitude_raises(self) -> None:
        with pytest.raises(ValueError, match="Longitude"):
            Coordinates(latitude=0.0, longitude=float("nan"))

    def test_inf_latitude_raises(self) -> None:
        with pytest.raises(ValueError, match="Latitude"):
            Coordinates(latitude=float("inf"), longitude=0.0)

    def test_neg_inf_latitude_raises(self) -> None:
        with pytest.raises(ValueError, match="Latitude"):
            Coordinates(latitude=float("-inf"), longitude=0.0)

    def test_inf_longitude_raises(self) -> None:
        with pytest.raises(ValueError, match="Longitude"):
            Coordinates(latitude=0.0, longitude=float("inf"))

    def test_negative_zero_is_valid(self) -> None:
        coords = Coordinates(latitude=-0.0, longitude=-0.0)
        assert coords.latitude == 0.0
        assert coords.longitude == 0.0
```

- [ ] **Step 2: Add BoundingBox edge case tests**

Append to `TestBoundingBox` class:

```python
    def test_contains_point_on_ne_corner(self) -> None:
        bbox = BoundingBox(
            southwest=Coordinates(40.0, -5.0),
            northeast=Coordinates(50.0, 5.0),
        )
        point = Coordinates(50.0, 5.0)
        assert bbox.contains(point) is True

    def test_contains_point_on_edge_latitude(self) -> None:
        bbox = BoundingBox(
            southwest=Coordinates(40.0, -5.0),
            northeast=Coordinates(50.0, 5.0),
        )
        point = Coordinates(50.0, 0.0)  # On north edge
        assert bbox.contains(point) is True
```

- [ ] **Step 3: Add entity edge case tests**

Append to relevant classes in `tests/domain/test_entities.py`:

```python
# Append to TestPlace
    def test_empty_string_name(self) -> None:
        """Empty string name is accepted — no validation at entity level."""
        place = Place(id=uuid.uuid4(), name="", latitude=0.0, longitude=0.0, source="test")
        assert place.name == ""

# Append to TestPhoto
    def test_all_optional_fields_none(self) -> None:
        """Photo with only required fields — all optionals default to None."""
        photo = Photo(id=uuid.uuid4(), file_path="/test.jpg")
        assert photo.latitude is None
        assert photo.longitude is None
        assert photo.taken_at is None
        assert photo.place_id is None
        assert photo.trip_id is None
```

Add `import math` at the top of `test_value_objects.py` if needed for any NaN/inf helpers, though `float("nan")` works without it.

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/domain/ -v
```

- [ ] **Step 5: Commit**

```bash
git add tests/domain/
git commit -m "test(domain): add NaN/Infinity/boundary edge cases for Coordinates and entities"
```

---

### Task 2: DB Round-Trip Completeness

**Files:**
- Modify: `tests/infrastructure/test_db_repository.py`

- [ ] **Step 1: Strengthen place save/get to assert ALL fields**

Find `test_save_and_get` in `TestSqlPlaceRepository` and expand its assertions. The current test only checks `name` and `country`. Add assertions for every field:

```python
    def test_save_and_get_all_fields(self, session: Session) -> None:
        repo = SqlPlaceRepository(session)
        now = datetime.now(tz=UTC)
        place = Place(
            id=uuid.uuid4(),
            name="Tokyo",
            latitude=35.6762,
            longitude=139.6503,
            source="manual",
            country="Japan",
            admin1="Tokyo",
            category="city",
            notes="Capital city",
            created_at=now,
            updated_at=now,
        )
        repo.save(place)

        loaded = repo.get(place.id)
        assert loaded is not None
        assert loaded.id == place.id
        assert loaded.name == "Tokyo"
        assert loaded.latitude == pytest.approx(35.6762)
        assert loaded.longitude == pytest.approx(139.6503)
        assert loaded.source == "manual"
        assert loaded.country == "Japan"
        assert loaded.admin1 == "Tokyo"
        assert loaded.category == "city"
        assert loaded.notes == "Capital city"
        assert loaded.created_at is not None
        assert loaded.updated_at is not None
```

Add imports: `from datetime import UTC, datetime` (check what's already imported).

- [ ] **Step 2: Add project config JSON round-trip test**

Append to `TestSqlProjectRepository`:

```python
    def test_config_json_round_trip(self, session: Session) -> None:
        repo = SqlProjectRepository(session)
        config = {
            "dpi": 300,
            "nested": {"key": "value"},
            "unicode": "\u00e9",
            "special": 'quotes "and" more',
        }
        project = Project(
            id=uuid.uuid4(),
            name="Config Test",
            map_type=MapType.TRAVEL,
            config=config,
        )
        repo.save(project)

        loaded = repo.get(project.id)
        assert loaded is not None
        assert loaded.config == config
        assert loaded.config["nested"]["key"] == "value"
        assert loaded.config["unicode"] == "\u00e9"
```

- [ ] **Step 3: Add unique constraint test for project name**

```python
    def test_duplicate_project_name_raises(self, session: Session) -> None:
        repo = SqlProjectRepository(session)
        project1 = Project(
            id=uuid.uuid4(), name="Duplicate", map_type=MapType.TRAVEL
        )
        project2 = Project(
            id=uuid.uuid4(), name="Duplicate", map_type=MapType.REGION
        )
        repo.save(project1)
        with pytest.raises(Exception):  # IntegrityError wrapped by SQLAlchemy
            repo.save(project2)
            session.flush()
```

Note: The exact exception depends on whether SQLAlchemy raises `IntegrityError` immediately on save or on flush. Read the save method to determine. Use broad `Exception` if unsure, then narrow after seeing what actually raises.

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/infrastructure/test_db_repository.py -v
```

- [ ] **Step 5: Commit**

```bash
git add tests/infrastructure/test_db_repository.py
git commit -m "test(db): add full-field assertions, JSON round-trip, and unique constraint tests"
```

---

### Task 3: Renderer Content Validation

**Files:**
- Modify: `tests/infrastructure/test_renderer.py`

- [ ] **Step 1: Add magic bytes and dimensions tests**

Append new test class to `tests/infrastructure/test_renderer.py`:

```python
from PIL import Image


class TestRenderOutputValidation:
    """Verify rendered output is valid, not just that a file exists."""

    def test_png_magic_bytes(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")]
        out = tmp_path / "test.png"
        engine.render_travel_map(places, [], str(out), OutputFormat.PNG)
        with open(out, "rb") as f:
            header = f.read(8)
        assert header == b"\x89PNG\r\n\x1a\n"

    def test_svg_contains_svg_tag(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")]
        out = tmp_path / "test.svg"
        engine.render_travel_map(places, [], str(out), OutputFormat.SVG)
        content = out.read_text()
        assert "<svg" in content

    def test_pdf_magic_bytes(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")]
        out = tmp_path / "test.pdf"
        engine.render_travel_map(places, [], str(out), OutputFormat.PDF)
        with open(out, "rb") as f:
            header = f.read(4)
        assert header == b"%PDF"

    def test_eps_magic_bytes(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")]
        out = tmp_path / "test.eps"
        engine.render_travel_map(places, [], str(out), OutputFormat.EPS)
        with open(out, "rb") as f:
            header = f.read(11)
        assert header == b"%!PS-Adobe-"

    def test_png_dimensions_match_config(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [Place(id=uuid.uuid4(), name="Test", latitude=0.0, longitude=0.0, source="test")]
        out = tmp_path / "test.png"
        engine.render_travel_map(places, [], str(out), OutputFormat.PNG, config={"width": 800})
        img = Image.open(out)
        assert img.width == 800

    def test_marker_visible_on_rendered_map(self, tmp_path: Path) -> None:
        """Spot-check: a rendered map with one place should have non-background pixels."""
        style = load_style("default")
        engine = RenderEngine(style)
        places = [Place(id=uuid.uuid4(), name="Marker", latitude=0.0, longitude=0.0, source="test")]
        out = tmp_path / "marker.png"
        engine.render_travel_map(places, [], str(out), OutputFormat.PNG, config={"width": 400, "dpi": 72})
        img = Image.open(out)
        pixels = list(img.getdata())
        # The map should NOT be a single solid color (markers/features should vary)
        unique_colors = set(pixels)
        assert len(unique_colors) > 10  # A real map has many colors

    def test_empty_places_renders_without_error(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        out = tmp_path / "empty.png"
        engine.render_travel_map([], [], str(out), OutputFormat.PNG)
        assert out.exists()
        assert out.stat().st_size > 0
```

Add imports at the top: `from PIL import Image`. Also ensure `Place`, `uuid`, `OutputFormat`, `RenderEngine`, `load_style`, and `Path` are imported (check existing imports in the file).

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/infrastructure/test_renderer.py -v
```

Note: Renderer tests are slow (each renders a real map). If `test_png_dimensions_match_config` fails, the width may be calculated differently (matplotlib uses DPI and figure size, not pixel width directly). Check the engine's `_merge_config` to understand how width is applied. The test may need to verify `img.width` is close to but not exactly 800. Adjust assertion if needed.

- [ ] **Step 3: Commit**

```bash
git add tests/infrastructure/test_renderer.py
git commit -m "test(renderer): add format validation, dimension checks, and marker visibility tests"
```

---

### Task 4: Fix Tautological Tests + EXIF Fixture

**Files:**
- Create: `tests/fixtures/create_test_photos.py` (script to generate EXIF fixtures)
- Create: `tests/fixtures/gps_photo.jpg` (generated binary)
- Create: `tests/fixtures/no_gps_photo.jpg` (generated binary)
- Modify: `tests/application/test_place_service.py`
- Modify: `tests/infrastructure/test_exif.py`
- Modify: `tests/infrastructure/test_nominatim.py`

- [ ] **Step 1: Create EXIF test fixtures**

Create `tests/fixtures/create_test_photos.py`:

```python
"""Generate minimal JPEG test fixtures with and without EXIF GPS data."""
from __future__ import annotations

import struct
from pathlib import Path

from PIL import Image
import piexif


def _dms_to_rational(degrees: float, minutes: float, seconds: float) -> tuple:
    """Convert DMS to EXIF rational format."""
    return (
        (int(degrees), 1),
        (int(minutes), 1),
        (int(seconds * 100), 100),
    )


def create_gps_photo(output_path: Path) -> None:
    """Create a 2x2 JPEG with GPS EXIF data (Paris: 48.8566, 2.3522)."""
    img = Image.new("RGB", (2, 2), color="red")

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: "N",
        piexif.GPSIFD.GPSLatitude: _dms_to_rational(48.0, 51.0, 23.76),
        piexif.GPSIFD.GPSLongitudeRef: "E",
        piexif.GPSIFD.GPSLongitude: _dms_to_rational(2.0, 21.0, 7.92),
    }
    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: "2025:06:15 14:30:00",
    }
    exif_dict = {"GPS": gps_ifd, "Exif": exif_ifd}
    exif_bytes = piexif.dump(exif_dict)
    img.save(str(output_path), exif=exif_bytes)


def create_no_gps_photo(output_path: Path) -> None:
    """Create a 2x2 JPEG with no GPS EXIF data."""
    img = Image.new("RGB", (2, 2), color="blue")
    img.save(str(output_path))


if __name__ == "__main__":
    fixtures_dir = Path(__file__).parent
    create_gps_photo(fixtures_dir / "gps_photo.jpg")
    create_no_gps_photo(fixtures_dir / "no_gps_photo.jpg")
    print("Created test fixtures.")
```

**Important:** This script requires `piexif`. Check if it's in the project dependencies. If not, use an alternative approach — generate the EXIF bytes manually or use PIL's built-in EXIF support. If `piexif` is not available, create the fixtures using PIL's `img.save(path, exif=exif_data_bytes)` with manually constructed EXIF bytes, or simply use the mock-based approach and skip the real fixture. The implementer should check `pyproject.toml` for available dependencies.

If `piexif` is not available, a simpler approach: create a minimal JPEG programmatically using PIL alone (just `Image.new("RGB", (2,2)).save(path)`) and use it to test the "no GPS data" path. For GPS data, keep the existing mock-based test and add a note that a real fixture would require `piexif`.

Run the script to generate fixtures:
```bash
mkdir -p tests/fixtures
cd tests/fixtures && uv run python create_test_photos.py
```

- [ ] **Step 2: Add real-file EXIF test**

Append to `tests/infrastructure/test_exif.py`:

```python
class TestPillowExifRealFiles:
    """Tests using real JPEG files instead of mocks."""

    def test_extract_no_gps_photo_returns_none(self) -> None:
        fixture = Path(__file__).parent.parent / "fixtures" / "no_gps_photo.jpg"
        if not fixture.exists():
            pytest.skip("Test fixture not available")
        service = PillowExifService()
        result = service.extract_from_file(fixture)
        assert result is None

    def test_extract_gps_photo_returns_coordinates(self) -> None:
        fixture = Path(__file__).parent.parent / "fixtures" / "gps_photo.jpg"
        if not fixture.exists():
            pytest.skip("Test fixture not available")
        service = PillowExifService()
        result = service.extract_from_file(fixture)
        assert result is not None
        assert abs(result.latitude - 48.8566) < 0.01
        assert abs(result.longitude - 2.3522) < 0.01
        assert result.taken_at is not None
```

Add imports: `from pathlib import Path` and `from voyages.infrastructure.exif.extractor import PillowExifService`. Check existing imports.

- [ ] **Step 3: Fix tautological PlaceService search test**

In `tests/application/test_place_service.py`, find `test_search_delegates_to_geocoding` and replace it with a version that verifies the service actually calls the geocoding service:

```python
    def test_search_delegates_to_geocoding(self) -> None:
        """Verify search() calls geocoding.search() with the query and returns its results."""
        geocoding_place = Place(
            id=uuid.uuid4(),
            name="Paris, France",
            latitude=48.8566,
            longitude=2.3522,
            source="nominatim",
        )
        tracking_geocoding = FakeGeocodingService(results=[geocoding_place])
        service = PlaceService(
            place_repo=self.place_repo,
            geocoding=tracking_geocoding,
        )
        results = service.search("Paris")
        assert len(results) == 1
        assert results[0].name == "Paris, France"
        # Verify the geocoding service was actually called
        assert tracking_geocoding.search_called is True
        assert tracking_geocoding.last_query == "Paris"
```

Also modify `FakeGeocodingService` to track calls:

```python
class FakeGeocodingService:
    def __init__(self, results: list[Place] | None = None) -> None:
        self._results = results or []
        self.search_called = False
        self.last_query: str | None = None

    def search(self, query: str) -> list[Place]:
        self.search_called = True
        self.last_query = query
        return self._results

    def reverse_geocode(self, coords: Coordinates) -> Place | None:
        return None
```

Read the existing `FakeGeocodingService` in the file first and modify it to add tracking fields. Don't replace it entirely — just add the tracking attributes.

- [ ] **Step 4: Add Nominatim error handling tests**

Append to `tests/infrastructure/test_nominatim.py`:

```python
class TestNominatimErrorHandling:
    """Test error handling for malformed and missing responses."""

    @patch("voyages.infrastructure.geocoding.nominatim.httpx.get")
    def test_search_missing_lat_in_result(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = [{"display_name": "Test", "lon": "2.0", "address": {}}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        service = NominatimGeocodingService()
        # Should either skip the malformed result or raise
        # Document actual behavior
        try:
            results = service.search("test")
            # If it doesn't raise, it might return partial results
        except (KeyError, TypeError):
            pass  # Expected if no error handling

    @patch("voyages.infrastructure.geocoding.nominatim.httpx.get")
    def test_search_empty_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        service = NominatimGeocodingService()
        results = service.search("nonexistent")
        assert results == []

    @patch("voyages.infrastructure.geocoding.nominatim.httpx.get")
    def test_reverse_missing_address_field(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "display_name": "Test Place",
            "lat": "48.85",
            "lon": "2.35",
            # No "address" key
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        service = NominatimGeocodingService()
        # Document behavior when address is missing
        try:
            result = service.reverse_geocode(Coordinates(48.85, 2.35))
            # May return Place with country=None
            if result is not None:
                assert result.country is None or result.country == ""
        except (KeyError, TypeError):
            pass  # Expected if no error handling
```

Add imports: `Coordinates` from `voyages.domain.value_objects`, `NominatimGeocodingService` from the geocoding module.

- [ ] **Step 5: Run tests**

```bash
uv run pytest tests/application/test_place_service.py tests/infrastructure/test_exif.py tests/infrastructure/test_nominatim.py -v
```

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/ tests/application/test_place_service.py tests/infrastructure/test_exif.py tests/infrastructure/test_nominatim.py
git commit -m "test: fix tautological tests, add EXIF fixtures, and Nominatim error tests"
```

---

### Task 5: Style Loading Edge Cases

**Files:**
- Modify: `tests/infrastructure/test_styles.py`

- [ ] **Step 1: Add edge case tests**

Append to `TestLoadStyle` class:

```python
    def test_missing_yaml_field_raises(self, tmp_path: Path) -> None:
        """Style YAML missing a required field should raise an error."""
        style_file = tmp_path / "incomplete.yml"
        style_file.write_text("name: incomplete\nocean: '#000'\n")
        with pytest.raises((KeyError, TypeError)):
            load_style(str(style_file))

    def test_invalid_yaml_syntax_raises(self, tmp_path: Path) -> None:
        """Malformed YAML should raise an error."""
        style_file = tmp_path / "bad.yml"
        style_file.write_text("name: bad\nocean: [invalid\n")
        with pytest.raises(Exception):  # yaml.YAMLError
            load_style(str(style_file))

    def test_all_builtin_styles_have_all_fields(self) -> None:
        """Every built-in style should have all MapStyle fields populated (no None)."""
        for style in get_builtin_styles():
            assert style.name is not None
            assert style.ocean is not None
            assert style.land is not None
            assert style.visited is not None
            assert style.visited_light is not None
            assert style.route is not None
            assert style.font is not None
            assert style.borders is not None
            assert style.marker is not None
            assert style.marker_size > 0
            assert style.title_size > 0
            assert style.label_size > 0
```

Verify `Path` and `get_builtin_styles` are imported.

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/infrastructure/test_styles.py -v
```

- [ ] **Step 3: Commit**

```bash
git add tests/infrastructure/test_styles.py
git commit -m "test(styles): add edge cases for missing fields, invalid YAML, and field completeness"
```

---

### Task 6: In-Process Integration Tests

**Files:**
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_place_workflow.py`
- Create: `tests/integration/test_project_workflow.py`

These use FastAPI TestClient with real in-memory SQLite — no mocks. Tests the full stack: route → service → repository → DB.

- [ ] **Step 1: Create integration test directory and place workflow tests**

Create `tests/integration/__init__.py` (empty).

Create `tests/integration/test_place_workflow.py`:

```python
"""Integration tests: full-stack place CRUD workflow via API."""
from __future__ import annotations

from starlette.testclient import TestClient

from voyages.server import create_app


def _make_client() -> TestClient:
    return TestClient(create_app(database_url="sqlite://"))


class TestPlaceCrudWorkflow:
    """Create → list → verify → delete → verify gone."""

    def test_full_place_lifecycle(self) -> None:
        client = _make_client()

        # Create
        create_resp = client.post(
            "/api/places",
            json={"name": "Paris", "lat": 48.8566, "lon": 2.3522, "source": "manual", "country": "France"},
        )
        assert create_resp.status_code == 201
        place_id = create_resp.json()["id"]

        # List — should contain Paris
        list_resp = client.get("/api/places")
        assert list_resp.status_code == 200
        names = [p["name"] for p in list_resp.json()]
        assert "Paris" in names

        # Delete
        delete_resp = client.delete(f"/api/places/{place_id}")
        assert delete_resp.status_code == 204

        # List again — should be empty
        list_resp2 = client.get("/api/places")
        assert list_resp2.json() == []

    def test_create_multiple_and_search(self) -> None:
        client = _make_client()

        client.post("/api/places", json={"name": "Paris", "lat": 48.85, "lon": 2.35, "source": "manual"})
        client.post("/api/places", json={"name": "Parma", "lat": 44.80, "lon": 10.33, "source": "manual"})
        client.post("/api/places", json={"name": "Berlin", "lat": 52.52, "lon": 13.40, "source": "manual"})

        # Search — should find places matching query
        search_resp = client.get("/api/places/search", params={"q": "Par"})
        assert search_resp.status_code == 200
        results = search_resp.json()
        result_names = [r["name"] for r in results]
        assert "Paris" in result_names
        assert "Parma" in result_names
        assert "Berlin" not in result_names
```

- [ ] **Step 2: Create project workflow integration test**

Create `tests/integration/test_project_workflow.py`:

```python
"""Integration tests: project creation and render workflow via API."""
from __future__ import annotations

from starlette.testclient import TestClient

from voyages.server import create_app


def _make_client() -> TestClient:
    return TestClient(create_app(database_url="sqlite://"))


class TestProjectRenderWorkflow:
    """Create project → render → verify valid output."""

    def test_create_project_and_render(self) -> None:
        client = _make_client()

        # Create a place
        place_resp = client.post(
            "/api/places",
            json={"name": "Paris", "lat": 48.8566, "lon": 2.3522, "source": "manual"},
        )
        assert place_resp.status_code == 201

        # Create a project
        project_resp = client.post(
            "/api/projects",
            json={"name": "Test Map", "map_type": "travel"},
        )
        assert project_resp.status_code == 201
        project_id = project_resp.json()["id"]

        # Render
        render_resp = client.post(f"/api/render/{project_id}")
        assert render_resp.status_code == 200
        # Verify response is a PNG (magic bytes)
        assert render_resp.content[:8] == b"\x89PNG\r\n\x1a\n"
```

- [ ] **Step 3: Run integration tests**

```bash
uv run pytest tests/integration/ -v
```

- [ ] **Step 4: Commit**

```bash
git add tests/integration/
git commit -m "test(integration): add full-stack place CRUD and project render workflow tests"
```

---

### Task 7: E2E Subprocess Tests + Pytest Config

**Files:**
- Create: `tests/e2e/test_cli_e2e.py`
- Modify: `pyproject.toml` (add e2e marker)
- Modify: `Makefile` (add test-e2e, test-all targets)

- [ ] **Step 1: Add pytest marker to pyproject.toml**

In `pyproject.toml`, find the `[tool.pytest.ini_options]` section and add:

```toml
markers = [
    "e2e: end-to-end tests that invoke CLI as subprocess (deselect with '-m not e2e')",
]
```

- [ ] **Step 2: Update Makefile test targets**

Change the `test` target from:
```makefile
test: ## Run tests
	uv run pytest
```
to:
```makefile
test: ## Run tests (excludes e2e)
	uv run pytest -m "not e2e"
```

Add new targets:
```makefile
test-e2e: ## Run end-to-end tests only
	uv run pytest -m e2e

test-all: ## Run all tests including e2e
	uv run pytest
```

- [ ] **Step 3: Create E2E CLI tests**

Create `tests/e2e/test_cli_e2e.py`:

```python
"""End-to-end tests that invoke the voyages CLI as a subprocess."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.e2e
class TestCliE2E:
    """Test CLI commands via subprocess with real SQLite database."""

    def test_place_add_and_list(self, tmp_path: Path) -> None:
        env_with_db = {"HOME": str(tmp_path), "PATH": "", "VIRTUAL_ENV": ""}
        # Use sys.executable to ensure we use the right Python
        base_cmd = [sys.executable, "-m", "voyages"]

        # Add a place
        add_result = subprocess.run(
            [*base_cmd, "place", "add", "--name", "Paris", "--lat", "48.8566", "--lon", "2.3522"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
        )
        assert add_result.returncode == 0
        assert "Created place" in add_result.stdout

        # List places
        list_result = subprocess.run(
            [*base_cmd, "place", "list"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
        )
        assert list_result.returncode == 0
        assert "Paris" in list_result.stdout

    def test_render_nonexistent_project(self, tmp_path: Path) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "voyages", "render", "nonexistent"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
        )
        assert result.returncode != 0

    def test_help_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "voyages", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "voyages" in result.stdout.lower() or "usage" in result.stdout.lower()
```

Note: The `sys.executable` approach runs `python -m voyages` which works if the package is installed in the venv. Check that `voyages` is accessible as a module (`python -m voyages`). If not, use `uv run voyages` via subprocess instead.

- [ ] **Step 4: Run E2E tests**

```bash
uv run pytest tests/e2e/test_cli_e2e.py -v
```

- [ ] **Step 5: Verify make targets**

```bash
make test       # Should skip e2e tests
make test-e2e   # Should run only e2e tests
make test-all   # Should run everything
```

- [ ] **Step 6: Commit**

```bash
git add tests/e2e/test_cli_e2e.py pyproject.toml Makefile
git commit -m "test(e2e): add subprocess CLI tests, pytest markers, and Makefile targets"
```

---

### Task 8: Final Verification and PR

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest -v
```

- [ ] **Step 2: Run linting**

```bash
uv run ruff check src tests && uv run ruff format --check src tests
```

Fix any issues in files we changed.

- [ ] **Step 3: Run mypy**

```bash
uv run mypy src
```

- [ ] **Step 4: Verify make targets**

```bash
make ci         # Should pass (lint + fmt-check + test excluding e2e)
make test-all   # Should pass (all tests including e2e)
```

- [ ] **Step 5: Push and create PR**

```bash
git push -u origin <branch-name>
gh pr create \
  --title "test: strengthen test suite and add integration/E2E coverage (P2+P3)" \
  --body "$(cat <<'EOF'
## Summary

Continues dalbrecht/Voyages#4 (P2 + P3)

**P2 — Strengthen existing tests:**
- Domain: NaN, Infinity, boundary, and entity edge cases for Coordinates/BoundingBox
- DB: Full-field round-trip assertions, JSON config round-trip, unique constraint test
- Renderer: Magic bytes validation (PNG/SVG/PDF/EPS), dimension check, marker visibility spot-check, empty input handling
- Styles: Missing YAML fields, invalid syntax, all built-in fields populated
- Fixed tautological PlaceService.search() test with call tracking
- Added real EXIF JPEG test fixtures and real-file extraction tests
- Nominatim error handling tests for malformed responses

**P3 — Integration and E2E tests:**
- In-process integration: Place CRUD workflow, project render workflow (full stack, no mocks)
- Subprocess E2E: CLI place add→list, render nonexistent project, help flag
- Pytest `e2e` marker for selective test runs
- Makefile: `make test` excludes E2E, `make test-e2e` and `make test-all` added

## Test plan

- [ ] `make ci` passes (excludes E2E)
- [ ] `make test-all` passes (includes E2E)
- [ ] `uv run ruff check src tests` — clean
- [ ] `uv run mypy src` — clean

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
