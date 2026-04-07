"""Render API routes."""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse


def _get_dependencies(request: Request) -> tuple[Any, ...]:
    """Create all dependencies needed for rendering."""
    from voyages.application.project_service import ProjectService  # noqa: PLC0415
    from voyages.infrastructure.db.repository import (  # noqa: PLC0415
        SqlPlaceRepository,
        SqlProjectRepository,
        SqlRegionRepository,
        SqlTripRepository,
    )
    from voyages.infrastructure.renderer.engine import RenderEngine  # noqa: PLC0415
    from voyages.infrastructure.renderer.styles import load_style  # noqa: PLC0415

    session = request.state.db
    project_repo = SqlProjectRepository(session)
    place_repo = SqlPlaceRepository(session)
    trip_repo = SqlTripRepository(session)
    region_repo = SqlRegionRepository(session)
    project_service = ProjectService(project_repo)
    style = load_style("default")
    render_engine = RenderEngine(style)
    return project_service, place_repo, trip_repo, region_repo, render_engine


def create_render_router() -> APIRouter:
    """Create the render API router."""
    router = APIRouter()

    @router.post("/render/{project_id}")
    def render_project(request: Request, project_id: str) -> FileResponse:
        from voyages.domain.value_objects import MapType, OutputFormat  # noqa: PLC0415

        project_service, place_repo, trip_repo, region_repo, render_engine = (
            _get_dependencies(request)
        )

        project = project_service.get(uuid.UUID(project_id))
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        fmt = OutputFormat.PNG
        config = {"dpi": 200, "width": 1200}

        # Gather entities
        places = [place_repo.get(pid) for pid in project.place_ids]
        filtered_places = [p for p in places if p is not None]
        regions = [region_repo.get(rid) for rid in project.region_ids]
        filtered_regions = [r for r in regions if r is not None]

        tmp_dir = tempfile.mkdtemp()
        output_path = str(
            Path(tmp_dir) / f"{project.name}{fmt.extension}",
        )

        if project.map_type == MapType.TRAVEL:
            render_engine.render_travel_map(
                filtered_places, filtered_regions, output_path, fmt, config,
            )
        elif project.map_type == MapType.REGION:
            render_engine.render_region_map(
                filtered_places, filtered_regions, output_path, fmt, config,
            )
        elif project.map_type == MapType.ROUTE:
            trips = [trip_repo.get(tid) for tid in project.trip_ids]
            filtered_trips = [t for t in trips if t is not None]
            if not filtered_trips:
                raise HTTPException(
                    status_code=400,
                    detail="No trips found for route rendering",
                )
            render_engine.render_route_map(
                filtered_trips[0],
                filtered_places,
                output_path,
                fmt,
                config,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown map type: {project.map_type}",
            )

        return FileResponse(
            output_path,
            media_type="image/png",
            filename=f"{project.name}{fmt.extension}",
        )

    return router
