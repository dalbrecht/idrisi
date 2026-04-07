from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

import pytest

from voyages.application.trip_service import TripService
from voyages.domain.errors import TripNotFoundError

if TYPE_CHECKING:
    from voyages.domain.entities import Trip

PARIS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
LONDON_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
BERLIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
EXPECTED_TWO = 2
EXPECTED_THREE = 3


class FakeTripRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Trip] = {}

    def get(self, trip_id: uuid.UUID) -> Trip | None:
        return self._store.get(trip_id)

    def list_all(self) -> list[Trip]:
        return list(self._store.values())

    def save(self, trip: Trip) -> Trip:
        self._store[trip.id] = trip
        return trip

    def delete(self, trip_id: uuid.UUID) -> None:
        self._store.pop(trip_id, None)


class TestTripService:
    def setup_method(self) -> None:
        self.repo = FakeTripRepository()
        self.service = TripService(trip_repo=self.repo)

    def test_create_returns_trip(self) -> None:
        trip = self.service.create(name="Europe 2024")
        assert trip.name == "Europe 2024"
        assert trip.id is not None
        assert trip.stops == []

    def test_create_with_optional_fields(self) -> None:
        start = date(2024, 6, 1)
        end = date(2024, 6, 30)
        trip = self.service.create(
            name="Summer Trip",
            description="A great summer",
            start_date=start,
            end_date=end,
        )
        assert trip.description == "A great summer"
        assert trip.start_date == start
        assert trip.end_date == end

    def test_create_saves_to_repo(self) -> None:
        trip = self.service.create(name="Europe 2024")
        assert self.repo.get(trip.id) is not None

    def test_get_existing(self) -> None:
        created = self.service.create(name="Europe 2024")
        fetched = self.service.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_nonexistent_returns_none(self) -> None:
        result = self.service.get(uuid.uuid4())
        assert result is None

    def test_list_all_empty(self) -> None:
        assert self.service.list_all() == []

    def test_list_all_returns_all_trips(self) -> None:
        self.service.create(name="Trip 1")
        self.service.create(name="Trip 2")
        assert len(self.service.list_all()) == EXPECTED_TWO

    def test_add_stop_assigns_position_zero(self) -> None:
        trip = self.service.create(name="Europe 2024")
        updated = self.service.add_stop(trip.id, PARIS_ID)
        assert len(updated.stops) == 1
        assert updated.stops[0].place_id == PARIS_ID
        assert updated.stops[0].position == 0

    def test_add_multiple_stops_auto_position(self) -> None:
        trip = self.service.create(name="Europe 2024")
        self.service.add_stop(trip.id, PARIS_ID)
        self.service.add_stop(trip.id, LONDON_ID)
        updated = self.service.add_stop(trip.id, BERLIN_ID)
        assert len(updated.stops) == EXPECTED_THREE
        positions = [s.position for s in updated.stops]
        assert positions == [0, 1, EXPECTED_TWO]

    def test_add_stop_with_timestamps(self) -> None:
        trip = self.service.create(name="Europe 2024")
        arrived = datetime(2024, 6, 1, 10, 0, tzinfo=UTC)
        departed = datetime(2024, 6, 5, 10, 0, tzinfo=UTC)
        updated = self.service.add_stop(trip.id, PARIS_ID, arrived_at=arrived, departed_at=departed)
        stop = updated.stops[0]
        assert stop.arrived_at == arrived
        assert stop.departed_at == departed

    def test_add_stop_trip_not_found_raises(self) -> None:
        with pytest.raises(TripNotFoundError):
            self.service.add_stop(uuid.uuid4(), PARIS_ID)

    def test_remove_stop(self) -> None:
        trip = self.service.create(name="Europe 2024")
        self.service.add_stop(trip.id, PARIS_ID)
        self.service.add_stop(trip.id, LONDON_ID)
        updated = self.service.remove_stop(trip.id, PARIS_ID)
        assert len(updated.stops) == 1
        assert updated.stops[0].place_id == LONDON_ID

    def test_remove_stop_renumbers_positions(self) -> None:
        trip = self.service.create(name="Europe 2024")
        self.service.add_stop(trip.id, PARIS_ID)
        self.service.add_stop(trip.id, LONDON_ID)
        self.service.add_stop(trip.id, BERLIN_ID)
        updated = self.service.remove_stop(trip.id, LONDON_ID)
        positions = [s.position for s in updated.stops]
        assert positions == [0, 1]

    def test_remove_stop_trip_not_found_raises(self) -> None:
        with pytest.raises(TripNotFoundError):
            self.service.remove_stop(uuid.uuid4(), PARIS_ID)

    def test_reorder_stops(self) -> None:
        trip = self.service.create(name="Europe 2024")
        self.service.add_stop(trip.id, PARIS_ID)
        self.service.add_stop(trip.id, LONDON_ID)
        self.service.add_stop(trip.id, BERLIN_ID)
        # Reorder: Berlin first, then Paris, then London
        updated = self.service.reorder_stops(trip.id, [BERLIN_ID, PARIS_ID, LONDON_ID])
        assert updated.stops[0].place_id == BERLIN_ID
        assert updated.stops[0].position == 0
        assert updated.stops[1].place_id == PARIS_ID
        assert updated.stops[1].position == 1
        assert updated.stops[EXPECTED_TWO].place_id == LONDON_ID
        assert updated.stops[EXPECTED_TWO].position == EXPECTED_TWO

    def test_reorder_stops_with_unknown_place_id(self) -> None:
        """Reorder with place_ids not in the trip — document actual behavior."""
        trip = self.service.create(name="Test Trip")
        known_place = uuid.uuid4()
        self.service.add_stop(trip.id, known_place)
        unknown_place = uuid.uuid4()
        updated = self.service.reorder_stops(trip.id, [unknown_place, known_place])
        known_stops = [s for s in updated.stops if s.place_id == known_place]
        assert len(known_stops) == 1

    def test_reorder_stops_trip_not_found_raises(self) -> None:
        with pytest.raises(TripNotFoundError):
            self.service.reorder_stops(uuid.uuid4(), [PARIS_ID])

    def test_delete_removes_trip(self) -> None:
        trip = self.service.create(name="Europe 2024")
        self.service.delete(trip.id)
        assert self.repo.get(trip.id) is None

    def test_delete_nonexistent_does_not_raise(self) -> None:
        self.service.delete(uuid.uuid4())  # should not raise
