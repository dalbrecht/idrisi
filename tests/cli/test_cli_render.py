"""Tests for the render CLI command."""

from __future__ import annotations

import tempfile
import uuid
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from idrisi.cli import app
from idrisi.cli.render_commands import get_render_dependencies
from idrisi.domain.entities import Project
from idrisi.domain.value_objects import MapType

runner = CliRunner()


@patch("idrisi.cli.render_commands.get_render_dependencies")
def test_render_travel_map(mock_deps: MagicMock) -> None:
    project_service = MagicMock()
    place_repo = MagicMock()
    trip_repo = MagicMock()
    region_repo = MagicMock()
    render_engine = MagicMock()

    project = Project(
        id=uuid.uuid4(),
        name="world",
        map_type=MapType.TRAVEL,
        place_ids=[],
        region_ids=[],
        trip_ids=[],
    )
    project_service.get_by_name.return_value = project
    render_engine.render_travel_map.return_value = "./world.png"

    mock_deps.return_value = (
        project_service,
        place_repo,
        trip_repo,
        region_repo,
        render_engine,
    )

    result = runner.invoke(app, ["render", "world"])
    assert result.exit_code == 0
    assert "Rendered" in result.output
    render_engine.render_travel_map.assert_called_once()


@patch("idrisi.cli.render_commands.get_render_dependencies")
def test_render_project_not_found(mock_deps: MagicMock) -> None:
    project_service = MagicMock()
    place_repo = MagicMock()
    trip_repo = MagicMock()
    region_repo = MagicMock()
    render_engine = MagicMock()

    project_service.get_by_name.return_value = None

    mock_deps.return_value = (
        project_service,
        place_repo,
        trip_repo,
        region_repo,
        render_engine,
    )

    result = runner.invoke(app, ["render", "nonexistent"])
    assert result.exit_code == 1
    assert "not found" in result.output


@patch("idrisi.cli.render_commands.get_render_dependencies")
def test_render_region_map(mock_deps: MagicMock) -> None:
    project_service = MagicMock()
    place_repo = MagicMock()
    trip_repo = MagicMock()
    region_repo = MagicMock()
    render_engine = MagicMock()

    project = Project(
        id=uuid.uuid4(),
        name="europe",
        map_type=MapType.REGION,
        place_ids=[],
        region_ids=[],
        trip_ids=[],
    )
    project_service.get_by_name.return_value = project
    render_engine.render_region_map.return_value = "./europe.png"

    mock_deps.return_value = (
        project_service,
        place_repo,
        trip_repo,
        region_repo,
        render_engine,
    )

    result = runner.invoke(app, ["render", "europe"])
    assert result.exit_code == 0
    assert "Rendered" in result.output
    render_engine.render_region_map.assert_called_once()


@patch("idrisi.cli.render_commands.get_render_dependencies")
def test_render_route_map(mock_deps: MagicMock) -> None:
    project_service = MagicMock()
    place_repo = MagicMock()
    trip_repo = MagicMock()
    region_repo = MagicMock()
    render_engine = MagicMock()

    trip_id = uuid.uuid4()
    project = Project(
        id=uuid.uuid4(),
        name="roadtrip",
        map_type=MapType.ROUTE,
        place_ids=[],
        region_ids=[],
        trip_ids=[trip_id],
    )
    project_service.get_by_name.return_value = project
    mock_trip = MagicMock()
    trip_repo.get.return_value = mock_trip
    render_engine.render_route_map.return_value = "./roadtrip.png"

    mock_deps.return_value = (
        project_service,
        place_repo,
        trip_repo,
        region_repo,
        render_engine,
    )

    result = runner.invoke(app, ["render", "roadtrip"])
    assert result.exit_code == 0
    assert "Rendered" in result.output
    render_engine.render_route_map.assert_called_once()


@patch("idrisi.cli.render_commands.get_render_dependencies")
def test_render_route_map_no_trips(mock_deps: MagicMock) -> None:
    """Verifies that render exits with error when no trips are found for a route map."""
    project_service = MagicMock()
    place_repo = MagicMock()
    trip_repo = MagicMock()
    region_repo = MagicMock()
    render_engine = MagicMock()

    trip_id = uuid.uuid4()
    project = Project(
        id=uuid.uuid4(),
        name="notrips",
        map_type=MapType.ROUTE,
        place_ids=[],
        region_ids=[],
        trip_ids=[trip_id],
    )
    project_service.get_by_name.return_value = project
    # trip_repo.get returns None (trip not found)
    trip_repo.get.return_value = None

    mock_deps.return_value = (
        project_service,
        place_repo,
        trip_repo,
        region_repo,
        render_engine,
    )

    result = runner.invoke(app, ["render", "notrips"])
    assert result.exit_code == 1
    assert "No trips" in result.output


@patch("idrisi.cli.render_commands.get_render_dependencies")
def test_render_with_custom_style(mock_deps: MagicMock) -> None:
    """Verifies that passing --style overrides the default map style during rendering."""
    project_service = MagicMock()
    place_repo = MagicMock()
    trip_repo = MagicMock()
    region_repo = MagicMock()
    render_engine = MagicMock()

    project = Project(
        id=uuid.uuid4(),
        name="styled",
        map_type=MapType.TRAVEL,
        place_ids=[],
        region_ids=[],
        trip_ids=[],
    )
    project_service.get_by_name.return_value = project
    render_engine.render_travel_map.return_value = "./styled.png"

    mock_deps.return_value = (
        project_service,
        place_repo,
        trip_repo,
        region_repo,
        render_engine,
    )

    result = runner.invoke(app, ["render", "styled", "--style", "minimal"])
    assert result.exit_code == 0
    assert "Rendered" in result.output


def test_get_render_dependencies_creates_real_dependencies() -> None:
    """Verifies that the render dependencies factory returns five real dependency objects."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = f"{tmpdir}/render_test.db"
        with patch("idrisi.cli.render_commands._DB_URL", f"sqlite:///{db_path}"):
            result = get_render_dependencies()
            try:
                assert len(result) == 5
            finally:
                for dep in result:
                    close = getattr(dep, "close", None)
                    if callable(close):
                        close()
                    dispose = getattr(dep, "dispose", None)
                    if callable(dispose):
                        dispose()
