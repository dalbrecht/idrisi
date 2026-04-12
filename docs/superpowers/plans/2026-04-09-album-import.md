# Album Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import macOS Photos albums into Voyages as clustered route projects via an interactive CLI.

**Architecture:** New `voyages album` CLI command group backed by `AlbumService` (application layer) and `OsxPhotosAdapter` (infrastructure layer). Photos are fetched via `osxphotos`, sorted chronologically, clustered with DBSCAN, and persisted as Places/Trip/Project using existing services.

**Tech Stack:** osxphotos, scikit-learn (DBSCAN), questionary (interactive picker), existing Voyages stack (Typer, SQLAlchemy, Nominatim)

**Spec:** `docs/superpowers/specs/2026-04-09-album-import-design.md`

---

### Task 1: Add dependencies to pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add new dependencies**

Add `osxphotos`, `scikit-learn`, and `questionary` to the `dependencies` list in `pyproject.toml`:

```toml
dependencies = [
    "cartopy>=0.23",
    "fastapi>=0.115",
    "httpx>=0.27",
    "matplotlib>=3.9",
    "osxphotos>=0.68",
    "pillow>=10",
    "pydantic>=2.9",
    "pyyaml>=6",
    "questionary>=2.0",
    "scikit-learn>=1.5",
    "sqlalchemy>=2.0",
    "typer>=0.12",
    "uvicorn>=0.30",
]
```

Also add type stubs to `dev` dependencies:

```toml
[project.optional-dependencies]
dev = [
    "mypy>=1.11",
    "pytest>=8",
    "pytest-cov>=5",
    "ruff>=0.6",
    "types-Pillow",
    "types-PyYAML",
]
```

Add a mypy override for osxphotos (no type stubs available):

```toml
[[tool.mypy.overrides]]
module = [
    "cartopy.*",
    "matplotlib.*",
    "osxphotos.*",
    "questionary.*",
]
ignore_missing_imports = true
```

- [ ] **Step 2: Install dependencies**

Run: `uv sync`
Expected: All dependencies install successfully.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "build: add osxphotos, scikit-learn, questionary dependencies"
```

---

### Task 2: Add domain value objects

**Files:**
- Modify: `src/voyages/domain/value_objects.py`
- Test: `tests/domain/test_value_objects.py`

- [ ] **Step 1: Write failing tests for new value objects**

Append the following tests to `tests/domain/test_value_objects.py`:

```python
from datetime import UTC, datetime

from voyages.domain.value_objects import AlbumSummary, GeotaggedPhoto, PhotoCluster

TOKYO_LAT = 35.6762
TOKYO_LON = 139.6503
OSAKA_LAT = 34.6937
OSAKA_LON = 135.5023


class TestAlbumSummary:
    def test_create(self) -> None:
        album = AlbumSummary(id="abc123", title="Japan 2024", photo_count=347)
        assert album.id == "abc123"
        assert album.title == "Japan 2024"
        assert album.photo_count == 347

    def test_frozen(self) -> None:
        album = AlbumSummary(id="abc123", title="Japan 2024", photo_count=347)
        try:
            album.title = "Changed"  # type: ignore[misc]
            msg = "Should have raised"
            raise AssertionError(msg)
        except AttributeError:
            pass


class TestGeotaggedPhoto:
    def test_create(self) -> None:
        ts = datetime(2024, 3, 15, 10, 30, 0, tzinfo=UTC)
        photo = GeotaggedPhoto(
            latitude=TOKYO_LAT,
            longitude=TOKYO_LON,
            timestamp=ts,
            path="/photos/img1.jpg",
        )
        assert photo.latitude == TOKYO_LAT
        assert photo.longitude == TOKYO_LON
        assert photo.timestamp == ts
        assert photo.path == "/photos/img1.jpg"

    def test_frozen(self) -> None:
        ts = datetime(2024, 3, 15, 10, 30, 0, tzinfo=UTC)
        photo = GeotaggedPhoto(
            latitude=TOKYO_LAT, longitude=TOKYO_LON, timestamp=ts, path="/p.jpg",
        )
        try:
            photo.latitude = 0.0  # type: ignore[misc]
            msg = "Should have raised"
            raise AssertionError(msg)
        except AttributeError:
            pass


class TestPhotoCluster:
    def test_create(self) -> None:
        early = datetime(2024, 3, 15, 9, 0, 0, tzinfo=UTC)
        late = datetime(2024, 3, 15, 17, 0, 0, tzinfo=UTC)
        cluster = PhotoCluster(
            centroid_lat=TOKYO_LAT,
            centroid_lon=TOKYO_LON,
            photo_count=47,
            earliest=early,
            latest=late,
            representative_path="/photos/best.jpg",
        )
        assert cluster.centroid_lat == TOKYO_LAT
        assert cluster.centroid_lon == TOKYO_LON
        assert cluster.photo_count == 47
        assert cluster.earliest == early
        assert cluster.latest == late
        assert cluster.representative_path == "/photos/best.jpg"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/domain/test_value_objects.py::TestAlbumSummary -v`
Expected: FAIL — `ImportError: cannot import name 'AlbumSummary'`

- [ ] **Step 3: Implement the value objects**

Add the following to the end of `src/voyages/domain/value_objects.py`:

```python
@dataclass(frozen=True)
class AlbumSummary:
    """Lightweight album metadata for the picker."""

    id: str
    title: str
    photo_count: int


@dataclass(frozen=True)
class GeotaggedPhoto:
    """A photo with location and time — intermediate type, not persisted."""

    latitude: float
    longitude: float
    timestamp: datetime
    path: str


@dataclass(frozen=True)
class PhotoCluster:
    """Result of clustering — a group of photos collapsed to one point."""

    centroid_lat: float
    centroid_lon: float
    photo_count: int
    earliest: datetime
    latest: datetime
    representative_path: str
```

Also add the `datetime` import at the top of the file. The file uses `from __future__ import annotations`, so add to the TYPE_CHECKING block:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/domain/test_value_objects.py::TestAlbumSummary tests/domain/test_value_objects.py::TestGeotaggedPhoto tests/domain/test_value_objects.py::TestPhotoCluster -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Run full domain test suite**

Run: `uv run pytest tests/domain/ -v`
Expected: All tests PASS (no regressions).

- [ ] **Step 6: Commit**

```bash
git add src/voyages/domain/value_objects.py tests/domain/test_value_objects.py
git commit -m "feat(domain): add AlbumSummary, GeotaggedPhoto, PhotoCluster value objects"
```

---

### Task 3: Add PhotosLibraryPort protocol

**Files:**
- Modify: `src/voyages/application/interfaces.py`

- [ ] **Step 1: Add the protocol**

Add the following to `src/voyages/application/interfaces.py`. The new types need to be imported in the `TYPE_CHECKING` block:

Update the existing `TYPE_CHECKING` block to include:

```python
if TYPE_CHECKING:
    from pathlib import Path
    from uuid import UUID

    from voyages.domain.entities import Photo, Place, Project, Region, Trip
    from voyages.domain.value_objects import (
        AlbumSummary,
        Coordinates,
        GeotaggedPhoto,
        OutputFormat,
    )
```

Then add at the end of the file:

```python
class PhotosLibraryPort(Protocol):
    """Protocol for accessing a photo library (e.g., macOS Photos.app)."""

    def list_albums(self) -> list[AlbumSummary]: ...

    def get_album_photos(self, album_id: str) -> list[GeotaggedPhoto]: ...
```

- [ ] **Step 2: Run lint to verify**

Run: `uv run ruff check src/voyages/application/interfaces.py`
Expected: No errors.

- [ ] **Step 3: Run mypy to verify**

Run: `uv run mypy src/voyages/application/interfaces.py`
Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add src/voyages/application/interfaces.py
git commit -m "feat(application): add PhotosLibraryPort protocol"
```

---

### Task 4: Implement clustering module

**Files:**
- Create: `src/voyages/application/clustering.py`
- Create: `tests/application/test_clustering.py`

- [ ] **Step 1: Write failing tests**

Create `tests/application/test_clustering.py`:

```python
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from voyages.application.clustering import cluster_photos
from voyages.domain.value_objects import GeotaggedPhoto, PhotoCluster

TOKYO_LAT = 35.6762
TOKYO_LON = 139.6503
SHINJUKU_LAT = 35.6938
SHINJUKU_LON = 139.7034
OSAKA_LAT = 34.6937
OSAKA_LON = 135.5023
KYOTO_LAT = 35.0116
KYOTO_LON = 135.7681
EXPECTED_TWO = 2
EXPECTED_THREE = 3


def _photo(lat: float, lon: float, hour: int = 10, day: int = 15) -> GeotaggedPhoto:
    """Helper to create a GeotaggedPhoto with minimal boilerplate."""
    return GeotaggedPhoto(
        latitude=lat,
        longitude=lon,
        timestamp=datetime(2024, 3, day, hour, 0, 0, tzinfo=UTC),
        path=f"/photos/{lat}_{lon}.jpg",
    )


class TestClusterPhotos:
    def test_empty_input(self) -> None:
        result = cluster_photos([])
        assert result == []

    def test_single_photo(self) -> None:
        photos = [_photo(TOKYO_LAT, TOKYO_LON)]
        result = cluster_photos(photos)
        assert len(result) == 1
        assert result[0].photo_count == 1
        assert result[0].centroid_lat == pytest.approx(TOKYO_LAT)
        assert result[0].centroid_lon == pytest.approx(TOKYO_LON)

    def test_two_nearby_photos_cluster_together(self) -> None:
        photos = [
            _photo(TOKYO_LAT, TOKYO_LON, hour=10),
            _photo(SHINJUKU_LAT, SHINJUKU_LON, hour=14),
        ]
        # Shinjuku is ~5km from central Tokyo — with a 10km eps they should cluster
        result = cluster_photos(photos, eps_km=10.0)
        assert len(result) == 1
        assert result[0].photo_count == EXPECTED_TWO

    def test_two_distant_photos_separate(self) -> None:
        photos = [
            _photo(TOKYO_LAT, TOKYO_LON, hour=10),
            _photo(OSAKA_LAT, OSAKA_LON, hour=14),
        ]
        # Tokyo to Osaka is ~400km — with default eps=0.5km they should be separate
        result = cluster_photos(photos, eps_km=0.5)
        assert len(result) == EXPECTED_TWO

    def test_clusters_ordered_by_earliest_timestamp(self) -> None:
        photos = [
            _photo(OSAKA_LAT, OSAKA_LON, hour=8, day=16),
            _photo(TOKYO_LAT, TOKYO_LON, hour=10, day=15),
        ]
        result = cluster_photos(photos, eps_km=0.5)
        assert len(result) == EXPECTED_TWO
        # Tokyo (day=15) should come first chronologically
        assert result[0].centroid_lat == pytest.approx(TOKYO_LAT)
        assert result[1].centroid_lat == pytest.approx(OSAKA_LAT)

    def test_centroid_is_mean_of_cluster(self) -> None:
        lat1, lon1 = 35.0, 139.0
        lat2, lon2 = 35.001, 139.001
        photos = [
            _photo(lat1, lon1, hour=10),
            _photo(lat2, lon2, hour=11),
        ]
        result = cluster_photos(photos, eps_km=1.0)
        assert len(result) == 1
        assert result[0].centroid_lat == pytest.approx((lat1 + lat2) / 2, abs=0.001)
        assert result[0].centroid_lon == pytest.approx((lon1 + lon2) / 2, abs=0.001)

    def test_earliest_and_latest_timestamps(self) -> None:
        early = datetime(2024, 3, 15, 8, 0, 0, tzinfo=UTC)
        late = datetime(2024, 3, 15, 18, 0, 0, tzinfo=UTC)
        photos = [
            GeotaggedPhoto(latitude=35.0, longitude=139.0, timestamp=early, path="/a.jpg"),
            GeotaggedPhoto(latitude=35.001, longitude=139.001, timestamp=late, path="/b.jpg"),
        ]
        result = cluster_photos(photos, eps_km=1.0)
        assert len(result) == 1
        assert result[0].earliest == early
        assert result[0].latest == late

    def test_representative_path_is_closest_to_centroid(self) -> None:
        photos = [
            _photo(35.0, 139.0, hour=10),
            _photo(35.0001, 139.0001, hour=11),  # closer to centroid
            _photo(35.002, 139.002, hour=12),
        ]
        result = cluster_photos(photos, eps_km=1.0)
        assert len(result) == 1
        # The middle photo is closest to the centroid
        assert result[0].representative_path == "/photos/35.0001_139.0001.jpg"

    def test_multiple_clusters_with_mixed_sizes(self) -> None:
        photos = [
            # Tokyo cluster (3 photos)
            _photo(TOKYO_LAT, TOKYO_LON, hour=9, day=15),
            _photo(TOKYO_LAT + 0.001, TOKYO_LON + 0.001, hour=10, day=15),
            _photo(TOKYO_LAT - 0.001, TOKYO_LON - 0.001, hour=11, day=15),
            # Osaka cluster (1 photo)
            _photo(OSAKA_LAT, OSAKA_LON, hour=15, day=16),
        ]
        result = cluster_photos(photos, eps_km=0.5)
        assert len(result) == EXPECTED_TWO
        assert result[0].photo_count == EXPECTED_THREE  # Tokyo
        assert result[1].photo_count == 1  # Osaka

    def test_min_samples_filters_noise_as_single_clusters(self) -> None:
        photos = [
            # Tight cluster (3 photos)
            _photo(35.0, 139.0, hour=10),
            _photo(35.0001, 139.0001, hour=11),
            _photo(35.0002, 139.0002, hour=12),
            # Isolated photo
            _photo(OSAKA_LAT, OSAKA_LON, hour=15),
        ]
        # With min_samples=1 (default), isolated photo becomes its own cluster
        result = cluster_photos(photos, eps_km=0.5, min_samples=1)
        assert len(result) == EXPECTED_TWO

    def test_custom_eps(self) -> None:
        photos = [
            _photo(TOKYO_LAT, TOKYO_LON, hour=10),
            _photo(SHINJUKU_LAT, SHINJUKU_LON, hour=14),
        ]
        # With small eps, they should be separate
        result_small = cluster_photos(photos, eps_km=0.1)
        assert len(result_small) == EXPECTED_TWO

        # With large eps, they should be together
        result_large = cluster_photos(photos, eps_km=10.0)
        assert len(result_large) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/application/test_clustering.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'voyages.application.clustering'`

- [ ] **Step 3: Implement the clustering module**

Create `src/voyages/application/clustering.py`:

```python
"""Photo clustering using DBSCAN with haversine distance."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

import numpy as np
from sklearn.cluster import DBSCAN

from voyages.domain.value_objects import PhotoCluster

if TYPE_CHECKING:
    from voyages.domain.value_objects import GeotaggedPhoto

_EARTH_RADIUS_KM = 6371.0


def cluster_photos(
    photos: Sequence[GeotaggedPhoto],
    eps_km: float = 0.5,
    min_samples: int = 1,
) -> list[PhotoCluster]:
    """Cluster geotagged photos by geographic proximity using DBSCAN.

    Photos are sorted chronologically first. Clusters are returned ordered
    by the earliest timestamp in each cluster. Noise points (if min_samples > 1)
    are treated as single-photo clusters.

    Args:
        photos: Sequence of geotagged photos to cluster.
        eps_km: Maximum distance in kilometers between photos in a cluster.
        min_samples: Minimum number of photos to form a dense cluster.

    Returns:
        List of PhotoCluster objects ordered by earliest timestamp.
    """
    if not photos:
        return []

    sorted_photos = sorted(photos, key=lambda p: p.timestamp)

    coords_rad = np.array(
        [[math.radians(p.latitude), math.radians(p.longitude)] for p in sorted_photos]
    )

    eps_rad = eps_km / _EARTH_RADIUS_KM

    db = DBSCAN(eps=eps_rad, min_samples=min_samples, metric="haversine")
    labels: np.ndarray = db.fit_predict(coords_rad)

    clusters: dict[int, list[int]] = {}
    for idx, label in enumerate(labels):
        label_int = int(label)
        if label_int == -1:
            noise_key = -(idx + 2)
            clusters[noise_key] = [idx]
        else:
            clusters.setdefault(label_int, []).append(idx)

    result: list[PhotoCluster] = []
    for indices in clusters.values():
        cluster_photos_list = [sorted_photos[i] for i in indices]
        centroid_lat = sum(p.latitude for p in cluster_photos_list) / len(cluster_photos_list)
        centroid_lon = sum(p.longitude for p in cluster_photos_list) / len(cluster_photos_list)
        earliest = min(p.timestamp for p in cluster_photos_list)
        latest = max(p.timestamp for p in cluster_photos_list)

        closest_idx = min(
            range(len(cluster_photos_list)),
            key=lambda i: (
                (cluster_photos_list[i].latitude - centroid_lat) ** 2
                + (cluster_photos_list[i].longitude - centroid_lon) ** 2
            ),
        )
        representative_path = cluster_photos_list[closest_idx].path

        result.append(
            PhotoCluster(
                centroid_lat=centroid_lat,
                centroid_lon=centroid_lon,
                photo_count=len(cluster_photos_list),
                earliest=earliest,
                latest=latest,
                representative_path=representative_path,
            )
        )

    result.sort(key=lambda c: c.earliest)
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/application/test_clustering.py -v`
Expected: All 12 tests PASS.

- [ ] **Step 5: Run lint and type check**

Run: `uv run ruff check src/voyages/application/clustering.py && uv run mypy src/voyages/application/clustering.py`
Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add src/voyages/application/clustering.py tests/application/test_clustering.py
git commit -m "feat(application): add DBSCAN photo clustering module"
```

---

### Task 5: Implement OsxPhotosAdapter

**Files:**
- Create: `src/voyages/infrastructure/photos/__init__.py`
- Create: `src/voyages/infrastructure/photos/osxphotos_adapter.py`
- Create: `tests/infrastructure/test_osxphotos_adapter.py`

- [ ] **Step 1: Create the package init file**

Create an empty `src/voyages/infrastructure/photos/__init__.py`:

```python
```

- [ ] **Step 2: Write the integration test (skipped on non-macOS)**

Create `tests/infrastructure/test_osxphotos_adapter.py`:

```python
"""Integration tests for OsxPhotosAdapter.

These tests require macOS with a Photos library and are skipped in CI.
"""

from __future__ import annotations

import sys

import pytest

from voyages.infrastructure.photos.osxphotos_adapter import OsxPhotosAdapter

pytestmark = pytest.mark.skipif(
    sys.platform != "darwin",
    reason="macOS Photos.app required",
)


class TestOsxPhotosAdapter:
    def setup_method(self) -> None:
        self.adapter = OsxPhotosAdapter()

    def test_list_albums_returns_list(self) -> None:
        albums = self.adapter.list_albums()
        assert isinstance(albums, list)

    def test_list_albums_entries_have_required_fields(self) -> None:
        albums = self.adapter.list_albums()
        if not albums:
            pytest.skip("No albums in Photos library")
        album = albums[0]
        assert isinstance(album.id, str)
        assert isinstance(album.title, str)
        assert isinstance(album.photo_count, int)

    def test_get_album_photos_nonexistent_returns_empty(self) -> None:
        photos = self.adapter.get_album_photos("nonexistent-album-id-xyz")
        assert photos == []

    def test_get_album_photos_returns_geotagged_only(self) -> None:
        albums = self.adapter.list_albums()
        if not albums:
            pytest.skip("No albums in Photos library")
        photos = self.adapter.get_album_photos(albums[0].id)
        for photo in photos:
            assert photo.latitude is not None
            assert photo.longitude is not None
            assert photo.timestamp is not None
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/infrastructure/test_osxphotos_adapter.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'voyages.infrastructure.photos'`

- [ ] **Step 4: Implement the adapter**

Create `src/voyages/infrastructure/photos/osxphotos_adapter.py`:

```python
"""macOS Photos.app adapter using osxphotos."""

from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING

import osxphotos

from voyages.domain.value_objects import AlbumSummary, GeotaggedPhoto

if TYPE_CHECKING:
    pass


class OsxPhotosAdapter:
    """Reads albums and geotagged photos from the macOS Photos library."""

    def __init__(self) -> None:
        self._db: osxphotos.PhotosDB | None = None

    def _get_db(self) -> osxphotos.PhotosDB:
        if self._db is None:
            self._db = osxphotos.PhotosDB()
        return self._db

    def list_albums(self) -> list[AlbumSummary]:
        """Return all user-created albums with photo counts."""
        db = self._get_db()
        album_names: list[str] = db.album_info
        results: list[AlbumSummary] = []
        for album in album_names:
            results.append(
                AlbumSummary(
                    id=album.uuid,
                    title=album.title,
                    photo_count=len(album.photos),
                )
            )
        return results

    def get_album_photos(self, album_id: str) -> list[GeotaggedPhoto]:
        """Return geotagged photos from the specified album.

        Only photos with valid GPS coordinates and timestamps are included.

        Args:
            album_id: The UUID of the album to read.

        Returns:
            List of GeotaggedPhoto objects, filtered to those with GPS data.
        """
        db = self._get_db()
        albums = [a for a in db.album_info if a.uuid == album_id]
        if not albums:
            return []

        album = albums[0]
        results: list[GeotaggedPhoto] = []

        for photo in album.photos:
            location = photo.location
            if location is None or location == (None, None):
                continue

            lat, lon = location
            if lat is None or lon is None:
                continue

            taken_at = photo.date
            if taken_at is None:
                continue

            if taken_at.tzinfo is None:
                taken_at = taken_at.replace(tzinfo=UTC)

            results.append(
                GeotaggedPhoto(
                    latitude=float(lat),
                    longitude=float(lon),
                    timestamp=taken_at,
                    path=str(photo.original_filename),
                )
            )

        return results
```

- [ ] **Step 5: Run tests**

Run: `uv run pytest tests/infrastructure/test_osxphotos_adapter.py -v`
Expected: Tests PASS (or are skipped if no Photos library available).

- [ ] **Step 6: Run lint**

Run: `uv run ruff check src/voyages/infrastructure/photos/osxphotos_adapter.py`
Expected: No errors.

- [ ] **Step 7: Commit**

```bash
git add src/voyages/infrastructure/photos/__init__.py src/voyages/infrastructure/photos/osxphotos_adapter.py tests/infrastructure/test_osxphotos_adapter.py
git commit -m "feat(infrastructure): add OsxPhotosAdapter for macOS Photos.app"
```

---

### Task 6: Implement AlbumService

**Files:**
- Create: `src/voyages/application/album_service.py`
- Create: `tests/application/test_album_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/application/test_album_service.py`:

```python
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from voyages.application.album_service import AlbumImportResult, AlbumService
from voyages.domain.entities import Place, Trip
from voyages.domain.value_objects import AlbumSummary, GeotaggedPhoto, MapType

if TYPE_CHECKING:
    from voyages.domain.value_objects import Coordinates

TOKYO_LAT = 35.6762
TOKYO_LON = 139.6503
OSAKA_LAT = 34.6937
OSAKA_LON = 135.5023
EXPECTED_TWO = 2
EXPECTED_THREE = 3
EXPECTED_FOURTEEN = 14


class FakePhotosLibrary:
    def __init__(
        self,
        albums: list[AlbumSummary] | None = None,
        photos: dict[str, list[GeotaggedPhoto]] | None = None,
    ) -> None:
        self._albums = albums or []
        self._photos = photos or {}

    def list_albums(self) -> list[AlbumSummary]:
        return list(self._albums)

    def get_album_photos(self, album_id: str) -> list[GeotaggedPhoto]:
        return list(self._photos.get(album_id, []))


class FakePlaceRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Place] = {}

    def get(self, place_id: uuid.UUID) -> Place | None:
        return self._store.get(place_id)

    def list_all(self) -> list[Place]:
        return list(self._store.values())

    def search_by_name(self, query: str) -> list[Place]:
        return []

    def save(self, place: Place) -> Place:
        self._store[place.id] = place
        return place

    def delete(self, place_id: uuid.UUID) -> None:
        self._store.pop(place_id, None)


class FakeTripRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Trip] = {}

    def get(self, trip_id: uuid.UUID) -> Trip | None:
        return self._store.get(trip_id)

    def list_all(self) -> list[Trip]:
        return list(self._store.values())

    def save(self, trip: Trip) -> Trip:
        self._store[trip.id] = trip
        return trip

    def delete(self, trip_id: uuid.UUID) -> None:
        self._store.pop(trip_id, None)


class FakeProjectRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, object] = {}
        self._by_name: dict[str, object] = {}

    def get(self, project_id: uuid.UUID) -> object | None:
        return self._store.get(project_id)

    def get_by_name(self, name: str) -> object | None:
        return self._by_name.get(name)

    def list_all(self) -> list[object]:
        return list(self._store.values())

    def save(self, project: object) -> object:
        self._store[project.id] = project  # type: ignore[union-attr]
        self._by_name[project.name] = project  # type: ignore[union-attr]
        return project

    def delete(self, project_id: uuid.UUID) -> None:
        self._store.pop(project_id, None)


class FakeGeocodingService:
    def __init__(self) -> None:
        self._call_count = 0

    def search(self, query: str) -> list[Place]:
        return []

    def reverse_geocode(self, coords: Coordinates) -> Place | None:
        self._call_count += 1
        return Place(
            id=uuid.uuid4(),
            name=f"Place {self._call_count}",
            latitude=coords.latitude,
            longitude=coords.longitude,
            source="nominatim",
            country="Japan",
        )


class FailingGeocodingService:
    def search(self, query: str) -> list[Place]:
        return []

    def reverse_geocode(self, coords: Coordinates) -> Place | None:
        return None


def _make_service(
    photos_lib: FakePhotosLibrary | None = None,
    geocoding: FakeGeocodingService | FailingGeocodingService | None = None,
) -> tuple[AlbumService, FakePlaceRepository, FakeTripRepository, FakeProjectRepository]:
    place_repo = FakePlaceRepository()
    trip_repo = FakeTripRepository()
    project_repo = FakeProjectRepository()
    geo = geocoding or FakeGeocodingService()
    lib = photos_lib or FakePhotosLibrary()

    from voyages.application.place_service import PlaceService
    from voyages.application.project_service import ProjectService
    from voyages.application.trip_service import TripService

    place_svc = PlaceService(place_repo=place_repo, geocoding=geo)
    trip_svc = TripService(trip_repo=trip_repo)
    project_svc = ProjectService(project_repo=project_repo)

    svc = AlbumService(
        photos_library=lib,
        place_service=place_svc,
        trip_service=trip_svc,
        project_service=project_svc,
        geocoding=geo,
    )
    return svc, place_repo, trip_repo, project_repo


def _sample_photos(album_id: str = "abc") -> tuple[FakePhotosLibrary, str]:
    photos = [
        GeotaggedPhoto(
            latitude=TOKYO_LAT,
            longitude=TOKYO_LON,
            timestamp=datetime(2024, 3, 15, 10, 0, 0, tzinfo=UTC),
            path="/photos/tokyo1.jpg",
        ),
        GeotaggedPhoto(
            latitude=TOKYO_LAT + 0.001,
            longitude=TOKYO_LON + 0.001,
            timestamp=datetime(2024, 3, 15, 14, 0, 0, tzinfo=UTC),
            path="/photos/tokyo2.jpg",
        ),
        GeotaggedPhoto(
            latitude=OSAKA_LAT,
            longitude=OSAKA_LON,
            timestamp=datetime(2024, 3, 16, 10, 0, 0, tzinfo=UTC),
            path="/photos/osaka1.jpg",
        ),
    ]
    albums = [AlbumSummary(id=album_id, title="Japan 2024", photo_count=3)]
    lib = FakePhotosLibrary(albums=albums, photos={album_id: photos})
    return lib, album_id


class TestAlbumServiceListAlbums:
    def test_list_albums(self) -> None:
        albums = [
            AlbumSummary(id="a1", title="Japan", photo_count=100),
            AlbumSummary(id="a2", title="Iceland", photo_count=50),
        ]
        lib = FakePhotosLibrary(albums=albums)
        svc, *_ = _make_service(photos_lib=lib)
        result = svc.list_albums()
        assert len(result) == EXPECTED_TWO
        assert result[0].title == "Japan"

    def test_list_albums_empty(self) -> None:
        svc, *_ = _make_service()
        result = svc.list_albums()
        assert result == []


class TestAlbumServiceImport:
    def test_import_creates_places_for_each_cluster(self) -> None:
        lib, album_id = _sample_photos()
        svc, place_repo, _, _ = _make_service(photos_lib=lib)
        result = svc.import_album(album_id=album_id, project_name="Japan 2024")
        assert len(place_repo.list_all()) == EXPECTED_TWO  # Tokyo cluster + Osaka

    def test_import_creates_trip_with_ordered_stops(self) -> None:
        lib, album_id = _sample_photos()
        svc, _, trip_repo, _ = _make_service(photos_lib=lib)
        result = svc.import_album(album_id=album_id, project_name="Japan 2024")
        trips = trip_repo.list_all()
        assert len(trips) == 1
        trip = trips[0]
        assert trip.name == "Japan 2024"
        assert len(trip.stops) == EXPECTED_TWO
        assert trip.stops[0].position == 0
        assert trip.stops[1].position == 1

    def test_import_creates_route_project(self) -> None:
        lib, album_id = _sample_photos()
        svc, _, _, project_repo = _make_service(photos_lib=lib)
        result = svc.import_album(album_id=album_id, project_name="Japan 2024")
        projects = project_repo.list_all()
        assert len(projects) == 1
        project = projects[0]
        assert project.name == "Japan 2024"
        assert project.map_type == MapType.ROUTE

    def test_import_returns_result(self) -> None:
        lib, album_id = _sample_photos()
        svc, *_ = _make_service(photos_lib=lib)
        result = svc.import_album(album_id=album_id, project_name="Japan 2024")
        assert isinstance(result, AlbumImportResult)
        assert result.total_photos == EXPECTED_THREE
        assert result.geotagged_photos == EXPECTED_THREE
        assert result.cluster_count == EXPECTED_TWO
        assert result.project_name == "Japan 2024"

    def test_import_with_custom_eps(self) -> None:
        lib, album_id = _sample_photos()
        svc, place_repo, _, _ = _make_service(photos_lib=lib)
        # With a huge eps, all 3 photos should cluster into 1
        result = svc.import_album(
            album_id=album_id, project_name="Japan 2024", eps_km=500.0,
        )
        assert result.cluster_count == 1
        assert len(place_repo.list_all()) == 1

    def test_import_empty_album(self) -> None:
        lib = FakePhotosLibrary(
            albums=[AlbumSummary(id="empty", title="Empty", photo_count=0)],
            photos={"empty": []},
        )
        svc, *_ = _make_service(photos_lib=lib)
        with pytest.raises(ValueError, match="No geotagged photos"):
            svc.import_album(album_id="empty", project_name="Empty")

    def test_import_geocoding_failure_uses_coordinate_label(self) -> None:
        lib, album_id = _sample_photos()
        svc, place_repo, _, _ = _make_service(
            photos_lib=lib, geocoding=FailingGeocodingService(),
        )
        result = svc.import_album(album_id=album_id, project_name="Japan 2024")
        places = place_repo.list_all()
        # Should have coordinate-based names like "Stop 1 (35.68°N, 139.65°E)"
        assert all("°N" in p.name or "°S" in p.name for p in places)

    def test_import_project_has_trip_and_place_ids(self) -> None:
        lib, album_id = _sample_photos()
        svc, place_repo, trip_repo, project_repo = _make_service(photos_lib=lib)
        result = svc.import_album(album_id=album_id, project_name="Japan 2024")
        projects = project_repo.list_all()
        project = projects[0]
        assert len(project.trip_ids) == 1
        assert len(project.place_ids) == EXPECTED_TWO
        trips = trip_repo.list_all()
        assert project.trip_ids[0] == trips[0].id
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/application/test_album_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'voyages.application.album_service'`

- [ ] **Step 3: Implement AlbumService**

Create `src/voyages/application/album_service.py`:

```python
"""Service for importing macOS Photos albums into Voyages projects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from voyages.application.clustering import cluster_photos
from voyages.domain.value_objects import Coordinates, MapType

if TYPE_CHECKING:
    from uuid import UUID

    from voyages.application.interfaces import GeocodingService, PhotosLibraryPort
    from voyages.application.place_service import PlaceService
    from voyages.application.project_service import ProjectService
    from voyages.application.trip_service import TripService
    from voyages.domain.entities import Project
    from voyages.domain.value_objects import AlbumSummary, PhotoCluster


@dataclass
class AlbumImportResult:
    """Summary of an album import operation."""

    project_name: str
    total_photos: int
    geotagged_photos: int
    cluster_count: int
    place_names: list[str]


class AlbumService:
    """Orchestrates importing a Photos album into a Voyages project."""

    def __init__(
        self,
        photos_library: PhotosLibraryPort,
        place_service: PlaceService,
        trip_service: TripService,
        project_service: ProjectService,
        geocoding: GeocodingService,
    ) -> None:
        self._photos_library = photos_library
        self._place_service = place_service
        self._trip_service = trip_service
        self._project_service = project_service
        self._geocoding = geocoding

    def list_albums(self) -> list[AlbumSummary]:
        """Return all albums from the photos library."""
        return self._photos_library.list_albums()

    def get_project_by_name(self, name: str) -> Project | None:
        """Check if a project with the given name already exists."""
        return self._project_service.get_by_name(name)

    def delete_project(self, project_id: UUID) -> None:
        """Delete a project by ID."""
        self._project_service.delete(project_id)

    def import_album(
        self,
        album_id: str,
        project_name: str,
        eps_km: float = 0.5,
        min_samples: int = 1,
        style: str = "default",
    ) -> AlbumImportResult:
        """Import an album as a Voyages project.

        Fetches geotagged photos, clusters them, creates Places and a Trip,
        then wires everything into a new Project.

        Args:
            album_id: The album identifier to import.
            project_name: Name for the created project.
            eps_km: DBSCAN cluster radius in kilometers.
            min_samples: Minimum photos per cluster.

        Returns:
            AlbumImportResult with summary statistics.

        Raises:
            ValueError: If the album has no geotagged photos.
        """
        photos = self._photos_library.get_album_photos(album_id)
        total_photos = len(photos)

        if not photos:
            msg = f"No geotagged photos found in album. Nothing to import."
            raise ValueError(msg)

        clusters = cluster_photos(photos, eps_km=eps_km, min_samples=min_samples)

        place_names: list[str] = []
        place_ids = []

        for i, cluster in enumerate(clusters):
            name = self._name_cluster(cluster, i + 1)
            place_names.append(name)
            place = self._place_service.create(
                name=name,
                lat=cluster.centroid_lat,
                lon=cluster.centroid_lon,
                source="photos-album",
            )
            place_ids.append(place.id)

        trip = self._trip_service.create(
            name=project_name,
            start_date=clusters[0].earliest.date() if clusters else None,
            end_date=clusters[-1].latest.date() if clusters else None,
        )

        for position, pid in enumerate(place_ids):
            self._trip_service.add_stop(
                trip_id=trip.id,
                place_id=pid,
                arrived_at=clusters[position].earliest,
                departed_at=clusters[position].latest,
            )

        project = self._project_service.create(
            name=project_name,
            map_type=MapType.ROUTE,
            description=f"Imported from Photos album ({total_photos} photos, {len(clusters)} stops)",
            config={"style": style},
        )

        for pid in place_ids:
            self._project_service.add_place(project.id, pid)
        self._project_service.add_trip(project.id, trip.id)

        return AlbumImportResult(
            project_name=project_name,
            total_photos=total_photos,
            geotagged_photos=total_photos,
            cluster_count=len(clusters),
            place_names=place_names,
        )

    def _name_cluster(self, cluster: PhotoCluster, position: int) -> str:
        """Attempt to reverse-geocode a cluster centroid, falling back to coordinates."""
        coords = Coordinates(latitude=cluster.centroid_lat, longitude=cluster.centroid_lon)
        place = self._geocoding.reverse_geocode(coords)
        if place is not None:
            return place.name

        lat = cluster.centroid_lat
        lon = cluster.centroid_lon
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        return f"Stop {position} ({abs(lat):.2f}\u00b0{lat_dir}, {abs(lon):.2f}\u00b0{lon_dir})"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/application/test_album_service.py -v`
Expected: All 9 tests PASS.

- [ ] **Step 5: Run lint and type check**

Run: `uv run ruff check src/voyages/application/album_service.py && uv run mypy src/voyages/application/album_service.py`
Expected: No errors.

- [ ] **Step 6: Commit**

```bash
git add src/voyages/application/album_service.py tests/application/test_album_service.py
git commit -m "feat(application): add AlbumService for album-to-project import"
```

---

### Task 7: Implement album CLI commands

**Files:**
- Create: `src/voyages/cli/album_commands.py`
- Create: `tests/cli/test_cli_album.py`
- Modify: `src/voyages/cli/__init__.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/test_cli_album.py`:

```python
"""Tests for the album CLI commands."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from voyages.application.album_service import AlbumImportResult
from voyages.cli import app
from voyages.domain.value_objects import AlbumSummary

runner = CliRunner()

EXPECTED_TWO = 2


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_list(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
        AlbumSummary(id="a2", title="Iceland", photo_count=128),
    ]
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "list"])
    assert result.exit_code == 0
    assert "Japan 2024" in result.output
    assert "347" in result.output
    assert "Iceland" in result.output
    assert "128" in result.output


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_list_empty(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = []
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "list"])
    assert result.exit_code == 0
    assert "No albums" in result.output


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_by_name(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.get_project_by_name.return_value = None
    svc.import_album.return_value = AlbumImportResult(
        project_name="Japan 2024",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=14,
        place_names=[f"Place {i}" for i in range(14)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024"])
    assert result.exit_code == 0
    assert "Japan 2024" in result.output
    assert "14" in result.output
    svc.import_album.assert_called_once()


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_not_found(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Nonexistent Album"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_dry_run(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.import_album.return_value = AlbumImportResult(
        project_name="Japan 2024",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=14,
        place_names=[f"Place {i}" for i in range(14)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output.lower() or "Dry run" in result.output


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_custom_eps(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.get_project_by_name.return_value = None
    svc.import_album.return_value = AlbumImportResult(
        project_name="Japan 2024",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=5,
        place_names=[f"Place {i}" for i in range(5)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024", "--eps", "2.0"])
    assert result.exit_code == 0
    svc.import_album.assert_called_once()
    call_kwargs = svc.import_album.call_args
    assert call_kwargs.kwargs.get("eps_km") == 2.0 or call_kwargs[1].get("eps_km") == 2.0


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_custom_name(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.get_project_by_name.return_value = None
    svc.import_album.return_value = AlbumImportResult(
        project_name="My Japan Trip",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=14,
        place_names=[f"Place {i}" for i in range(14)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024", "--name", "My Japan Trip"])
    assert result.exit_code == 0
    call_kwargs = svc.import_album.call_args
    assert (
        call_kwargs.kwargs.get("project_name") == "My Japan Trip"
        or call_kwargs[1].get("project_name") == "My Japan Trip"
    )


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_style_flag(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.get_project_by_name.return_value = None
    svc.import_album.return_value = AlbumImportResult(
        project_name="Japan 2024",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=14,
        place_names=[f"Place {i}" for i in range(14)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024", "--style", "dark"])
    assert result.exit_code == 0
    call_kwargs = svc.import_album.call_args
    assert call_kwargs.kwargs.get("style") == "dark" or call_kwargs[1].get("style") == "dark"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/cli/test_cli_album.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'voyages.cli.album_commands'`

- [ ] **Step 3: Implement album CLI commands**

Create `src/voyages/cli/album_commands.py`:

```python
"""CLI commands for macOS Photos album import."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from voyages.application.album_service import AlbumImportResult, AlbumService
from voyages.application.place_service import PlaceService
from voyages.application.project_service import ProjectService
from voyages.application.trip_service import TripService
from voyages.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlProjectRepository,
    SqlTripRepository,
)
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.geocoding.nominatim import NominatimGeocodingService
from voyages.infrastructure.photos.osxphotos_adapter import OsxPhotosAdapter

album_app = typer.Typer(name="album", help="Import from macOS Photos albums.", no_args_is_help=True)

console = Console()

_DB_URL = "sqlite:///voyages.db"


def get_album_dependencies() -> AlbumService:
    """Create an AlbumService wired to the default SQLite database."""
    engine = create_engine_and_tables(_DB_URL)
    session = get_session(engine)
    place_repo = SqlPlaceRepository(session)
    trip_repo = SqlTripRepository(session)
    project_repo = SqlProjectRepository(session)
    geocoding = NominatimGeocodingService()
    photos_library = OsxPhotosAdapter()

    place_svc = PlaceService(place_repo=place_repo, geocoding=geocoding)
    trip_svc = TripService(trip_repo=trip_repo)
    project_svc = ProjectService(project_repo=project_repo)

    return AlbumService(
        photos_library=photos_library,
        place_service=place_svc,
        trip_service=trip_svc,
        project_service=project_svc,
        geocoding=geocoding,
    )


@album_app.command(name="list")
def list_albums() -> None:
    """List all albums in the macOS Photos library."""
    svc = get_album_dependencies()
    albums = svc.list_albums()

    if not albums:
        console.print("No albums found in Photos library.")
        return

    table = Table(title="Photos Albums")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Photos", justify="right")

    for i, album in enumerate(albums, 1):
        table.add_row(str(i), album.title, str(album.photo_count))

    console.print(table)


@album_app.command(name="import")
def import_album(
    album_name: str | None = typer.Argument(None, help="Album name to import. Omit for interactive picker."),
    name: str | None = typer.Option(None, "--name", help="Project name (defaults to album title)."),
    eps: float = typer.Option(0.5, "--eps", help="Cluster radius in kilometers."),
    min_samples: int = typer.Option(1, "--min-samples", help="Minimum photos per cluster."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without saving."),
    style: str = typer.Option("default", "--style", help="Map style to assign to the project."),
) -> None:
    """Import a Photos album as a Voyages route project."""
    svc = get_album_dependencies()
    albums = svc.list_albums()

    if not albums:
        console.print("No albums found in Photos library.")
        raise typer.Exit(code=1)

    if album_name is not None:
        matched = [a for a in albums if a.title == album_name]
        if not matched:
            console.print(f"Album '{album_name}' not found.")
            raise typer.Exit(code=1)
        selected = matched[0]
    else:
        import questionary

        choices = [
            questionary.Choice(
                title=f"{a.title} ({a.photo_count} photos)",
                value=a,
            )
            for a in albums
        ]
        selected = questionary.select(
            "Select an album:",
            choices=choices,
        ).ask()

        if selected is None:
            raise typer.Exit(code=0)

    project_name = name or selected.title

    # Check for duplicate project name
    existing = svc.get_project_by_name(project_name)
    if existing is not None and not dry_run:
        overwrite = typer.confirm(f"Project '{project_name}' already exists. Overwrite?", default=False)
        if not overwrite:
            raise typer.Exit(code=0)
        svc.delete_project(existing.id)

    if dry_run:
        console.print(f"[Dry run] Would import album '{selected.title}' as project '{project_name}'")
        console.print(f"  Album photos: {selected.photo_count}")
        console.print(f"  Cluster radius: {eps} km")
        console.print(f"  Min samples: {min_samples}")

        result = svc.import_album(
            album_id=selected.id,
            project_name=project_name,
            eps_km=eps,
            min_samples=min_samples,
            style=style,
        )
        _print_result(result, dry_run=True)
        return

    result = svc.import_album(
        album_id=selected.id,
        project_name=project_name,
        eps_km=eps,
        min_samples=min_samples,
        style=style,
    )
    _print_result(result)


def _print_result(result: AlbumImportResult, *, dry_run: bool = False) -> None:
    """Print the import result summary."""
    prefix = "[Dry run] " if dry_run else ""

    console.print()
    console.print(f"{prefix}Importing {result.total_photos} photos...")
    console.print(f"  Geotagged: {result.geotagged_photos} / {result.total_photos}")
    console.print(f"  Clusters: {result.cluster_count} stops identified")

    if not dry_run:
        console.print(f"  Places created: {result.cluster_count}")
        console.print(f"  Trip created: \"{result.project_name}\"")
        console.print(f"  Project created: \"{result.project_name}\" (ROUTE)")
        console.print()
        console.print(f"Done. Render with: voyages render \"{result.project_name}\"")
    else:
        console.print()
        table = Table(title="Clusters (preview)")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Name", style="bold")

        for i, pname in enumerate(result.place_names, 1):
            table.add_row(str(i), pname)

        console.print(table)
```

- [ ] **Step 4: Register the album sub-app in cli/__init__.py**

Modify `src/voyages/cli/__init__.py` to add the album_app import and registration:

```python
"""Voyages CLI — Typer-based command-line interface."""

from __future__ import annotations

import typer

from voyages.cli.album_commands import album_app
from voyages.cli.import_commands import import_app
from voyages.cli.place_commands import place_app
from voyages.cli.project_commands import project_app
from voyages.cli.render_commands import render
from voyages.cli.serve_command import serve
from voyages.cli.trip_commands import trip_app

app = typer.Typer(
    name="voyages",
    help="A Python map generation toolbox for travel cartography.",
    no_args_is_help=True,
)

# Register sub-apps
app.add_typer(album_app)
app.add_typer(place_app)
app.add_typer(project_app)
app.add_typer(trip_app)
app.add_typer(import_app)

# Register top-level commands
app.command()(serve)
app.command()(render)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/cli/test_cli_album.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 6: Run the full test suite**

Run: `uv run pytest -v`
Expected: All tests PASS (no regressions).

- [ ] **Step 7: Run lint and type check**

Run: `uv run ruff check src/voyages/cli/album_commands.py && uv run mypy src/voyages/cli/album_commands.py`
Expected: No errors (or only pre-existing warnings).

- [ ] **Step 8: Commit**

```bash
git add src/voyages/cli/album_commands.py src/voyages/cli/__init__.py tests/cli/test_cli_album.py
git commit -m "feat(cli): add album list and import commands"
```

---

### Task 8: Integration smoke test

**Files:**
- Modify: `tests/e2e/test_smoke.py`

- [ ] **Step 1: Check existing smoke test**

Read `tests/e2e/test_smoke.py` to understand the current pattern.

- [ ] **Step 2: Add album CLI smoke test**

Append to `tests/e2e/test_smoke.py`:

```python
def test_album_help() -> None:
    result = runner.invoke(app, ["album", "--help"])
    assert result.exit_code == 0
    assert "album" in result.output.lower()


def test_album_list_help() -> None:
    result = runner.invoke(app, ["album", "list", "--help"])
    assert result.exit_code == 0


def test_album_import_help() -> None:
    result = runner.invoke(app, ["album", "import", "--help"])
    assert result.exit_code == 0
    assert "--eps" in result.output
    assert "--dry-run" in result.output
    assert "--name" in result.output
    assert "--min-samples" in result.output
    assert "--style" in result.output
```

If the smoke test file uses `CliRunner` and imports `app`, match that pattern. If it uses a different approach, adapt accordingly.

- [ ] **Step 3: Run smoke tests**

Run: `uv run pytest tests/e2e/ -v`
Expected: All tests PASS.

- [ ] **Step 4: Run full test suite with coverage**

Run: `uv run pytest --cov=voyages --cov-report=term-missing -v`
Expected: All tests PASS. New modules should show good coverage.

- [ ] **Step 5: Run full lint pipeline**

Run: `make ci`
Expected: Lint, format check, and tests all pass.

- [ ] **Step 6: Commit**

```bash
git add tests/e2e/test_smoke.py
git commit -m "test(e2e): add album CLI smoke tests"
```
