---
title: "Importing Photos"
description: "Extract GPS coordinates and timestamps from photo EXIF data to create places automatically"
section: "guides"
order: 3
---

# Importing Photos

## Overview

Voyages extracts GPS coordinates and timestamps from photo EXIF data to automatically create places. Each geotagged photo becomes a Place entry and a Photo record in the database — no manual coordinate entry required.

## Supported Data

Voyages reads the following EXIF fields from each photo:

| Field | EXIF Source | Stored As |
|---|---|---|
| Latitude / Longitude | `GPSLatitude`, `GPSLongitude` | `Place.latitude`, `Place.longitude` |
| Timestamp | `DateTimeOriginal` | `Photo.taken_at` |

Photos without GPS data are skipped with a warning. The import summary reports how many files were skipped and why.

## Basic Import

```bash
voyages import photos ~/Photos/trip-2025
```

Voyages scans the directory recursively, reads EXIF metadata from each image, and creates:

- A `Place` record for each unique GPS location (`source="exif"`)
- A `Photo` record linking the file to its place

## Dry Run

Preview what will be imported without writing anything to the database:

```bash
voyages import photos ~/Photos/trip-2025 --dry-run
```

The dry run reports the number of photos found, how many have GPS data, and what Place entries would be created. Use this to verify Voyages is reading the right files before committing.

## Link to a Trip

Associate imported photos with an existing trip:

```bash
voyages import photos ~/Photos/trip-2025 --trip "Europe 2025"
```

The trip name must match an existing trip in the database. Each Photo record will have its `trip_id` set accordingly.

## What Gets Created

Each geotagged photo produces two records:

**Place**
- `latitude`, `longitude` — from GPS EXIF fields
- `source` — set to `"exif"`

**Photo**
- `file_path` — absolute path to the image file
- `latitude`, `longitude` — copied from GPS EXIF fields
- `taken_at` — from `DateTimeOriginal` EXIF field
- `place_id` — references the created or matched Place
- `trip_id` — set if `--trip` was specified

## Common Issues

**No GPS data**

Phone cameras often omit GPS when location access is disabled. Voyages skips these files and reports them in the import summary. Enable location on your camera or manually assign places afterward.

**Timezone handling**

EXIF `DateTimeOriginal` does not store a timezone. Voyages stores the timestamp as-is. If your photos span multiple timezones, `taken_at` values will reflect local camera time, not UTC.

**Duplicate photos**

Running the same import twice will attempt to create duplicate Photo records for the same file path. Voyages uses `file_path` to detect duplicates and skips files already in the database.
