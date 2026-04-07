---
title: "CLI Workflow"
description: "End-to-end walkthrough of a realistic Voyages CLI session"
section: "guides"
order: 1
---

# CLI Workflow

This guide walks through a complete Voyages workflow from importing photos to rendering a finished map, using the CLI.

## 1. Import Photos

Start with a dry run to preview what will be imported before committing:

```bash
voyages import photos ~/Photos/europe-2025 --trip "Europe 2025" --dry-run
```

This scans the directory and reports what would be imported without writing anything to the database. Review the output to confirm Voyages found the expected files and extracted locations correctly.

When satisfied, run without `--dry-run` to import:

```bash
voyages import photos ~/Photos/europe-2025 --trip "Europe 2025"
```

**What happens during import:**
Voyages reads EXIF metadata from each photo in the top-level of the directory (subdirectories are not scanned). Photos with GPS coordinates are saved as `Photo` records. Photos without GPS data are skipped entirely — no record is created for them. No `Place` records are created automatically during import.

**Options:**

| Flag | Type | Description |
|------|------|-------------|
| `--trip` | string | Link imported photos to an existing trip by name. Optional. |
| `--dry-run` | flag | Preview the import without writing to the database. |

## 2. Review Places

After importing, check what places were extracted from your photos:

```bash
voyages place list
```

This lists all places in the database with their names, coordinates, and categories. Places extracted from EXIF GPS data will appear here alongside any places you have added manually.

## 3. Add Places Manually

For specific landmarks or points of interest that weren't captured by GPS, add them directly:

```bash
voyages place add --name "Eiffel Tower" --lat 48.8584 --lon 2.2945 --category landmark
```

**Options:**

| Flag | Type | Description |
|------|------|-------------|
| `--name` | string | Display name for the place. Required. |
| `--lat` | float | Latitude in decimal degrees. Required. |
| `--lon` | float | Longitude in decimal degrees. Required. |
| `--category` | string | Category label (e.g., `landmark`, `restaurant`, `hotel`). Optional. |

## 4. Search and Add

Use Nominatim geocoding to find places by name rather than entering coordinates manually:

```bash
voyages place search "Colosseum"
```

Voyages queries the Nominatim geocoding service and returns matching results with coordinates. Select the correct result to add it to your database. This is useful for well-known places where you don't want to look up coordinates yourself.

## 5. Create a Trip

Organize places into a trip:

```bash
voyages trip create "Italy 2025" --description "Two weeks in Italy"
```

Trips group related places and provide context for your maps. You can link places to trips and reference trips when importing photos.

**Options:**

| Flag | Type | Description |
|------|------|-------------|
| `--description` | string | Optional longer description for the trip. |

## 6. Create a Project

A project ties together a set of places, a trip, and rendering settings into a named map:

```bash
voyages project create "Italy Map" --map-type route
```

**Options:**

| Flag | Type | Description |
|------|------|-------------|
| `--map-type` | string | Map layout style. Default: `travel`. Choices: `travel`, `region`, `route`. |
| `--description` | string | Optional description for the project. |

Map type controls the visual organization of the output:
- `travel` — General travel map with place markers.
- `region` — Regional overview showing geographic extent.
- `route` — Sequential path connecting places in order.

> **Note:** There is no CLI command to associate places or trips with a project. After creating a project, use the web UI or the REST API to add `place_ids` and `trip_ids` to the project before rendering. A project with no associated places will render an empty map.

## 7. Render

Generate the map output from your project:

```bash
voyages render "Italy Map" --style vintage --format svg --dpi 300 --output ./maps
```

Voyages renders the project using the specified style and writes the output file to `./maps`.

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--format` | string | `png` | Output format. Choices: `svg`, `pdf`, `png`, `eps`. |
| `--style` | string | `default` | Visual style to apply. |
| `--dpi` | int | `200` | Resolution in dots per inch. |
| `--width` | int | `1200` | Output width in pixels. |
| `--output` | path | `.` | Directory to write the output file. |

The output filename is derived from the project name and format, e.g., `italy-map.svg`.

## 8. Try Different Outputs

Re-render with different settings to produce variants for different uses.

Print-ready PDF:

```bash
voyages render "Italy Map" --format pdf --dpi 300 --output ./maps
```

Dark style for screen use:

```bash
voyages render "Italy Map" --style dark --format png --output ./maps
```

Each render writes a new file without overwriting previous outputs as long as the format or filename differs. Experiment with `--style` values and `--dpi` settings to find the right balance of quality and file size for your intended use.
