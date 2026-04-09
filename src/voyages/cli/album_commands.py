"""CLI commands for macOS Photos album import."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from voyages.application.album_service import AlbumImportResult, AlbumService
from voyages.application.place_service import PlaceService
from voyages.application.project_service import ProjectService
from voyages.application.trip_service import TripService
from voyages.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlProjectRepository,
    SqlTripRepository,
)
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.geocoding.nominatim import NominatimGeocodingService
from voyages.infrastructure.photos.osxphotos_adapter import OsxPhotosAdapter

album_app = typer.Typer(name="album", help="Import from macOS Photos albums.", no_args_is_help=True)

console = Console()

_DB_URL = "sqlite:///voyages.db"


def get_album_dependencies() -> AlbumService:
    """Create an AlbumService wired to the default SQLite database."""
    engine = create_engine_and_tables(_DB_URL)
    session = get_session(engine)
    place_repo = SqlPlaceRepository(session)
    trip_repo = SqlTripRepository(session)
    project_repo = SqlProjectRepository(session)
    geocoding = NominatimGeocodingService()
    photos_library = OsxPhotosAdapter()

    place_svc = PlaceService(place_repo=place_repo, geocoding=geocoding)
    trip_svc = TripService(trip_repo=trip_repo)
    project_svc = ProjectService(project_repo=project_repo)

    return AlbumService(
        photos_library=photos_library,
        place_service=place_svc,
        trip_service=trip_svc,
        project_service=project_svc,
        geocoding=geocoding,
    )


@album_app.command(name="list")
def list_albums() -> None:
    """List all albums in the macOS Photos library."""
    svc = get_album_dependencies()
    albums = svc.list_albums()

    if not albums:
        console.print("No albums found in Photos library.")
        return

    table = Table(title="Photos Albums")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Photos", justify="right")

    for i, album in enumerate(albums, 1):
        table.add_row(str(i), album.title, str(album.photo_count))

    console.print(table)


@album_app.command(name="import")
def import_album(
    album_name: str | None = typer.Argument(
        None, help="Album name to import. Omit for interactive picker."
    ),
    name: str | None = typer.Option(None, "--name", help="Project name (defaults to album title)."),
    eps: float = typer.Option(0.5, "--eps", help="Cluster radius in kilometers."),
    min_samples: int = typer.Option(1, "--min-samples", help="Minimum photos per cluster."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without saving."),
    style: str = typer.Option("default", "--style", help="Map style to assign to the project."),
) -> None:
    """Import a Photos album as a Voyages route project."""
    svc = get_album_dependencies()
    albums = svc.list_albums()

    if not albums:
        console.print("No albums found in Photos library.")
        raise typer.Exit(code=1)

    if album_name is not None:
        matched = [a for a in albums if a.title == album_name]
        if not matched:
            console.print(f"Album '{album_name}' not found.")
            raise typer.Exit(code=1)
        selected = matched[0]
    else:
        import questionary  # noqa: PLC0415

        choices = [
            questionary.Choice(
                title=f"{a.title} ({a.photo_count} photos)",
                value=a,
            )
            for a in albums
        ]
        selected = questionary.select(
            "Select an album:",
            choices=choices,
        ).ask()

        if selected is None:
            raise typer.Exit(code=0)

    project_name = name or selected.title

    try:
        if dry_run:
            result = svc.preview_album(
                album_id=selected.id,
                project_name=project_name,
                total_album_photos=selected.photo_count,
                eps_km=eps,
                min_samples=min_samples,
            )
            _print_result(result, dry_run=True)
            return

        # Check for duplicate project name
        existing = svc.get_project_by_name(project_name)
        if existing is not None:
            overwrite = typer.confirm(
                f"Project '{project_name}' already exists. Overwrite?",
                default=False,
            )
            if not overwrite:
                raise typer.Exit(code=0)
            svc.delete_project(existing.id)

        result = svc.import_album(
            album_id=selected.id,
            project_name=project_name,
            total_album_photos=selected.photo_count,
            eps_km=eps,
            min_samples=min_samples,
            style=style,
        )
        _print_result(result)
    except ValueError as exc:
        console.print(f"Error: {exc}")
        raise typer.Exit(code=1) from None


def _print_result(result: AlbumImportResult, *, dry_run: bool = False) -> None:
    """Print the import result summary."""
    prefix = "[Dry run] " if dry_run else ""
    skipped = result.total_photos - result.geotagged_photos

    console.print()
    console.print(f"{prefix}Importing {result.total_photos} photos...")
    if skipped > 0:
        console.print(
            f"  Geotagged: {result.geotagged_photos} / {result.total_photos}"
            f" ({skipped} skipped \u2014 no GPS data)"
        )
    else:
        console.print(f"  Geotagged: {result.geotagged_photos} / {result.total_photos}")
    console.print(f"  Clusters: {result.cluster_count} stops identified")

    if not dry_run:
        console.print(f"  Places created: {result.cluster_count}")
        console.print(f'  Trip created: "{result.project_name}"')
        console.print(f'  Project created: "{result.project_name}" (ROUTE)')
        console.print()
        console.print(f'Done. Render with: voyages render "{result.project_name}"')
    else:
        console.print()
        table = Table(title="Clusters (preview)")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Name", style="bold")

        for i, pname in enumerate(result.place_names, 1):
            table.add_row(str(i), pname)

        console.print(table)
