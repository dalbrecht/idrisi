"""Tests for API error handling — invalid input and missing entities."""

from __future__ import annotations

import uuid

from starlette.testclient import TestClient

from voyages.server import create_app

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
