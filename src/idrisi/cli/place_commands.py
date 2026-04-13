"""CLI commands for managing places."""

from __future__ import annotations

import typer

from idrisi.application.place_service import PlaceService
from idrisi.infrastructure.db.repository import SqlPlaceRepository
from idrisi.infrastructure.db.session import create_engine_and_tables, get_session
from idrisi.infrastructure.geocoding.nominatim import NominatimGeocodingService

place_app = typer.Typer(name="place", help="Manage places.", no_args_is_help=True)

_DB_URL = "sqlite:///idrisi.db"


def get_place_service() -> PlaceService:
    """Create a PlaceService wired to the default SQLite database."""
    engine = create_engine_and_tables(_DB_URL)
    session = get_session(engine)
    repo = SqlPlaceRepository(session)
    geocoding = NominatimGeocodingService()
    return PlaceService(repo, geocoding)


@place_app.command("list")
def list_places() -> None:
    """List all stored places."""
    svc = get_place_service()
    places = svc.list_all()
    if not places:
        typer.echo("No places found.")
        return
    for place in places:
        typer.echo(f"{place.name} ({place.latitude}, {place.longitude})")


@place_app.command()
def search(query: str = typer.Argument(help="Search query string.")) -> None:
    """Search for places using the geocoding service."""
    svc = get_place_service()
    results = svc.search(query)
    if not results:
        typer.echo("No results found.")
        return
    for place in results:
        typer.echo(f"{place.name} ({place.latitude}, {place.longitude})")


@place_app.command()
def add(
    name: str = typer.Option(..., help="Place name."),
    lat: float = typer.Option(..., help="Latitude."),
    lon: float = typer.Option(..., help="Longitude."),
    category: str | None = typer.Option(None, help="Place category."),
) -> None:
    """Add a new place."""
    svc = get_place_service()
    place = svc.create(name=name, lat=lat, lon=lon, source="cli", category=category)
    typer.echo(f"Created place: {place.name} ({place.id})")
