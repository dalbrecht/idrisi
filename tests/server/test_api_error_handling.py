"""Tests for API error handling — invalid input and missing entities."""

from __future__ import annotations

import uuid

from starlette.testclient import TestClient

from idrisi.server import create_app

EXPECTED_BAD_REQUEST = 400
EXPECTED_NOT_FOUND = 404
EXPECTED_NO_CONTENT = 204
EXPECTED_CREATED = 201


def _make_client() -> TestClient:
    app = create_app(database_url="sqlite://")
    return TestClient(app)


class TestInvalidUUID:
    """DELETE with malformed UUID string should return 400, not 500."""

    def test_delete_place_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.delete("/api/places/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()

    def test_delete_trip_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.delete("/api/trips/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()

    def test_delete_project_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.delete("/api/projects/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()

    def test_delete_region_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.delete("/api/regions/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()

    def test_render_invalid_uuid(self) -> None:
        client = _make_client()
        response = client.post("/api/render/not-a-uuid")
        assert response.status_code == EXPECTED_BAD_REQUEST
        assert "detail" in response.json()


class TestEntityNotFound:
    """DELETE/POST with valid but nonexistent UUID should return 404."""

    def test_delete_place_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/places/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()

    def test_delete_trip_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/trips/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()

    def test_delete_project_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/projects/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()

    def test_delete_region_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/regions/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()

    def test_render_project_not_found(self) -> None:
        client = _make_client()
        fake_id = str(uuid.uuid4())
        response = client.post(f"/api/render/{fake_id}")
        assert response.status_code == EXPECTED_NOT_FOUND
        assert "detail" in response.json()


EXPECTED_UNPROCESSABLE = 422


class TestValidationErrors:
    """POST with invalid request bodies should return 422."""

    def test_create_place_missing_name(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/places",
            json={"lat": 48.85, "lon": 2.35, "source": "manual"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_place_invalid_lat_type(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/places",
            json={"name": "Paris", "lat": "not-a-number", "lon": 2.35, "source": "manual"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_trip_missing_name(self) -> None:
        client = _make_client()
        response = client.post("/api/trips", json={})
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_project_missing_name(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/projects",
            json={"map_type": "travel"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_project_invalid_map_type(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/projects",
            json={"name": "Test", "map_type": "invalid_type"},
        )
        # MapType("invalid_type") raises ValueError → caught by handler → 400
        # OR Pydantic validates → 422. Either way, NOT 500.
        assert response.status_code in (EXPECTED_BAD_REQUEST, EXPECTED_UNPROCESSABLE)

    def test_create_region_missing_name(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/regions",
            json={"region_type": "country"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE

    def test_create_region_missing_region_type(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/regions",
            json={"name": "France"},
        )
        assert response.status_code == EXPECTED_UNPROCESSABLE
