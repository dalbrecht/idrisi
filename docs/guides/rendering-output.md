---
title: "Rendering & Output"
description: "Output formats, projections, render settings, and example commands"
section: "guides"
order: 5
---

# Rendering & Output

## Output Formats

| Format | Flag | Best For |
|---|---|---|
| PNG | `--format png` | Web, social media, quick preview |
| SVG | `--format svg` | Scalable graphics, editing in Illustrator/Inkscape |
| PDF | `--format pdf` | Print-ready documents |
| EPS | `--format eps` | Legacy print workflows |

Note: WebP is defined in the `OutputFormat` enum but the CLI render command currently accepts `svg|pdf|png|eps`.

## Projections

Idrisi uses two projections depending on map type:

| Projection | Used For | Characteristics |
|---|---|---|
| EqualEarth | Travel maps — world view | Equal-area, minimizes size distortion across continents |
| PlateCarree | Region and route maps — zoomed | Equirectangular, straightforward for bounded extents |

## Render Settings

| Flag | Default | Description |
|---|---|---|
| `--dpi` | 200 | Dots per inch. Use 300+ for print output. |
| `--width` | 1200 | Output width in pixels. |
| `--output` | `.` | Directory where the output file is written. |

## Map Types and Rendering

**Travel** — Shades visited regions, places place markers, and uses EqualEarth projection for a world-view layout.

**Region** — Zooms to the specified bounds and renders detailed admin_1 boundaries from Natural Earth data. Includes place labels and a scale bar.

**Route** — Draws the trip path as a polyline between ordered stops with numbered stop markers. Uses PlateCarree projection with an auto-fit extent around the route.

## Examples

Quick preview:

```bash
idrisi render "My Map" --format png
```

Print-ready PDF at 300 DPI:

```bash
idrisi render "My Map" --format pdf --dpi 300
```

High-resolution poster for printing:

```bash
idrisi render "My Map" --format png --dpi 300 --width 3600
```

SVG export for editing in Illustrator or Inkscape:

```bash
idrisi render "My Map" --format svg --output ./exports
```
