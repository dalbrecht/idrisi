"""End-to-end smoke tests for the full Voyages workflow."""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from voyages.application.place_service import PlaceService
from voyages.application.project_service import ProjectService
from voyages.cli import app
from voyages.domain.value_objects import MapType, OutputFormat
from voyages.infrastructure.db.repository import SqlPlaceRepository, SqlProjectRepository
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.renderer.engine import RenderEngine
from voyages.infrastructure.renderer.styles import load_style
from voyages.server import create_app

if TYPE_CHECKING:
    from voyages.domain.entities import Place
    from voyages.domain.value_objects import Coordinates

runner = CliRunner()

TOKYO_LAT = 35.6762
TOKYO_LON = 139.6503
PARIS_LAT = 48.8566
PARIS_LON = 2.3522

MIN_FILE_SIZE = 1000


class FakeGeocoding:
    """No-network geocoding stub for testing."""

    def search(self, query: str) -> list[Place]:
        return []

    def reverse_geocode(self, coords: Coordinates) -> Place | None:
        return None


def _make_in_memory_session() -> object:
    """Return a (engine, session) pair backed by in-memory SQLite."""
    engine = create_engine_and_tables("sqlite:///:memory:")
    return engine, get_session(engine)


class TestFullWorkflowViaServices:
    """Smoke test: create places, project, add places, render map."""

    def test_full_workflow_via_services(self) -> None:
        engine = create_engine_and_tables("sqlite:///:memory:")
        session = get_session(engine)

        place_repo = SqlPlaceRepository(session)
        project_repo = SqlProjectRepository(session)
        geocoding = FakeGeocoding()

        place_svc = PlaceService(place_repo=place_repo, geocoding=geocoding)
        project_svc = ProjectService(project_repo=project_repo)

        # Create two places
        tokyo = place_svc.create(
            name="Tokyo",
            lat=TOKYO_LAT,
            lon=TOKYO_LON,
            source="manual",
            country="Japan",
        )
        paris = place_svc.create(
            name="Paris",
            lat=PARIS_LAT,
            lon=PARIS_LON,
            source="manual",
            country="France",
        )

        assert tokyo.id is not None
        assert paris.id is not None

        # Create a travel project
        project = project_svc.create(
            name="World Tour",
            map_type=MapType.TRAVEL,
        )
        assert project.id is not None

        # Add places to the project
        project = project_svc.add_place(project.id, tokyo.id)
        project = project_svc.add_place(project.id, paris.id)
        assert len(project.place_ids) == 2

        # Reload places for rendering
        all_places = place_svc.list_all()
        assert len(all_places) == 2

        # Render a travel map to a temp file
        style = load_style("default")
        engine_renderer = RenderEngine(style=style)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "world_tour.png")
            result_path = engine_renderer.render_travel_map(
                places=all_places,
                regions=[],
                output_path=output_path,
                output_format=OutputFormat.PNG,
            )

            assert os.path.exists(result_path)
            file_size = os.path.getsize(result_path)
            assert file_size > MIN_FILE_SIZE, (
                f"Rendered map file too small: {file_size} bytes (expected > {MIN_FILE_SIZE})"
            )

        session.close()


class TestAPIWorkflow:
    """Smoke test: create place and project via the FastAPI HTTP layer."""

    def test_api_workflow(self) -> None:
        app = create_app(database_url="sqlite://")
        client = TestClient(app)

        # Create a place via POST /api/places
        create_response = client.post(
            "/api/places",
            json={
                "name": "Tokyo",
                "lat": TOKYO_LAT,
                "lon": TOKYO_LON,
                "source": "manual",
            },
        )
        assert create_response.status_code == 201
        place_data = create_response.json()
        assert place_data["name"] == "Tokyo"
        assert "id" in place_data
        place_id = place_data["id"]

        # Verify listing returns the created place
        list_response = client.get("/api/places")
        assert list_response.status_code == 200
        places = list_response.json()
        assert len(places) == 1
        assert places[0]["id"] == place_id
        assert places[0]["name"] == "Tokyo"

        # Create a project via POST /api/projects
        project_response = client.post(
            "/api/projects",
            json={
                "name": "Asia Trip",
                "map_type": "travel",
            },
        )
        assert project_response.status_code == 201
        project_data = project_response.json()
        assert project_data["name"] == "Asia Trip"
        assert "id" in project_data

        # Verify the project appears in the list
        project_id = project_data["id"]
        list_projects_response = client.get("/api/projects")
        assert list_projects_response.status_code == 200
        projects = list_projects_response.json()
        assert len(projects) == 1
        assert projects[0]["name"] == "Asia Trip"
        assert projects[0]["id"] == project_id


def test_album_help() -> None:
    result = runner.invoke(app, ["album", "--help"])
    assert result.exit_code == 0
    assert "album" in result.output.lower()


def test_album_list_help() -> None:
    result = runner.invoke(app, ["album", "list", "--help"])
    assert result.exit_code == 0


def test_album_import_help() -> None:
    result = runner.invoke(app, ["album", "import", "--help"])
    assert result.exit_code == 0
    assert "--eps" in result.output
    assert "--dry-run" in result.output
    assert "--name" in result.output
    assert "--min-samples" in result.output
    assert "--style" in result.output
