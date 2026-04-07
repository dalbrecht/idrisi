"""CLI render command for generating map outputs."""

from __future__ import annotations

from pathlib import Path

import typer

from voyages.application.project_service import ProjectService
from voyages.domain.value_objects import MapType, OutputFormat
from voyages.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlProjectRepository,
    SqlRegionRepository,
    SqlTripRepository,
)
from voyages.infrastructure.db.session import create_engine_and_tables, get_session
from voyages.infrastructure.renderer.engine import RenderEngine
from voyages.infrastructure.renderer.styles import load_style

_DB_URL = "sqlite:///voyages.db"


def get_render_dependencies() -> tuple[
    ProjectService, SqlPlaceRepository, SqlTripRepository, SqlRegionRepository, RenderEngine
]:
    """Create all dependencies needed for the render command."""
    engine = create_engine_and_tables(_DB_URL)
    session = get_session(engine)
    project_repo = SqlProjectRepository(session)
    place_repo = SqlPlaceRepository(session)
    trip_repo = SqlTripRepository(session)
    region_repo = SqlRegionRepository(session)
    project_service = ProjectService(project_repo)
    style = load_style("default")
    render_engine = RenderEngine(style)
    return project_service, place_repo, trip_repo, region_repo, render_engine


def render(
    project_name: str = typer.Argument(help="Name of the project to render."),
    output_format: str = typer.Option("png", "--format", help="Output format: png, svg, pdf, eps."),
    style: str = typer.Option("default", help="Map style name or path."),
    dpi: int = typer.Option(200, help="Output resolution in DPI."),
    width: int = typer.Option(1200, help="Output width in pixels."),
    output: str = typer.Option(".", help="Output directory."),
) -> None:
    """Render a map for the given project."""
    project_service, place_repo, trip_repo, region_repo, render_engine = get_render_dependencies()

    # Override style if non-default
    if style != "default":
        loaded_style = load_style(style)
        render_engine = RenderEngine(loaded_style)

    project = project_service.get_by_name(project_name)
    if project is None:
        typer.echo(f"Project not found: {project_name}")
        raise typer.Exit(code=1)

    fmt = OutputFormat(output_format)
    config = {"dpi": dpi, "width": width}
    output_dir = Path(output)
    output_path = str(output_dir / f"{project.name}{fmt.extension}")

    # Gather entities
    places = [place_repo.get(pid) for pid in project.place_ids]
    filtered_places = [p for p in places if p is not None]
    regions = [region_repo.get(rid) for rid in project.region_ids]
    filtered_regions = [r for r in regions if r is not None]

    if project.map_type == MapType.TRAVEL:
        result = render_engine.render_travel_map(
            filtered_places, filtered_regions, output_path, fmt, config
        )
    elif project.map_type == MapType.REGION:
        result = render_engine.render_region_map(
            filtered_places, filtered_regions, output_path, fmt, config
        )
    elif project.map_type == MapType.ROUTE:
        trips = [trip_repo.get(tid) for tid in project.trip_ids]
        filtered_trips = [t for t in trips if t is not None]
        if not filtered_trips:
            typer.echo("No trips found for route rendering.")
            raise typer.Exit(code=1)
        result = render_engine.render_route_map(
            filtered_trips[0], filtered_places, output_path, fmt, config
        )
    else:
        typer.echo(f"Unknown map type: {project.map_type}")
        raise typer.Exit(code=1)

    typer.echo(f"Rendered: {result}")
