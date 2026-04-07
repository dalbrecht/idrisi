"""Tests for the projects API routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from voyages.server import create_app

EXPECTED_CREATED = 201
EXPECTED_OK = 200
EXPECTED_NO_CONTENT = 204


def _make_client() -> TestClient:
    app = create_app(database_url="sqlite://")
    return TestClient(app)


class TestProjectsAPI:
    def test_list_empty(self) -> None:
        client = _make_client()
        response = client.get("/api/projects")
        assert response.status_code == EXPECTED_OK
        assert response.json() == []

    def test_create_project(self) -> None:
        client = _make_client()
        response = client.post(
            "/api/projects",
            json={"name": "World Map", "map_type": "travel"},
        )
        assert response.status_code == EXPECTED_CREATED
        data = response.json()
        assert data["name"] == "World Map"
        assert data["map_type"] == "travel"
        assert "id" in data

    def test_render_endpoint_exists(self) -> None:
        """The render endpoint should not return 405 (Method Not Allowed).

        It may return 404 (project not found) or another error depending on
        state, but 405 would mean the route is not registered.
        """
        client = _make_client()
        response = client.post("/api/render/00000000-0000-0000-0000-000000000000")
        assert response.status_code != 405

    def test_render_region_map_returns_png(self) -> None:
        client = _make_client()
        create_resp = client.post(
            "/api/projects",
            json={"name": "RegionMap", "map_type": "region"},
        )
        assert create_resp.status_code == EXPECTED_CREATED
        project_id = create_resp.json()["id"]

        render_resp = client.post(f"/api/render/{project_id}")
        assert render_resp.status_code == EXPECTED_OK
        # Verify PNG magic bytes
        assert render_resp.content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_render_route_map_no_trips_returns_400(self) -> None:
        client = _make_client()
        create_resp = client.post(
            "/api/projects",
            json={"name": "RouteMap", "map_type": "route"},
        )
        assert create_resp.status_code == EXPECTED_CREATED
        project_id = create_resp.json()["id"]

        render_resp = client.post(f"/api/render/{project_id}")
        assert render_resp.status_code == 400
        detail = render_resp.json().get("detail", "")
        assert "trip" in detail.lower()
