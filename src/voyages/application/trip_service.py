from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from voyages.domain.entities import Trip, TripStop
from voyages.domain.errors import TripNotFoundError

if TYPE_CHECKING:
    from datetime import date, datetime

    from voyages.application.interfaces import TripRepository


class TripService:
    """Application service for managing Trips and their stops."""

    def __init__(self, trip_repo: TripRepository) -> None:
        self._trip_repo = trip_repo

    def create(
        self,
        name: str,
        description: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Trip:
        """Create a new Trip and persist it."""
        trip = Trip(
            id=uuid.uuid4(),
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )
        return self._trip_repo.save(trip)

    def get(self, trip_id: uuid.UUID) -> Trip | None:
        """Return the Trip with the given ID, or None if not found."""
        return self._trip_repo.get(trip_id)

    def list_all(self) -> list[Trip]:
        """Return all stored Trips."""
        return self._trip_repo.list_all()

    def add_stop(
        self,
        trip_id: uuid.UUID,
        place_id: uuid.UUID,
        arrived_at: datetime | None = None,
        departed_at: datetime | None = None,
    ) -> Trip:
        """Add a stop to the given trip, auto-assigning position."""
        trip = self._trip_repo.get(trip_id)
        if trip is None:
            raise TripNotFoundError(trip_id)
        position = len(trip.stops)
        stop = TripStop(
            place_id=place_id,
            position=position,
            arrived_at=arrived_at,
            departed_at=departed_at,
        )
        trip.stops.append(stop)
        return self._trip_repo.save(trip)

    def remove_stop(self, trip_id: uuid.UUID, place_id: uuid.UUID) -> Trip:
        """Remove a stop from the trip and renumber remaining positions."""
        trip = self._trip_repo.get(trip_id)
        if trip is None:
            raise TripNotFoundError(trip_id)
        trip.stops = [s for s in trip.stops if s.place_id != place_id]
        for i, stop in enumerate(trip.stops):
            stop.position = i
        return self._trip_repo.save(trip)

    def reorder_stops(self, trip_id: uuid.UUID, place_ids: list[uuid.UUID]) -> Trip:
        """Reorder trip stops according to the given list of place IDs."""
        trip = self._trip_repo.get(trip_id)
        if trip is None:
            raise TripNotFoundError(trip_id)
        stop_map = {s.place_id: s for s in trip.stops}
        reordered: list[TripStop] = []
        for position, pid in enumerate(place_ids):
            if pid in stop_map:
                stop = stop_map[pid]
                stop.position = position
                reordered.append(stop)
        trip.stops = reordered
        return self._trip_repo.save(trip)

    def delete(self, trip_id: uuid.UUID) -> None:
        """Delete the Trip with the given ID."""
        self._trip_repo.delete(trip_id)
