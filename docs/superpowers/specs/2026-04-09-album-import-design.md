# Album Import — macOS Photos to Voyages Map

**Date:** 2026-04-09
**Status:** Approved

## Purpose

An interactive CLI feature that reads photo albums from macOS Photos.app, clusters geotagged photos into logical stops, and creates a Voyages Project with places and a trip — ready for rendering via the existing workflow.

## Scope

- macOS only (depends on Photos.app library access)
- CLI-only feature (no web UI additions)
- Read-only access to Photos — no modifications to the user's library
- Output is a Voyages Project; rendering is handled by existing `voyages render`

## Architecture

New CLI command group + dedicated service, following the existing clean architecture.

```
cli/album_commands.py  →  application/album_service.py  →  infrastructure/photos/osxphotos_adapter.py
                                   ↓
                         application/place_service.py (create places)
                         application/trip_service.py (create trip)
                         application/project_service.py (create project)
```

### New Files

| Layer | File | Responsibility |
|-------|------|----------------|
| Application | `application/clustering.py` | DBSCAN clustering logic, centroid computation |
| Application | `application/album_service.py` | Orchestrates album import: fetch → cluster → persist |
| Application | `application/interfaces.py` | Add `PhotosLibraryPort` protocol |
| Infrastructure | `infrastructure/photos/osxphotos_adapter.py` | `osxphotos` wrapper implementing `PhotosLibraryPort` |
| CLI | `cli/album_commands.py` | Typer sub-app with `list` and `import` commands |

### Layer Rules (unchanged)

- **Domain:** Zero external dependencies. New value objects only (no new domain logic for this feature).
- **Application:** `clustering.py` lives here since it depends on scikit-learn. `album_service.py` orchestrates existing services.
- **Infrastructure:** `osxphotos_adapter.py` is the only file that imports `osxphotos`.
- **CLI:** Thin wiring. Interactive picker lives here.

## Data Model

### New Value Objects

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
    representative_path: str  # photo closest to centroid
```

### Mapping to Existing Entities

- Each `PhotoCluster` → one `Place` (centroid coordinates, reverse-geocoded name)
- Ordered list of clusters → one `Trip` with `TripStop`s (ordered by earliest timestamp)
- Everything wired into one `Project` (map_type=ROUTE)

Individual photo coordinates are **not persisted**. Only cluster centroids become Places. Raw photo data stays in Photos.app.

## Clustering Logic

**Algorithm:** DBSCAN with haversine distance metric.

**Why DBSCAN:**
- No need to specify number of clusters upfront
- Finds natural density-based groups
- Handles variable spacing (walking a city vs. driving across a country)
- Labels outlier photos as noise

**Parameters:**
- `eps` — maximum distance between photos in a cluster, in kilometers. Default: `0.5` km.
- `min_samples` — minimum photos to form a cluster. Default: `1`.

Both are user-configurable via CLI flags.

**Process:**
1. Take all geotagged photos, sorted chronologically
2. Convert lat/lon to radians for haversine distance
3. Run DBSCAN → cluster labels
4. For each cluster: compute centroid (mean lat/lon), earliest/latest timestamp, pick representative photo (closest to centroid)
5. Noise points (label = -1): treat each as its own single-photo cluster — no photos silently dropped
6. Order clusters by earliest timestamp → trip stop order

**Function signature:**
```python
def cluster_photos(
    photos: Sequence[GeotaggedPhoto],
    eps_km: float = 0.5,
    min_samples: int = 1,
) -> list[PhotoCluster]:
```

Pure function. No side effects. Lives in the application layer since it depends on scikit-learn (domain layer requires zero external dependencies).

## CLI Interface

### Commands

```
voyages album list
```
Lists all albums from Photos.app with photo counts. Table output via `rich`.

```
voyages album import [ALBUM_NAME]
```
- If `ALBUM_NAME` provided, uses it directly (error if not found)
- If omitted, launches interactive arrow-key picker showing all albums
- After selection, runs the import pipeline

### Flags for `album import`

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--name` | TEXT | album title | Project name |
| `--eps` | FLOAT | 0.5 | Cluster radius in km |
| `--min-samples` | INT | 1 | Min photos per cluster |
| `--dry-run` | FLAG | false | Show what would be created without persisting |
| `--style` | TEXT | "default" | Map style to assign |

### Interactive Picker

Uses `questionary` for arrow-key navigation with search/filtering support. Displays album title and geotagged photo count.

### Example Session

```
$ voyages album import

  Select an album:
  ❯ Japan 2024 (347 photos)
    Iceland Road Trip (128 photos)
    Weekend in Austin (43 photos)
    Family Reunion (89 photos)

Selected: Japan 2024

Importing 347 photos...
  Geotagged: 312 / 347 (35 skipped — no GPS data)
  Clusters: 14 stops identified (eps=0.5km)
  Places created: 14
  Trip created: "Japan 2024"
  Project created: "Japan 2024" (ROUTE)

Done. Render with: voyages render "Japan 2024"
```

### Dry Run Output

Same summary plus a table of clusters:

| # | Name | Lat | Lon | Photos | Date Range |
|---|------|-----|-----|--------|------------|
| 1 | Shinjuku, Tokyo | 35.689 | 139.700 | 47 | 2024-03-15 – 2024-03-16 |
| 2 | Asakusa, Tokyo | 35.712 | 139.797 | 23 | 2024-03-16 – 2024-03-16 |
| ... | | | | | |

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Photos without GPS data | Skip silently, report count in summary |
| No geotagged photos in album | Abort: "No geotagged photos found in album 'X'. Nothing to import." |
| Duplicate project name | Prompt: "Project 'X' already exists. Overwrite? [y/N]" |
| Reverse geocoding failure | Fall back to coordinate label: "Stop 3 (35.68°N, 139.77°E)". Log warning. |
| osxphotos can't access library | "Could not access Photos library. Ensure Photos.app has been opened at least once." |
| Very large albums (>5k photos) | No special handling. DBSCAN is O(n²) worst case but fine for typical albums. Flag if it becomes an issue. |

## Dependencies

| Package | Purpose | Notes |
|---------|---------|-------|
| `osxphotos` | macOS Photos.app access | macOS only |
| `scikit-learn` | DBSCAN clustering | Standard ML library |
| `questionary` | Interactive arrow-key picker | Lightweight, works with Typer |

All added to `pyproject.toml` main dependencies.

## Testing Strategy

| Layer | Target | Approach |
|-------|--------|----------|
| Application | `clustering.py` | Unit tests with synthetic coordinates. No mocks. 100% coverage. Cases: single cluster, multiple clusters, noise points, all-noise, single photo, empty input. |
| Application | `album_service.py` | Unit tests with `PhotosLibraryPort` faked via protocol. Real SQLite repos (no DB mocking). Verify correct places/trips/projects created. 95%+ coverage. |
| Infrastructure | `osxphotos_adapter.py` | Integration tests, skipped in CI (`@pytest.mark.skipif(not sys.platform == "darwin")`). Requires real Photos library. |
| CLI | `album_commands.py` | Typer `CliRunner` tests with service faked. Test flag parsing, dry-run output, error messages. 95%+ coverage. |

Consistent with existing test patterns: no database mocking, real SQLite repos in tests.
