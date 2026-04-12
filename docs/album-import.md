# Album Import

Import photo albums from macOS Photos.app into Voyages as route map projects.

**Requires macOS.** The `album` command group is only available on macOS where Photos.app is installed.

## Quick Start

```bash
# List your Photos albums
voyages album list

# Import an album by name
voyages album import "Japan 2024"

# Or use the interactive picker
voyages album import
```

After import, render the map:

```bash
voyages render "Japan 2024" --format svg
```

## How It Works

1. **Reads** geotagged photos from a macOS Photos album via [osxphotos](https://github.com/RhetTbull/osxphotos)
2. **Sorts** photos chronologically
3. **Clusters** nearby photos into logical stops using DBSCAN (density-based spatial clustering with haversine distance)
4. **Creates** a Place for each cluster (reverse-geocoded via Nominatim)
5. **Creates** a Trip with ordered stops connecting the Places
6. **Creates** a Project (map type: ROUTE) referencing the Trip and Places

Photos without GPS data are silently skipped and reported in the summary.

## Commands

### `voyages album list`

Lists all user-created albums in your Photos library with photo counts.

```
$ voyages album list

         Photos Albums
  ┏━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
  ┃ # ┃ Title              ┃ Photos ┃
  ┡━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
  │ 1 │ Japan 2024         │    347 │
  │ 2 │ Iceland Road Trip  │    128 │
  │ 3 │ Weekend in Austin  │     43 │
  └───┴────────────────────┴────────┘
```

### `voyages album import [ALBUM_NAME]`

Import a Photos album as a Voyages route project.

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `ALBUM_NAME` | No | Album name to import. Omit for interactive picker. |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--name TEXT` | album title | Project name (overrides the album title) |
| `--eps FLOAT` | 0.5 | Cluster radius in kilometers |
| `--min-samples INT` | 1 | Minimum photos to form a cluster |
| `--dry-run` | false | Preview clusters without saving anything |
| `--style TEXT` | "default" | Map style to assign to the project |

**Example:**

```
$ voyages album import "Japan 2024"

Importing 347 photos...
  Geotagged: 312 / 347 (35 skipped — no GPS data)
  Clusters: 14 stops identified
  Places created: 14
  Trip created: "Japan 2024"
  Project created: "Japan 2024" (ROUTE)

Done. Render with: voyages render "Japan 2024"
```

## Clustering

Photos are grouped into stops using the [DBSCAN algorithm](https://en.wikipedia.org/wiki/DBSCAN) with haversine (great-circle) distance. This works well because:

- It doesn't require knowing the number of stops in advance
- It finds natural density-based groupings
- It adapts to mixed scales (walking around a city vs. driving between cities)

### Tuning the cluster radius

The `--eps` flag controls how close photos must be to belong to the same cluster (default: 0.5 km).

```bash
# Tight clusters — walking-distance stops (500m)
voyages album import "City Walk" --eps 0.5

# Loose clusters — neighborhood-level grouping (5km)
voyages album import "Road Trip" --eps 5.0

# Very loose — city-level grouping (50km)
voyages album import "Cross Country" --eps 50.0
```

### Preview with dry-run

Use `--dry-run` to see what clusters would be created without writing to the database:

```
$ voyages album import "Japan 2024" --dry-run --eps 2.0

[Dry run] Importing 347 photos...
  Geotagged: 312 / 347 (35 skipped — no GPS data)
  Clusters: 8 stops identified

        Clusters (preview)
  ┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
  ┃ # ┃ Name                  ┃
  ┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
  │ 1 │ Shinjuku, Tokyo       │
  │ 2 │ Asakusa, Tokyo        │
  │ 3 │ Hakone                │
  │ ...                       │
  └───┴───────────────────────┘
```

## Duplicate Projects

If a project with the same name already exists, the CLI prompts before overwriting:

```
$ voyages album import "Japan 2024"
Project 'Japan 2024' already exists. Overwrite? [y/N]:
```

Use `--name` to import under a different name:

```bash
voyages album import "Japan 2024" --name "Japan Trip v2"
```

## Architecture

The feature follows the Voyages clean architecture:

```
CLI (album_commands.py)
  └─ Application (album_service.py, clustering.py)
       ├─ PlaceService, TripService, ProjectService (existing)
       └─ Infrastructure (osxphotos_adapter.py)
            └─ osxphotos library → Photos.app database
```

- **Domain layer:** `AlbumSummary`, `GeotaggedPhoto`, `PhotoCluster` value objects
- **Application layer:** `AlbumService` orchestration, `cluster_photos()` pure function, `PhotosLibraryPort` protocol
- **Infrastructure layer:** `OsxPhotosAdapter` wraps osxphotos behind the protocol
- **CLI layer:** Thin Typer commands with `questionary` for interactive selection
