---
title: "API Overview"
description: "Base URL, content type, authentication, and error format for the Voyages REST API"
section: "reference"
order: 2
---

# API Overview

The Voyages API is a REST API built with FastAPI. It serves as the backend for the Voyages web UI and can be used directly from any HTTP client.

## Base URL

When running `voyages serve` with default settings:

```
http://127.0.0.1:8080
```

All API endpoints are prefixed with `/api` (e.g., `/api/places`, `/api/trips`). The host and port can be changed with `--host` and `--port` flags.

## Interactive Documentation

FastAPI generates interactive API documentation automatically from route definitions. Two UIs are available while the server is running:

| UI | URL |
|----|-----|
| Swagger UI | `http://127.0.0.1:8080/docs` |
| ReDoc | `http://127.0.0.1:8080/redoc` |

Swagger UI lets you try requests directly from the browser. ReDoc provides a cleaner reading experience for the full schema.

## Content Type

All request bodies and responses use `application/json`.

**Exception:** The `POST /api/render/{project_id}` endpoint returns a PNG image (`image/png`) rather than JSON.

All request examples in the [API Endpoints](api-endpoints.md) reference use full URLs such as `http://127.0.0.1:8080/api/places`.

## Identifiers

All entities (places, trips, projects, regions) use UUID v4 identifiers. UUIDs are assigned by the server at creation time and returned in response bodies.

Example: `"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"`

## Authentication

None. Voyages is a single-user local tool intended to run on localhost. No API keys, tokens, or sessions are required.

## Error Responses

Errors follow FastAPI's standard format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common status codes:

| Code | Meaning |
|------|---------|
| 404 | Resource not found |
| 422 | Validation error (missing or invalid field) |
| 500 | Internal server error |

Validation errors include additional structure identifying which field failed:

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## CORS

The server is configured with `CORSMiddleware` allowing all origins. This supports local development setups where the UI runs on a different port from the API.
