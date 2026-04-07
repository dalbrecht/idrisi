from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from voyages.application.place_service import PlaceService
from voyages.domain.entities import Place

if TYPE_CHECKING:
    from voyages.domain.value_objects import Coordinates

PARIS_LAT = 48.8566
PARIS_LON = 2.3522
LONDON_LAT = 51.5074
LONDON_LON = -0.1278
EXPECTED_TWO = 2


class FakePlaceRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Place] = {}

    def get(self, place_id: uuid.UUID) -> Place | None:
        return self._store.get(place_id)

    def list_all(self) -> list[Place]:
        return list(self._store.values())

    def search_by_name(self, query: str) -> list[Place]:
        q = query.lower()
        return [p for p in self._store.values() if q in p.name.lower()]

    def save(self, place: Place) -> Place:
        self._store[place.id] = place
        return place

    def delete(self, place_id: uuid.UUID) -> None:
        self._store.pop(place_id, None)


class FakeGeocodingService:
    def __init__(self, results: list[Place] | None = None) -> None:
        self._results = results or []

    def search(self, query: str) -> list[Place]:
        return list(self._results)

    def reverse_geocode(self, coords: Coordinates) -> Place | None:
        return None


class TestPlaceService:
    def setup_method(self) -> None:
        self.repo = FakePlaceRepository()
        self.geocoding = FakeGeocodingService()
        self.service = PlaceService(place_repo=self.repo, geocoding=self.geocoding)

    def test_create_returns_place(self) -> None:
        place = self.service.create(name="Paris", lat=PARIS_LAT, lon=PARIS_LON, source="manual")
        assert place.name == "Paris"
        assert place.latitude == PARIS_LAT
        assert place.longitude == PARIS_LON
        assert place.source == "manual"
        assert place.id is not None

    def test_create_saves_to_repo(self) -> None:
        place = self.service.create(name="Paris", lat=PARIS_LAT, lon=PARIS_LON, source="manual")
        assert self.repo.get(place.id) is not None

    def test_create_with_optional_fields(self) -> None:
        place = self.service.create(
            name="Paris",
            lat=PARIS_LAT,
            lon=PARIS_LON,
            source="manual",
            country="France",
            admin1="Île-de-France",
            category="city",
            notes="Capital of France",
        )
        assert place.country == "France"
        assert place.admin1 == "Île-de-France"
        assert place.category == "city"
        assert place.notes == "Capital of France"

    def test_get_existing(self) -> None:
        created = self.service.create(name="Paris", lat=PARIS_LAT, lon=PARIS_LON, source="manual")
        fetched = self.service.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Paris"

    def test_get_nonexistent_returns_none(self) -> None:
        result = self.service.get(uuid.uuid4())
        assert result is None

    def test_list_all_empty(self) -> None:
        assert self.service.list_all() == []

    def test_list_all_returns_all_places(self) -> None:
        self.service.create(name="Paris", lat=PARIS_LAT, lon=PARIS_LON, source="manual")
        self.service.create(name="London", lat=LONDON_LAT, lon=LONDON_LON, source="manual")
        places = self.service.list_all()
        assert len(places) == EXPECTED_TWO

    def test_search_delegates_to_geocoding(self) -> None:
        geocoding_place = Place(
            id=uuid.uuid4(), name="Paris, France", latitude=PARIS_LAT, longitude=PARIS_LON,
            source="nominatim",
        )
        self.geocoding = FakeGeocodingService(results=[geocoding_place])
        self.service = PlaceService(place_repo=self.repo, geocoding=self.geocoding)

        results = self.service.search("Paris")
        assert len(results) == 1
        assert results[0].name == "Paris, France"

    def test_search_empty_results(self) -> None:
        results = self.service.search("Nonexistent City XYZ")
        assert results == []

    def test_update_place(self) -> None:
        place = self.service.create(name="Paris", lat=PARIS_LAT, lon=PARIS_LON, source="manual")
        place.notes = "Updated notes"
        updated = self.service.update(place)
        assert updated.notes == "Updated notes"
        fetched = self.repo.get(place.id)
        assert fetched is not None
        assert fetched.notes == "Updated notes"

    def test_delete_removes_place(self) -> None:
        place = self.service.create(name="Paris", lat=PARIS_LAT, lon=PARIS_LON, source="manual")
        self.service.delete(place.id)
        assert self.repo.get(place.id) is None

    def test_delete_nonexistent_does_not_raise(self) -> None:
        self.service.delete(uuid.uuid4())  # should not raise
