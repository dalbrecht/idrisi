"""Tests for the album CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from voyages.application.album_service import AlbumImportResult
from voyages.cli import app
from voyages.domain.value_objects import AlbumSummary

runner = CliRunner()

EXPECTED_TWO = 2


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_list(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
        AlbumSummary(id="a2", title="Iceland", photo_count=128),
    ]
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "list"])
    assert result.exit_code == 0
    assert "Japan 2024" in result.output
    assert "347" in result.output
    assert "Iceland" in result.output
    assert "128" in result.output


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_list_empty(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = []
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "list"])
    assert result.exit_code == 0
    assert "No albums" in result.output


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_by_name(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.get_project_by_name.return_value = None
    svc.import_album.return_value = AlbumImportResult(
        project_name="Japan 2024",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=14,
        place_names=[f"Place {i}" for i in range(14)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024"])
    assert result.exit_code == 0
    assert "Japan 2024" in result.output
    assert "14" in result.output
    svc.import_album.assert_called_once()


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_not_found(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Nonexistent Album"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_dry_run(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.preview_album.return_value = AlbumImportResult(
        project_name="Japan 2024",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=14,
        place_names=[f"Place {i}" for i in range(14)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output.lower() or "Dry run" in result.output
    svc.preview_album.assert_called_once()
    svc.import_album.assert_not_called()


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_custom_eps(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.get_project_by_name.return_value = None
    svc.import_album.return_value = AlbumImportResult(
        project_name="Japan 2024",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=5,
        place_names=[f"Place {i}" for i in range(5)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024", "--eps", "2.0"])
    assert result.exit_code == 0
    svc.import_album.assert_called_once()
    call_kwargs = svc.import_album.call_args
    assert call_kwargs.kwargs.get("eps_km") == 2.0 or call_kwargs[1].get("eps_km") == 2.0


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_custom_name(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.get_project_by_name.return_value = None
    svc.import_album.return_value = AlbumImportResult(
        project_name="My Japan Trip",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=14,
        place_names=[f"Place {i}" for i in range(14)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024", "--name", "My Japan Trip"])
    assert result.exit_code == 0
    call_kwargs = svc.import_album.call_args
    assert (
        call_kwargs.kwargs.get("project_name") == "My Japan Trip"
        or call_kwargs[1].get("project_name") == "My Japan Trip"
    )


@patch("voyages.cli.album_commands.get_album_dependencies")
def test_album_import_style_flag(mock_deps: MagicMock) -> None:
    svc = MagicMock()
    svc.list_albums.return_value = [
        AlbumSummary(id="a1", title="Japan 2024", photo_count=347),
    ]
    svc.get_project_by_name.return_value = None
    svc.import_album.return_value = AlbumImportResult(
        project_name="Japan 2024",
        total_photos=347,
        geotagged_photos=312,
        cluster_count=14,
        place_names=[f"Place {i}" for i in range(14)],
    )
    mock_deps.return_value = svc

    result = runner.invoke(app, ["album", "import", "Japan 2024", "--style", "dark"])
    assert result.exit_code == 0
    call_kwargs = svc.import_album.call_args
    assert call_kwargs.kwargs.get("style") == "dark" or call_kwargs[1].get("style") == "dark"
