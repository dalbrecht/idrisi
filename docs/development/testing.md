---
title: "Testing"
description: "How to run tests, test structure, coverage targets, and testing conventions for Voyages"
section: "development"
order: 3
---

# Testing

## Running Tests

Run the full test suite:

```bash
make test   # runs: uv run pytest
```

Common pytest invocations:

```bash
# Run a single file
pytest tests/domain/test_entities.py

# Verbose output
pytest -v

# With coverage report
pytest --cov=voyages
```

Pytest is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

## Test Structure

The test layout mirrors the source layout. Each directory tests its corresponding architectural layer:

```
tests/
├── domain/             # Pure unit tests — no I/O, no mocks
├── application/        # Service tests — mock repository protocols
├── infrastructure/     # Integration tests — real in-memory SQLite
├── cli/                # Command tests — Typer CliRunner
└── server/             # Endpoint tests — FastAPI TestClient
```

## Coverage Targets

- **Domain layer:** 100% — pure logic with no I/O or external dependencies; there is no excuse for a gap here.
- **Overall:** 95% or higher.

## Testing by Layer

### Domain

Pure unit tests. No mocks, no I/O, no fixtures beyond simple object construction.

Test coverage includes:
- Dataclass construction and field defaults
- `Coordinates` range validation (latitude −90..90, longitude −180..180)
- `BoundingBox` behavior and edge cases
- Enum membership and string values
- Domain exception hierarchy

### Application

Service tests verify orchestration logic and error handling. Repositories and external services are replaced with mock implementations of their protocols.

```python
class FakePlaceRepository:
    """Implements PlaceRepository protocol for testing."""
    ...
```

Test coverage includes:
- Correct delegation to repository methods
- Error propagation from repositories to callers
- Correct domain exceptions raised for missing entities
- Service coordination across multiple protocols

### Infrastructure

Integration tests run against a real in-memory SQLite database. No mocking at this layer.

Test coverage includes:
- ORM model to domain entity mappings (round-trip)
- Repository query correctness (filter, sort, not-found behavior)
- Renderer producing output files in the expected format
- Geocoding client parsing Nominatim responses

### CLI

Command tests use Typer's `CliRunner` to invoke commands as a subprocess would.

```python
from typer.testing import CliRunner
from voyages.cli import app

runner = CliRunner()
result = runner.invoke(app, ["place", "list"])
assert result.exit_code == 0
```

Test coverage includes:
- Command output format and content
- Exit codes for success and error paths
- Argument and option parsing

### Server

Endpoint tests use FastAPI's `TestClient` with an in-memory database injected via dependency override.

```python
from fastapi.testclient import TestClient
from voyages.server import app

client = TestClient(app)
response = client.get("/places")
assert response.status_code == 200
```

Test coverage includes:
- HTTP status codes for success and error paths
- Request and response body structure
- Validation error responses

## Conventions

**Fixtures** — define database sessions and test data factories as pytest fixtures in `conftest.py` files at the appropriate directory level.

**Mock at layer boundaries only** — do not mock within a layer. Application tests mock infrastructure protocols; infrastructure tests do not mock the database.

**Factories** — use factory functions (or [factory_boy](https://factoryboy.readthedocs.io/) factories) to create domain entities with sensible defaults, reducing boilerplate and making test intent clear:

```python
def make_place(name: str = "Paris", lat: float = 48.8566, lon: float = 2.3522) -> Place:
    return Place(name=name, coordinates=Coordinates(latitude=lat, longitude=lon))
```
