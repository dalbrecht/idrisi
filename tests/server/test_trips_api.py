"""Tests for the trips API routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from idrisi.server import create_app

EXPECTED_CREATED = 201
EXPECTED_OK = 200
EXPECTED_NO_CONTENT = 204


def _make_client() -> TestClient:
    app = create_app(database_url="sqlite://")
    return TestClient(app)


class TestTripsAPI:
    def test_list_empty(self) -> None:
        client = _make_client()
        response = client.get("/api/trips")
        assert response.status_code == EXPECTED_OK
        assert response.json() == []

    def test_create_trip(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/trips",
            json={"name": "Europe 2024", "description": "Summer trip"},
        )
        assert response.status_code == EXPECTED_CREATED
        data = response.json()
        assert data["name"] == "Europe 2024"
        assert data["description"] == "Summer trip"
        assert "id" in data

    def test_delete_trip(self) -> None:
        client = _make_client()
        create_response = client.post(
            "/api/trips",
            json={"name": "Europe 2024"},
        )
        trip_id = create_response.json()["id"]
        delete_response = client.delete(f"/api/trips/{trip_id}")
        assert delete_response.status_code == EXPECTED_NO_CONTENT

        # Verify it's gone
        list_response = client.get("/api/trips")
        assert list_response.json() == []
