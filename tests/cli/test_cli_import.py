"""Tests for the import CLI commands."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from voyages.cli import app
from voyages.domain.entities import Photo

runner = CliRunner()


@patch("voyages.cli.import_commands.get_import_dependencies")
def test_import_photos_dry_run(mock_deps: MagicMock, tmp_path: object) -> None:
    svc = MagicMock()
    svc.import_from_directory.return_value = [
        Photo(
            id=uuid.uuid4(),
            file_path="/photos/img1.jpg",
            latitude=48.85,
            longitude=2.35,
        ),
    ]
    mock_deps.return_value = svc

    result = runner.invoke(app, ["import", "photos", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert "1 geotagged" in result.output


@patch("voyages.cli.import_commands.get_import_dependencies")
def test_import_photos(mock_deps: MagicMock, tmp_path: object) -> None:
    svc = MagicMock()
    svc.import_from_directory.return_value = [
        Photo(
            id=uuid.uuid4(),
            file_path="/photos/img1.jpg",
            latitude=48.85,
            longitude=2.35,
        ),
        Photo(
            id=uuid.uuid4(),
            file_path="/photos/img2.jpg",
            latitude=35.68,
            longitude=139.69,
        ),
    ]
    mock_deps.return_value = svc

    result = runner.invoke(app, ["import", "photos", str(tmp_path)])
    assert result.exit_code == 0
    assert "Imported 2 geotagged photos" in result.output


@patch("voyages.cli.import_commands.get_import_dependencies")
def test_import_photos_no_results(mock_deps: MagicMock, tmp_path: object) -> None:
    svc = MagicMock()
    svc.import_from_directory.return_value = []
    mock_deps.return_value = svc

    result = runner.invoke(app, ["import", "photos", str(tmp_path)])
    assert result.exit_code == 0
    assert "Imported 0 geotagged photos" in result.output


def test_import_photos_invalid_dir() -> None:
    result = runner.invoke(app, ["import", "photos", "/nonexistent/path/xyz"])
    assert result.exit_code == 1
    assert "Not a directory" in result.output


@patch("voyages.cli.import_commands.get_import_dependencies")
def test_import_photos_with_trip_option(mock_deps: MagicMock, tmp_path: object) -> None:
    """Covers import_commands.py line 55 (the --trip option message)."""
    svc = MagicMock()
    svc.import_from_directory.return_value = []
    mock_deps.return_value = svc

    result = runner.invoke(app, ["import", "photos", str(tmp_path), "--trip", "my-trip-id"])
    assert result.exit_code == 0
    assert "Trip assignment" in result.output
