"""Projects API routes."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

if TYPE_CHECKING:
    from voyages.application.project_service import ProjectService
    from voyages.domain.entities import Project


class ProjectCreate(BaseModel):
    """Request body for creating a project."""

    name: str
    map_type: str
    description: str | None = None


class ProjectResponse(BaseModel):
    """Response body for a project."""

    id: str
    name: str
    description: str | None
    map_type: str


def _get_service(request: Request) -> ProjectService:
    from voyages.application.project_service import (  # noqa: PLC0415
        ProjectService as _ProjectService,
    )
    from voyages.infrastructure.db.repository import SqlProjectRepository  # noqa: PLC0415

    session = request.state.db
    project_repo = SqlProjectRepository(session)
    return _ProjectService(project_repo=project_repo)


def _to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        map_type=project.map_type.value,
    )


def create_projects_router() -> APIRouter:
    """Create the projects API router."""
    router = APIRouter()

    @router.get("/projects")
    def list_projects(request: Request) -> list[ProjectResponse]:
        service = _get_service(request)
        return [_to_response(p) for p in service.list_all()]

    @router.post("/projects", status_code=201)
    def create_project(request: Request, body: ProjectCreate) -> ProjectResponse:
        from voyages.domain.value_objects import MapType  # noqa: PLC0415

        service = _get_service(request)
        project = service.create(
            name=body.name,
            map_type=MapType(body.map_type),
            description=body.description,
        )
        return _to_response(project)

    @router.delete("/projects/{project_id}", status_code=204)
    def delete_project(request: Request, project_id: str) -> Response:
        service = _get_service(request)
        service.delete(uuid.UUID(project_id))
        return Response(status_code=204)

    return router
