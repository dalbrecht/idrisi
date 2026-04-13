"""CLI commands for importing data."""

from __future__ import annotations

from pathlib import Path

import typer

from idrisi.application.photo_service import PhotoService
from idrisi.infrastructure.db.repository import SqlPhotoRepository
from idrisi.infrastructure.db.session import create_engine_and_tables, get_session
from idrisi.infrastructure.exif.extractor import PillowExifService
from idrisi.infrastructure.geocoding.nominatim import NominatimGeocodingService

import_app = typer.Typer(name="import", help="Import external data.", no_args_is_help=True)

_DB_URL = "sqlite:///idrisi.db"


def get_import_dependencies() -> PhotoService:
    """Create a PhotoService wired to the default SQLite database."""
    engine = create_engine_and_tables(_DB_URL)
    session = get_session(engine)
    photo_repo = SqlPhotoRepository(session)
    exif_service = PillowExifService()
    geocoding = NominatimGeocodingService()
    return PhotoService(photo_repo, exif_service, geocoding)


@import_app.command()
def photos(
    path: str = typer.Argument(help="Directory containing photos to import."),
    trip: str | None = typer.Option(None, help="Trip ID to assign imported photos to."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without saving."),
) -> None:
    """Import geotagged photos from a directory."""
    svc = get_import_dependencies()
    directory = Path(path)

    if not directory.is_dir():
        typer.echo(f"Not a directory: {path}")
        raise typer.Exit(code=1)

    results = svc.import_from_directory(directory, dry_run=dry_run)

    if dry_run:
        typer.echo(f"[dry-run] Found {len(results)} geotagged photos.")
    else:
        typer.echo(f"Imported {len(results)} geotagged photos.")

    for photo in results:
        typer.echo(f"  {photo.file_path} ({photo.latitude}, {photo.longitude})")

    if trip:
        typer.echo(f"Trip assignment: {trip} (not yet implemented)")
