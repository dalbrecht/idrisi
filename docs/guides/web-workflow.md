---
title: "Web UI Workflow"
description: "End-to-end walkthrough of a Idrisi session through the browser"
section: "guides"
order: 2
---

# Web UI Workflow

This guide walks through the same end-to-end workflow as the CLI guide — importing places, organizing trips, composing a map, and rendering output — using the Idrisi web interface.

## 1. Start the Server

Start the server:

```bash
idrisi serve
```

Open your browser to `http://127.0.0.1:8080`.

For development with hot-reload, use Make instead:

```bash
make serve
```

This runs uvicorn directly:

```bash
uv run uvicorn idrisi.server:create_app --factory --reload
```

> **Note:** `make serve` runs uvicorn directly and defaults to port **8000**, not 8080. Use `http://127.0.0.1:8000` when starting with `make serve`. `idrisi serve` defaults to port **8080**.

Screenshot: [Browser showing the Idrisi dashboard at http://127.0.0.1:8080]

## 2. Dashboard

The dashboard is your starting point. It provides:

- **Quick-action buttons** — shortcuts to common tasks like adding a place or creating a new project.
- **Navigation tabs** — access the three main sections: Places, Trips, and Map Composer.
- **Summary counts** — at-a-glance totals for places, trips, and projects in your database.

Screenshot: [Dashboard with navigation tabs and quick-action buttons visible]

## 3. Add Places

Navigate to the **Places** tab.

Use the **search bar** at the top of the page to filter your saved places by name. Type part of a place name to narrow the list — this searches over places already in your database, not an external geocoding service.

For locations not found by search, use the **manual add form**: enter a name, latitude, longitude, and optional category, then click Add Place.

Screenshot: [Places tab showing the search bar filtering the saved places list, and the manual add form below]

Your added places appear in the places list with their name, coordinates, and category.

## 4. Manage Trips

Navigate to the **Trips** tab.

Click **New Trip** to create a trip. Enter:

- **Name** — required.
- **Description** — optional, for notes about the trip.

Click Save. The trip appears in the trips list.

To associate places with a trip, use the trip detail view to link existing places. Note that trip stop ordering — the sequence in which places appear on a route map — is not currently configurable through the web UI, CLI, or API. Stops are rendered in the order they were added.

Screenshot: [Trips tab with a trip detail view showing linked places]

## 5. Compose a Map

Navigate to the **Map Composer** tab.

Click **New Project** and configure:

- **Name** — the project identifier, used in the output filename.
- **Map type** — choose from `travel`, `region`, or `route`. This controls how places are laid out on the map.
- **Style** — select a visual style from the dropdown (e.g., `default`, `vintage`, `dark`).

Associate the project with a trip or select individual places to include on the map.

Screenshot: [Map Composer tab with the new project form showing name, map type, and style fields]

## 6. Preview and Render

Once a project is configured, the **map preview** displays your places on an interactive Leaflet map using OpenStreetMap tiles. Pan and zoom to confirm the extent of your map and that all expected places are shown.

Screenshot: [Map preview with place markers visible on an OpenStreetMap base layer]

When you are satisfied with the preview, click **Render**. Idrisi generates the output file server-side using the project's style and format settings.

When rendering completes, a **Download** button appears. Click it to save the output file to your machine.

To produce additional variants (e.g., PDF for print or a different style), return to the project settings, adjust the options, and click Render again.
