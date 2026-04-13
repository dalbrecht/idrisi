"""Tests for the regions API routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from idrisi.server import create_app

EXPECTED_CREATED = 201
EXPECTED_OK = 200
EXPECTED_NO_CONTENT = 204


def _make_client() -> TestClient:
    app = create_app(database_url="sqlite://")
    return TestClient(app)


class TestRegionsAPI:
    def test_list_empty(self) -> None:
        client = _make_client()
        response = client.get("/api/regions")
        assert response.status_code == EXPECTED_OK
        assert response.json() == []

    def test_create_region(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/regions",
            json={"name": "Bavaria", "region_type": "state", "region_code": "DE-BY"},
        )
        assert response.status_code == EXPECTED_CREATED
        data = response.json()
        assert data["name"] == "Bavaria"
        assert data["region_type"] == "state"
        assert data["region_code"] == "DE-BY"
        assert "id" in data

    def test_create_two_regions_list_returns_both(self) -> None:
        client = _make_client()
        client.post(
            "/api/regions",
            json={"name": "Bavaria", "region_type": "state"},
        )
        client.post(
            "/api/regions",
            json={"name": "Saxony", "region_type": "state"},
        )
        response = client.get("/api/regions")
        assert response.status_code == EXPECTED_OK
        assert len(response.json()) == 2

    def test_create_then_delete_list_empty(self) -> None:
        client = _make_client()
        create_response = client.post(
            "/api/regions",
            json={"name": "Thuringia", "region_type": "state"},
        )
        region_id = create_response.json()["id"]
        delete_response = client.delete(f"/api/regions/{region_id}")
        assert delete_response.status_code == EXPECTED_NO_CONTENT

        list_response = client.get("/api/regions")
        assert list_response.json() == []
