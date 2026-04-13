"""Tests for the places API routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from idrisi.server import create_app

PARIS_LAT = 48.8566
PARIS_LON = 2.3522

EXPECTED_CREATED = 201
EXPECTED_OK = 200
EXPECTED_NO_CONTENT = 204


def _make_client() -> TestClient:
    app = create_app(database_url="sqlite://")
    return TestClient(app)


class TestPlacesAPI:
    def test_list_empty(self) -> None:
        client = _make_client()
        response = client.get("/api/places")
        assert response.status_code == EXPECTED_OK
        assert response.json() == []

    def test_create_place(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/places",
            json={
                "name": "Paris",
                "lat": PARIS_LAT,
                "lon": PARIS_LON,
                "source": "manual",
            },
        )
        assert response.status_code == EXPECTED_CREATED
        data = response.json()
        assert data["name"] == "Paris"
        assert data["lat"] == PARIS_LAT
        assert data["lon"] == PARIS_LON
        assert data["source"] == "manual"
        assert "id" in data

    def test_create_and_list(self) -> None:
        client = _make_client()
        client.post(
            "/api/places",
            json={
                "name": "Paris",
                "lat": PARIS_LAT,
                "lon": PARIS_LON,
                "source": "manual",
            },
        )
        response = client.get("/api/places")
        assert response.status_code == EXPECTED_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Paris"

    def test_search_endpoint_exists(self) -> None:
        client = _make_client()
        response = client.get("/api/places/search", params={"q": "Paris"})
        assert response.status_code == EXPECTED_OK
        assert isinstance(response.json(), list)

    def test_delete_place(self) -> None:
        client = _make_client()
        create_response = client.post(
            "/api/places",
            json={
                "name": "Paris",
                "lat": PARIS_LAT,
                "lon": PARIS_LON,
                "source": "manual",
            },
        )
        place_id = create_response.json()["id"]
        delete_response = client.delete(f"/api/places/{place_id}")
        assert delete_response.status_code == EXPECTED_NO_CONTENT

        # Verify it's gone
        list_response = client.get("/api/places")
        assert list_response.json() == []
