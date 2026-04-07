---
title: "API Endpoints"
description: "Complete endpoint reference for places, trips, projects, regions, and render"
section: "reference"
order: 3
---

# API Endpoints

All endpoints are relative to `http://127.0.0.1:8080/api`. See [API Overview](api-overview.md) for base URL, content type, and error format.

---

## Places

Places are geographic points with a name, coordinates, and optional metadata.

| Method | Path | Status | Purpose |
|--------|------|--------|---------|
| GET | `/api/places` | 200 | List all places |
| POST | `/api/places` | 201 | Create a place |
| GET | `/api/places/search?q=<query>` | 200 | Search places by name |
| DELETE | `/api/places/{place_id}` | 204 | Delete a place |

**Create a place**

```bash
curl -s -X POST http://127.0.0.1:8080/api/places \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eiffel Tower",
    "lat": 48.8584,
    "lon": 2.2945,
    "source": "manual",
    "country": "France",
    "admin1": "Île-de-France",
    "category": "landmark",
    "notes": "Visit at sunset"
  }'
```

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Eiffel Tower",
  "lat": 48.8584,
  "lon": 2.2945,
  "country": "France",
  "admin1": "Île-de-France",
  "category": "landmark",
  "notes": "Visit at sunset",
  "source": "manual"
}
```

**Search places**

```bash
curl -s "http://127.0.0.1:8080/api/places/search?q=eiffel"
```

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Eiffel Tower",
    "lat": 48.8584,
    "lon": 2.2945,
    "country": "France",
    "admin1": "Île-de-France",
    "category": "landmark",
    "notes": "Visit at sunset",
    "source": "manual"
  }
]
```

---

## Trips

Trips group places into an itinerary with an optional description and date range.

| Method | Path | Status | Purpose |
|--------|------|--------|---------|
| GET | `/api/trips` | 200 | List all trips |
| POST | `/api/trips` | 201 | Create a trip |
| DELETE | `/api/trips/{trip_id}` | 204 | Delete a trip |

**Create a trip**

```bash
curl -s -X POST http://127.0.0.1:8080/api/trips \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paris 2025",
    "description": "Week-long trip covering major landmarks and museums"
  }'
```

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "name": "Paris 2025",
  "description": "Week-long trip covering major landmarks and museums",
  "start_date": null,
  "end_date": null
}
```

---

## Projects

Projects define a map to render, including its type and optional description.

| Method | Path | Status | Purpose |
|--------|------|--------|---------|
| GET | `/api/projects` | 200 | List all projects |
| POST | `/api/projects` | 201 | Create a project |
| DELETE | `/api/projects/{project_id}` | 204 | Delete a project |

**Create a project**

```bash
curl -s -X POST http://127.0.0.1:8080/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Europe Trip Map",
    "map_type": "travel",
    "description": "2025 European adventure"
  }'
```

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "name": "Europe Trip Map",
  "description": "2025 European adventure",
  "map_type": "travel"
}
```

---

## Regions

Regions represent geographic areas such as countries or administrative divisions.

| Method | Path | Status | Purpose |
|--------|------|--------|---------|
| GET | `/api/regions` | 200 | List all regions |
| POST | `/api/regions` | 201 | Create a region |
| DELETE | `/api/regions/{region_id}` | 204 | Delete a region |

**Create a region**

```bash
curl -s -X POST http://127.0.0.1:8080/api/regions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "France",
    "region_type": "country",
    "region_code": "FR"
  }'
```

```json
{
  "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "name": "France",
  "region_type": "country",
  "region_code": "FR"
}
```

---

## Render

Renders a project to a PNG image.

| Method | Path | Status | Purpose |
|--------|------|--------|---------|
| POST | `/api/render/{project_id}` | 200 | Render project as PNG |

The response is a PNG file (`image/png`), not JSON. Use `-o` to save it.

**Render a project**

```bash
curl -s -X POST \
  http://127.0.0.1:8080/api/render/c3d4e5f6-a7b8-9012-cdef-123456789012 \
  -o map.png
```

The file `map.png` is written to disk. The rendered output reflects the current state of the project including all associated places, trips, and regions.

---

For the complete API specification including all parameters and response schemas, see the interactive documentation at `/docs` when running the server.
