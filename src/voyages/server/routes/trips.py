"""Trips API routes."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

if TYPE_CHECKING:
    from voyages.application.trip_service import TripService
    from voyages.domain.entities import Trip


class TripCreate(BaseModel):
    """Request body for creating a trip."""

    name: str
    description: str | None = None


class TripResponse(BaseModel):
    """Response body for a trip."""

    id: str
    name: str
    description: str | None
    start_date: str | None
    end_date: str | None


def _get_service(request: Request) -> TripService:
    from voyages.application.trip_service import TripService as _TripService  # noqa: PLC0415
    from voyages.infrastructure.db.repository import SqlTripRepository  # noqa: PLC0415

    session = request.state.db
    trip_repo = SqlTripRepository(session)
    return _TripService(trip_repo=trip_repo)


def _to_response(trip: Trip) -> TripResponse:
    return TripResponse(
        id=str(trip.id),
        name=trip.name,
        description=trip.description,
        start_date=trip.start_date.isoformat() if trip.start_date else None,
        end_date=trip.end_date.isoformat() if trip.end_date else None,
    )


def create_trips_router() -> APIRouter:
    """Create the trips API router."""
    router = APIRouter()

    @router.get("/trips")
    def list_trips(request: Request) -> list[TripResponse]:
        service = _get_service(request)
        return [_to_response(t) for t in service.list_all()]

    @router.post("/trips", status_code=201)
    def create_trip(request: Request, body: TripCreate) -> TripResponse:
        service = _get_service(request)
        trip = service.create(name=body.name, description=body.description)
        return _to_response(trip)

    @router.delete("/trips/{trip_id}", status_code=204)
    def delete_trip(request: Request, trip_id: str) -> Response:
        service = _get_service(request)
        service.delete(uuid.UUID(trip_id))
        return Response(status_code=204)

    return router
