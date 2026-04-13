"""Tests for place, project, and trip CLI commands."""

from __future__ import annotations

import tempfile
import uuid
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from idrisi.cli import app
from idrisi.cli.place_commands import get_place_service
from idrisi.cli.project_commands import get_project_service
from idrisi.cli.trip_commands import get_trip_service
from idrisi.domain.entities import Place, Project, Trip
from idrisi.domain.value_objects import MapType

runner = CliRunner()


# ---------------------------------------------------------------------------
# Place commands
# ---------------------------------------------------------------------------


@patch("idrisi.cli.place_commands.get_place_service")
def test_place_list_empty(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.list_all.return_value = []
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["place", "list"])
    assert result.exit_code == 0
    assert "No places found" in result.output


@patch("idrisi.cli.place_commands.get_place_service")
def test_place_list_with_results(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.list_all.return_value = [
        Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="cli"),
    ]
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["place", "list"])
    assert result.exit_code == 0
    assert "Paris" in result.output


@patch("idrisi.cli.place_commands.get_place_service")
def test_place_search(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.search.return_value = [
        Place(id=uuid.uuid4(), name="Tokyo", latitude=35.68, longitude=139.69, source="nominatim"),
    ]
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["place", "search", "Tokyo"])
    assert result.exit_code == 0
    assert "Tokyo" in result.output
    svc.search.assert_called_once_with("Tokyo")


@patch("idrisi.cli.place_commands.get_place_service")
def test_place_search_no_results(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.search.return_value = []
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["place", "search", "Nowhere"])
    assert result.exit_code == 0
    assert "No results found" in result.output


@patch("idrisi.cli.place_commands.get_place_service")
def test_place_add(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    place = Place(id=uuid.uuid4(), name="Test", latitude=1.0, longitude=2.0, source="cli")
    svc.create.return_value = place
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["place", "add", "--name", "Test", "--lat", "1.0", "--lon", "2.0"])
    assert result.exit_code == 0
    assert "Created place" in result.output


# ---------------------------------------------------------------------------
# Project commands
# ---------------------------------------------------------------------------


@patch("idrisi.cli.project_commands.get_project_service")
def test_project_list_empty(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.list_all.return_value = []
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0
    assert "No projects found" in result.output


@patch("idrisi.cli.project_commands.get_project_service")
def test_project_list_with_results(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.list_all.return_value = [
        Project(id=uuid.uuid4(), name="Europe", map_type=MapType.TRAVEL),
    ]
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0
    assert "Europe" in result.output
    assert "travel" in result.output


@patch("idrisi.cli.project_commands.get_project_service")
def test_project_create(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    project = Project(id=uuid.uuid4(), name="Asia Trip", map_type=MapType.TRAVEL)
    svc.create.return_value = project
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["project", "create", "Asia Trip"])
    assert result.exit_code == 0
    assert "Created project" in result.output
    svc.create.assert_called_once()


@patch("idrisi.cli.project_commands.get_project_service")
def test_project_show(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    project = Project(
        id=uuid.uuid4(),
        name="Europe",
        map_type=MapType.TRAVEL,
        description="My Europe trip",
    )
    svc.get_by_name.return_value = project
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["project", "show", "Europe"])
    assert result.exit_code == 0
    assert "Europe" in result.output
    assert "travel" in result.output


@patch("idrisi.cli.project_commands.get_project_service")
def test_project_show_not_found(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.get_by_name.return_value = None
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["project", "show", "Nope"])
    assert result.exit_code == 1
    assert "not found" in result.output


# ---------------------------------------------------------------------------
# Trip commands
# ---------------------------------------------------------------------------


@patch("idrisi.cli.trip_commands.get_trip_service")
def test_trip_list_empty(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.list_all.return_value = []
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["trip", "list"])
    assert result.exit_code == 0
    assert "No trips found" in result.output


@patch("idrisi.cli.trip_commands.get_trip_service")
def test_trip_list_with_results(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    svc.list_all.return_value = [
        Trip(id=uuid.uuid4(), name="Road Trip", stops=[]),
    ]
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["trip", "list"])
    assert result.exit_code == 0
    assert "Road Trip" in result.output


@patch("idrisi.cli.trip_commands.get_trip_service")
def test_trip_create(mock_get_svc: MagicMock) -> None:
    svc = MagicMock()
    trip = Trip(id=uuid.uuid4(), name="Summer 2024", stops=[])
    svc.create.return_value = trip
    mock_get_svc.return_value = svc

    result = runner.invoke(app, ["trip", "create", "Summer 2024"])
    assert result.exit_code == 0
    assert "Created trip" in result.output
    svc.create.assert_called_once()


# ---------------------------------------------------------------------------
# Error path tests
# ---------------------------------------------------------------------------


class TestCliErrorPaths:
    """Test CLI commands with invalid input."""

    def test_place_add_missing_name(self) -> None:
        result = runner.invoke(app, ["place", "add", "--lat", "48.85", "--lon", "2.35"])
        assert result.exit_code != 0

    def test_place_add_missing_lat(self) -> None:
        result = runner.invoke(app, ["place", "add", "--name", "Paris", "--lon", "2.35"])
        assert result.exit_code != 0

    def test_place_add_missing_lon(self) -> None:
        result = runner.invoke(app, ["place", "add", "--name", "Paris", "--lat", "48.85"])
        assert result.exit_code != 0

    @patch("idrisi.cli.project_commands.get_project_service")
    def test_project_create_invalid_map_type(self, mock_get_svc: MagicMock) -> None:
        svc = MagicMock()
        mock_get_svc.return_value = svc
        result = runner.invoke(app, ["project", "create", "Test", "--map-type", "invalid"])
        assert result.exit_code != 0
        svc.create.assert_not_called()

    def test_trip_create_missing_name(self) -> None:
        result = runner.invoke(app, ["trip", "create"])
        assert result.exit_code != 0

    @patch("idrisi.cli.place_commands.get_place_service")
    def test_place_add_invalid_coordinates(self, mock_get_svc: MagicMock) -> None:
        """Document behavior when lat > 90 — CLI has no validation."""
        svc = MagicMock()
        place = Place(id=uuid.uuid4(), name="Bad", latitude=999.0, longitude=0.0, source="cli")
        svc.create.return_value = place
        mock_get_svc.return_value = svc
        result = runner.invoke(app, ["place", "add", "--name", "Bad", "--lat", "999", "--lon", "0"])
        # CLI currently accepts any float — no coordinate validation
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Factory function coverage tests
# ---------------------------------------------------------------------------


def test_get_place_service_creates_real_service() -> None:
    """Verify get_place_service wires up a real PlaceService."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = f"{tmpdir}/test.db"
        with patch("idrisi.cli.place_commands._DB_URL", f"sqlite:///{db_path}"):
            svc = get_place_service()
            assert svc is not None
            result = svc.list_all()
            assert result == []


def test_get_project_service_creates_real_service() -> None:
    """Verify get_project_service wires up a real ProjectService."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = f"{tmpdir}/test.db"
        with patch("idrisi.cli.project_commands._DB_URL", f"sqlite:///{db_path}"):
            svc = get_project_service()
            assert svc is not None
            result = svc.list_all()
            assert result == []


def test_get_trip_service_creates_real_service() -> None:
    """Verify get_trip_service wires up a real TripService."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = f"{tmpdir}/test.db"
        with patch("idrisi.cli.trip_commands._DB_URL", f"sqlite:///{db_path}"):
            svc = get_trip_service()
            assert svc is not None
            result = svc.list_all()
            assert result == []
