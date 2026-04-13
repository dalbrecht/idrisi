"""CLI commands for managing trips."""

from __future__ import annotations

import typer

from idrisi.application.trip_service import TripService
from idrisi.infrastructure.db.repository import SqlTripRepository
from idrisi.infrastructure.db.session import create_engine_and_tables, get_session

trip_app = typer.Typer(name="trip", help="Manage trips.", no_args_is_help=True)

_DB_URL = "sqlite:///idrisi.db"


def get_trip_service() -> TripService:
    """Create a TripService wired to the default SQLite database."""
    engine = create_engine_and_tables(_DB_URL)
    session = get_session(engine)
    repo = SqlTripRepository(session)
    return TripService(repo)


@trip_app.command("list")
def list_trips() -> None:
    """List all trips."""
    svc = get_trip_service()
    trips = svc.list_all()
    if not trips:
        typer.echo("No trips found.")
        return
    for trip in trips:
        typer.echo(f"{trip.name} ({len(trip.stops)} stops)")


@trip_app.command()
def create(
    name: str = typer.Argument(help="Trip name."),
    description: str | None = typer.Option(None, help="Trip description."),
) -> None:
    """Create a new trip."""
    svc = get_trip_service()
    trip = svc.create(name=name, description=description)
    typer.echo(f"Created trip: {trip.name} ({trip.id})")
