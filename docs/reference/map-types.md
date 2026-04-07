---
title: "Map Types"
description: "Overview of the three Voyages map types and their configuration options"
section: "reference"
order: 5
---

# Map Types

## Overview

Voyages supports three map types, each optimized for a different visualization goal. The map type is set when creating a project via the `--map-type` flag and stored on the Project entity. It determines which render method is called and which cartographic projection is used.

## Travel Map (`travel`)

A world or large-area view designed to show everywhere you have been at a glance.

- **Projection:** EqualEarth — an equal-area projection well-suited for world maps that minimizes size distortion across continents.
- **Visited regions** are shaded using the `visited` color from the active style.
- **Places** are rendered as circular markers.
- A **legend** is included on the output.

Best for: showing all countries and places you have visited across a large geographic area.

## Region Map (`region`)

A zoomed view of a specific country, state, or area with detailed administrative boundaries.

- **Projection:** PlateCarree — a simple equirectangular projection appropriate for regional extents.
- **Boundaries** are drawn from the `admin_1_states_provinces_lines` dataset (50 m resolution) from Natural Earth shapefiles, showing states and provinces.
- **Place markers** are rendered with text labels.
- A **scale bar** is included on the output.
- The viewport is controlled by `center_lat`, `center_lon`, and `extent` in the project config.

Best for: a detailed view of a country, state, or other bounded area.

## Route Map (`route`)

A trip path visualization that connects ordered stops with a polyline.

- **Projection:** PlateCarree with auto-fit extent — the viewport is automatically calculated from the bounding coordinates of the trip stops, with 2-degree padding on each side.
- **Route polyline** connects stops in `position` order using the `route` color from the active style.
- **Numbered stop markers** label each stop (1, 2, 3, …).
- **Optional date labels** can be rendered when arrival/departure times are present.

Best for: showing a trip itinerary and the path traveled between stops.

## Configuration

The `config` dict on a Project controls render output dimensions and viewport. All keys are optional; defaults are applied by the render engine.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `dpi` | int | `200` | Output resolution in dots per inch |
| `width` | int | `1200` | Output width in pixels |
| `center_lat` | float | `0.0` | Viewport center latitude (region map) |
| `center_lon` | float | `0.0` | Viewport center longitude (region map) |
| `extent` | float | `20` | Half-width of the viewport in degrees (region map) |

Route maps ignore `center_lat`, `center_lon`, and `extent` because the viewport is computed automatically from stop coordinates.

## Choosing a Map Type

| Goal | Map type |
|------|----------|
| Show all countries or places visited | `travel` |
| Zoom into a country, state, or region | `region` |
| Visualize a trip itinerary | `route` |
