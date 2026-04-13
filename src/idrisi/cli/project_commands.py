"""CLI commands for managing projects."""

from __future__ import annotations

import typer

from idrisi.application.project_service import ProjectService
from idrisi.domain.value_objects import MapType
from idrisi.infrastructure.db.repository import SqlProjectRepository
from idrisi.infrastructure.db.session import create_engine_and_tables, get_session

project_app = typer.Typer(name="project", help="Manage projects.", no_args_is_help=True)

_DB_URL = "sqlite:///idrisi.db"


def get_project_service() -> ProjectService:
    """Create a ProjectService wired to the default SQLite database."""
    engine = create_engine_and_tables(_DB_URL)
    session = get_session(engine)
    repo = SqlProjectRepository(session)
    return ProjectService(repo)


@project_app.command("list")
def list_projects() -> None:
    """List all projects."""
    svc = get_project_service()
    projects = svc.list_all()
    if not projects:
        typer.echo("No projects found.")
        return
    for project in projects:
        typer.echo(f"{project.name} ({project.map_type.value})")


@project_app.command()
def create(
    name: str = typer.Argument(help="Project name."),
    map_type: str = typer.Option("travel", help="Map type: travel, region, or route."),
    description: str | None = typer.Option(None, help="Project description."),
) -> None:
    """Create a new project."""
    svc = get_project_service()
    mt = MapType(map_type)
    project = svc.create(name=name, map_type=mt, description=description)
    typer.echo(f"Created project: {project.name} ({project.id})")


@project_app.command()
def show(name: str = typer.Argument(help="Project name.")) -> None:
    """Show details of a project."""
    svc = get_project_service()
    project = svc.get_by_name(name)
    if project is None:
        typer.echo(f"Project not found: {name}")
        raise typer.Exit(code=1)
    typer.echo(f"Name: {project.name}")
    typer.echo(f"Type: {project.map_type.value}")
    typer.echo(f"Description: {project.description or '(none)'}")
    typer.echo(f"Places: {len(project.place_ids)}")
    typer.echo(f"Trips: {len(project.trip_ids)}")
    typer.echo(f"Regions: {len(project.region_ids)}")
