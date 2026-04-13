"""Projects API routes."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

if TYPE_CHECKING:
    from idrisi.application.project_service import ProjectService
    from idrisi.domain.entities import Project


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
    from idrisi.application.project_service import (  # noqa: PLC0415
        ProjectService as _ProjectService,
    )
    from idrisi.infrastructure.db.repository import SqlProjectRepository  # noqa: PLC0415

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
        from idrisi.domain.errors import BadRequestError  # noqa: PLC0415
        from idrisi.domain.value_objects import MapType  # noqa: PLC0415

        service = _get_service(request)
        try:
            map_type = MapType(body.map_type)
        except ValueError:
            raise BadRequestError(f"Invalid map type: {body.map_type!r}") from None
        project = service.create(
            name=body.name,
            map_type=map_type,
            description=body.description,
        )
        return _to_response(project)

    @router.delete("/projects/{project_id}", status_code=204)
    def delete_project(request: Request, project_id: str) -> Response:
        from idrisi.domain.errors import BadRequestError, ProjectNotFoundError  # noqa: PLC0415

        service = _get_service(request)
        try:
            entity_id = uuid.UUID(project_id)
        except ValueError:
            raise BadRequestError(f"Invalid UUID: {project_id}") from None
        if service.get(entity_id) is None:
            raise ProjectNotFoundError(entity_id)
        service.delete(entity_id)
        return Response(status_code=204)

    return router
