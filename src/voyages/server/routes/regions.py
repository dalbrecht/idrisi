"""Regions API routes."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

if TYPE_CHECKING:
    from voyages.application.region_service import RegionService
    from voyages.domain.entities import Region


class RegionCreate(BaseModel):
    """Request body for creating a region."""

    name: str
    region_type: str
    region_code: str | None = None


class RegionResponse(BaseModel):
    """Response body for a region."""

    id: str
    name: str
    region_type: str
    region_code: str | None


def _get_service(request: Request) -> RegionService:
    from voyages.application.region_service import (  # noqa: PLC0415
        RegionService as _RegionService,
    )
    from voyages.infrastructure.db.repository import (  # noqa: PLC0415
        SqlPlaceRepository,
        SqlRegionRepository,
    )

    session = request.state.db
    region_repo = SqlRegionRepository(session)
    place_repo = SqlPlaceRepository(session)
    return _RegionService(region_repo=region_repo, place_repo=place_repo)


def _to_response(region: Region) -> RegionResponse:
    return RegionResponse(
        id=str(region.id),
        name=region.name,
        region_type=region.region_type,
        region_code=region.region_code,
    )


def create_regions_router() -> APIRouter:
    """Create the regions API router."""
    router = APIRouter()

    @router.get("/regions")
    def list_regions(request: Request) -> list[RegionResponse]:
        service = _get_service(request)
        return [_to_response(r) for r in service.list_all()]

    @router.post("/regions", status_code=201)
    def create_region(request: Request, body: RegionCreate) -> RegionResponse:
        service = _get_service(request)
        region = service.create(
            name=body.name,
            region_type=body.region_type,
            region_code=body.region_code,
        )
        return _to_response(region)

    @router.delete("/regions/{region_id}", status_code=204)
    def delete_region(request: Request, region_id: str) -> Response:
        from voyages.domain.errors import BadRequestError, RegionNotFoundError  # noqa: PLC0415

        service = _get_service(request)
        try:
            entity_id = uuid.UUID(region_id)
        except ValueError:
            raise BadRequestError(f"Invalid UUID: {region_id}") from None
        if service.get(entity_id) is None:
            raise RegionNotFoundError(entity_id)
        service.delete(entity_id)
        return Response(status_code=204)

    return router
