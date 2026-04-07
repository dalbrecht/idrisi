---
title: "CLI Reference"
description: "Complete reference for all Voyages CLI commands and options"
section: "reference"
order: 1
---

# CLI Reference

The `voyages` CLI is the primary interface for managing places, trips, projects, and map output. All subcommands follow the pattern `voyages <group> <command>`.

---

## place

Manage places stored in the local database.

### place list

**Synopsis**

```
voyages place list
```

**Description**

Lists every place in the database, showing name and coordinates.

**Arguments**

None.

**Options**

None.

**Example**

```
$ voyages place list
Paris (48.8566, 2.3522)
Tokyo (35.6762, 139.6503)
```

---

### place search

**Synopsis**

```
voyages place search <query>
```

**Description**

Searches for places via the geocoding service (Nominatim) and prints matching results.

**Arguments**

| Argument | Type   | Description          |
|----------|--------|----------------------|
| `query`  | string | Search query string. |

**Options**

None.

**Example**

```
$ voyages place search "Kyoto Japan"
Kyoto (35.0116, 135.7681)
```

---

### place add

**Synopsis**

```
voyages place add --name <name> --lat <lat> --lon <lon> [--category <category>]
```

**Description**

Adds a new place directly to the database with explicit coordinates. Use this when you already know the exact location rather than relying on geocoding.

**Arguments**

None.

**Options**

| Flag         | Type   | Default | Description                    |
|--------------|--------|---------|--------------------------------|
| `--name`     | string | (required) | Place name.               |
| `--lat`      | float  | (required) | Latitude in decimal degrees. |
| `--lon`      | float  | (required) | Longitude in decimal degrees. |
| `--category` | string | none    | Optional category label.       |

**Example**

```
$ voyages place add --name "Asakusa Temple" --lat 35.7148 --lon 139.7967 --category shrine
Created place: Asakusa Temple (a1b2c3d4)
```

---

## trip

Manage trips and their associated stops.

### trip list

**Synopsis**

```
voyages trip list
```

**Description**

Lists all trips in the database with their stop counts.

**Arguments**

None.

**Options**

None.

**Example**

```
$ voyages trip list
Japan 2024 (12 stops)
Europe Summer (8 stops)
```

---

### trip create

**Synopsis**

```
voyages trip create <name> [--description <description>]
```

**Description**

Creates a new named trip. Trips are collections of ordered stops that can later be associated with a project for route rendering.

**Arguments**

| Argument | Type   | Description |
|----------|--------|-------------|
| `name`   | string | Trip name.  |

**Options**

| Flag            | Type   | Default | Description           |
|-----------------|--------|---------|-----------------------|
| `--description` | string | none    | Optional description. |

**Example**

```
$ voyages trip create "Japan 2024" --description "Two-week itinerary through Honshu"
Created trip: Japan 2024 (e5f6a7b8)
```

---

## project

Manage map projects. A project groups places, trips, and regions and defines the map type used for rendering.

### project list

**Synopsis**

```
voyages project list
```

**Description**

Lists all projects in the database with their map type.

**Arguments**

None.

**Options**

None.

**Example**

```
$ voyages project list
Japan 2024 (travel)
Europe Highlights (region)
```

---

### project create

**Synopsis**

```
voyages project create <name> [--map-type <type>] [--description <description>]
```

**Description**

Creates a new project. The map type controls how the project is rendered: `travel` plots individual visited places, `region` shades geographic regions, and `route` draws a continuous path from trip stops.

**Arguments**

| Argument | Type   | Description   |
|----------|--------|---------------|
| `name`   | string | Project name. |

**Options**

| Flag            | Type   | Default  | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| `--map-type`    | string | `travel` | Map type. Choices: `travel`, `region`, `route`.  |
| `--description` | string | none     | Optional description.                            |

**Example**

```
$ voyages project create "Japan 2024" --map-type route --description "Full itinerary"
Created project: Japan 2024 (c9d0e1f2)
```

---

### project show

**Synopsis**

```
voyages project show <name>
```

**Description**

Displays full details for a project, including its map type, description, and counts of associated places, trips, and regions.

**Arguments**

| Argument | Type   | Description   |
|----------|--------|---------------|
| `name`   | string | Project name. |

**Options**

None.

**Example**

```
$ voyages project show "Japan 2024"
Name: Japan 2024
Type: travel
Description: Two-week itinerary
Places: 12
Trips: 1
Regions: 0
```

---

## import

Import external data into the Voyages database.

### import photos

**Synopsis**

```
voyages import photos <path> [--trip <trip_id>] [--dry-run]
```

**Description**

Scans a directory for JPEG files with embedded GPS EXIF data and imports each geotagged photo as a place. Use `--dry-run` to preview results without writing to the database.

**Arguments**

| Argument | Type   | Description                            |
|----------|--------|----------------------------------------|
| `path`   | string | Path to the directory containing photos. |

**Options**

| Flag        | Type   | Default | Description                                          |
|-------------|--------|---------|------------------------------------------------------|
| `--trip`    | string | none    | Trip ID to assign imported photos to.                |
| `--dry-run` | flag   | false   | Preview discovered photos without saving to the database. |

**Example**

```
$ voyages import photos ~/Pictures/Japan2024 --dry-run
[dry-run] Found 34 geotagged photos.
  /Users/alice/Pictures/Japan2024/DSC_0001.jpg (35.6762, 139.6503)
  /Users/alice/Pictures/Japan2024/DSC_0002.jpg (34.9671, 135.7727)
  ...
```

---

## serve

Start the Voyages web server for the browser-based map interface.

**Synopsis**

```
voyages serve [--host <host>] [--port <port>]
```

**Description**

Launches a uvicorn ASGI server hosting the Voyages web application. By default the server binds to localhost only; set `--host 0.0.0.0` to expose it on all network interfaces.

**Arguments**

None.

**Options**

| Flag     | Type    | Default       | Description             |
|----------|---------|---------------|-------------------------|
| `--host` | string  | `127.0.0.1`   | Host address to bind.   |
| `--port` | integer | `8080`        | Port to listen on.      |

**Example**

```
$ voyages serve --port 9000
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:9000 (Press CTRL+C to quit)
```

---

## render

Render a map project to an image or vector file.

**Synopsis**

```
voyages render <project_name> [--format <fmt>] [--style <style>] [--dpi <dpi>] [--width <width>] [--output <dir>]
```

**Description**

Generates a map for the named project using its associated places, trips, and regions. The rendering behaviour depends on the project's map type:

- `travel` — plots place markers on a world map
- `region` — shades geographic regions
- `route` — draws a route line from the first trip's stops

**Arguments**

| Argument       | Type   | Description                        |
|----------------|--------|------------------------------------|
| `project_name` | string | Name of the project to render.     |

**Options**

| Flag       | Type    | Default    | Description                                               |
|------------|---------|------------|-----------------------------------------------------------|
| `--format` | string  | `png`      | Output format. Choices: `svg`, `pdf`, `png`, `eps`.       |
| `--style`  | string  | `default`  | Map style name or path to a custom style file.            |
| `--dpi`    | integer | `200`      | Output resolution in DPI. Affects raster formats only.    |
| `--width`  | integer | `1200`     | Output width in pixels.                                   |
| `--output` | string  | `.`        | Directory to write the output file into.                  |

**Example**

```
$ voyages render "Japan 2024" --format pdf --dpi 300 --output ~/Desktop
Rendered: /Users/alice/Desktop/Japan 2024.pdf
```
