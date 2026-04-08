"""Tests for the projects API routes."""

from __future__ import annotations

import os
import tempfile
from uuid import uuid4

from fastapi.testclient import TestClient

from voyages.domain.entities import Place, Trip, TripStop
from voyages.domain.value_objects import MapType
from voyages.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlProjectRepository,
    SqlTripRepository,
)
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.server import create_app

EXPECTED_CREATED = 201
EXPECTED_OK = 200
EXPECTED_NO_CONTENT = 204


def _make_client() -> TestClient:
    app = create_app(database_url="sqlite://")
    return TestClient(app)


class TestAppFactory:
    """Tests for the application factory (server/__init__.py)."""

    def test_create_app_with_file_database(self) -> None:
        """Verifies the app factory creates a database file when given a file-based SQLite URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            app = create_app(database_url=f"sqlite:///{db_path}")
            client = TestClient(app)
            response = client.get("/api/projects")
            assert response.status_code == EXPECTED_OK
            assert os.path.exists(db_path)


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

    def test_delete_project(self) -> None:
        """Verifies that deleting a project removes it from the project list."""
        client = _make_client()
        create_resp = client.post(
            "/api/projects",
            json={"name": "ToDelete", "map_type": "travel"},
        )
        assert create_resp.status_code == EXPECTED_CREATED
        project_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/api/projects/{project_id}")
        assert delete_resp.status_code == EXPECTED_NO_CONTENT

        # Verify it's gone
        list_resp = client.get("/api/projects")
        assert list_resp.status_code == EXPECTED_OK
        ids = [p["id"] for p in list_resp.json()]
        assert project_id not in ids

    def test_render_travel_map_returns_png(self) -> None:
        """Verifies that rendering a travel map project returns a valid PNG image."""
        client = _make_client()
        create_resp = client.post(
            "/api/projects",
            json={"name": "TravelMap", "map_type": "travel"},
        )
        assert create_resp.status_code == EXPECTED_CREATED
        project_id = create_resp.json()["id"]

        render_resp = client.post(f"/api/render/{project_id}")
        assert render_resp.status_code == EXPECTED_OK
        # Verify PNG magic bytes
        assert render_resp.content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_render_route_map_with_trip_returns_png(self) -> None:
        """Verifies that rendering a route map project with trips returns a valid PNG image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "route_test.db")
            db_url = f"sqlite:///{db_path}"

            # Set up data directly via repositories
            engine = create_engine_and_tables(db_url)
            session = get_session(engine)

            place1 = Place(id=uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")
            place2 = Place(
                id=uuid4(), name="London", latitude=51.50, longitude=-0.12, source="test"
            )
            trip = Trip(
                id=uuid4(),
                name="Route Test Trip",
                stops=[
                    TripStop(place_id=place1.id, position=0),
                    TripStop(place_id=place2.id, position=1),
                ],
            )

            place_repo = SqlPlaceRepository(session)
            trip_repo = SqlTripRepository(session)
            project_repo = SqlProjectRepository(session)

            from voyages.application.project_service import ProjectService  # noqa: PLC0415

            place_repo.save(place1)
            place_repo.save(place2)
            trip_repo.save(trip)

            project_service = ProjectService(project_repo)
            project = project_service.create(name="RouteWithTrip", map_type=MapType.ROUTE)
            project_service.add_place(project.id, place1.id)
            project_service.add_place(project.id, place2.id)
            project_service.add_trip(project.id, trip.id)
            session.commit()
            session.close()

            # Now render via the HTTP layer pointing at the same DB file
            app = create_app(database_url=db_url)
            client = TestClient(app)
            render_resp = client.post(f"/api/render/{project.id}")
            assert render_resp.status_code == EXPECTED_OK
            assert render_resp.content[:8] == b"\x89PNG\r\n\x1a\n"
