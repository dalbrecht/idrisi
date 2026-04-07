"""Places API routes."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

if TYPE_CHECKING:
    from voyages.application.place_service import PlaceService
    from voyages.domain.entities import Place


class PlaceCreate(BaseModel):
    """Request body for creating a place."""

    name: str
    lat: float
    lon: float
    source: str
    country: str | None = None
    admin1: str | None = None
    category: str | None = None
    notes: str | None = None


class PlaceResponse(BaseModel):
    """Response body for a place."""

    id: str
    name: str
    lat: float
    lon: float
    country: str | None
    admin1: str | None
    category: str | None
    notes: str | None
    source: str


def _get_service(request: Request) -> PlaceService:
    from voyages.application.place_service import PlaceService as _PlaceService  # noqa: PLC0415
    from voyages.infrastructure.db.repository import SqlPlaceRepository  # noqa: PLC0415
    from voyages.infrastructure.geocoding.nominatim import (  # noqa: PLC0415
        NominatimGeocodingService,
    )

    session = request.state.db
    place_repo = SqlPlaceRepository(session)
    geocoding = NominatimGeocodingService()
    return _PlaceService(place_repo=place_repo, geocoding=geocoding)


def _to_response(place: Place) -> PlaceResponse:
    return PlaceResponse(
        id=str(place.id),
        name=place.name,
        lat=place.latitude,
        lon=place.longitude,
        country=place.country,
        admin1=place.admin1,
        category=place.category,
        notes=place.notes,
        source=place.source,
    )


def create_places_router() -> APIRouter:
    """Create the places API router."""
    router = APIRouter()

    @router.get("/places")
    def list_places(request: Request) -> list[PlaceResponse]:
        service = _get_service(request)
        return [_to_response(p) for p in service.list_all()]

    @router.post("/places", status_code=201)
    def create_place(request: Request, body: PlaceCreate) -> PlaceResponse:
        service = _get_service(request)
        place = service.create(
            name=body.name,
            lat=body.lat,
            lon=body.lon,
            source=body.source,
            country=body.country,
            admin1=body.admin1,
            category=body.category,
            notes=body.notes,
        )
        return _to_response(place)

    @router.get("/places/search")
    def search_places(request: Request, q: str = "") -> list[PlaceResponse]:
        from voyages.infrastructure.db.repository import SqlPlaceRepository  # noqa: PLC0415

        session = request.state.db
        place_repo = SqlPlaceRepository(session)
        results = place_repo.search_by_name(q)
        return [_to_response(p) for p in results]

    @router.delete("/places/{place_id}", status_code=204)
    def delete_place(request: Request, place_id: str) -> Response:
        service = _get_service(request)
        service.delete(uuid.UUID(place_id))
        return Response(status_code=204)

    return router
