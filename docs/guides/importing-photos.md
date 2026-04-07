---
title: "Importing Photos"
description: "Extract GPS coordinates and timestamps from photo EXIF data to create photo records"
section: "guides"
order: 3
---

# Importing Photos

## Overview

Voyages extracts GPS coordinates and timestamps from photo EXIF data and saves them as Photo records. Only photos with valid GPS data are imported — photos without GPS coordinates are silently skipped.

## Supported Data

Voyages reads the following EXIF fields from each photo:

| Field | EXIF Source | Stored As |
|---|---|---|
| Latitude / Longitude | `GPSLatitude`, `GPSLongitude` | `Photo.latitude`, `Photo.longitude` |
| Timestamp | `DateTimeOriginal` | `Photo.taken_at` |

Photos without GPS data are skipped entirely. No warning or count is reported for skipped files — the import summary shows only the number of photos successfully imported.

## Basic Import

```bash
voyages import photos ~/Photos/trip-2025
```

Voyages scans the **top-level** of the directory (non-recursive), reads EXIF metadata from each image file, and creates a `Photo` record for each file that contains GPS coordinates. No `Place` records are created automatically.

## Dry Run

Preview what will be imported without writing anything to the database:

```bash
voyages import photos ~/Photos/trip-2025 --dry-run
```

The dry run reports the number of geotagged photos found. Use this to verify Voyages is reading the right files before committing.

## Link to a Trip

The `--trip` option is accepted but **not yet implemented**:

```bash
voyages import photos ~/Photos/trip-2025 --trip "Europe 2025"
```

Passing `--trip` prints a message that trip assignment is not yet implemented. Photo records are still imported normally; the `trip_id` field will not be set.

## What Gets Created

Each geotagged photo produces one record:

**Photo**
- `file_path` — absolute path to the image file
- `latitude`, `longitude` — from GPS EXIF fields
- `taken_at` — from `DateTimeOriginal` EXIF field (see timezone note below)

No `Place` records are created during photo import. To associate imported photos with places, use `voyages place add` or the web UI to create places manually.

## Common Issues

**No GPS data**

Phone cameras often omit GPS when location access is disabled. Photos without GPS coordinates are skipped entirely. Enable location on your camera app before shooting, or add places manually afterward.

**Timezone handling**

EXIF `DateTimeOriginal` does not include timezone information. Voyages parses the timestamp and stores it labeled as UTC. If the photo was taken in a timezone other than UTC, `taken_at` will not reflect the actual moment of capture in UTC — it will reflect the camera's local clock reading, incorrectly labeled as UTC.

**Duplicate photos**

Voyages does not detect duplicate imports. Running the same import command twice will create duplicate `Photo` records for the same file. Check the database before re-importing from the same directory.

**Subdirectories**

The import command scans only the top level of the specified directory. Files in subdirectories are not imported. Organize photos into flat directories before importing, or run the command once for each subdirectory.
