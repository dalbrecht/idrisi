from __future__ import annotations

import uuid

from idrisi.application.region_service import RegionService
from idrisi.domain.entities import Place, Region

EXPECTED_ONE = 1
EXPECTED_TWO = 2


class FakeRegionRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Region] = {}

    def get(self, region_id: uuid.UUID) -> Region | None:
        return self._store.get(region_id)

    def list_all(self) -> list[Region]:
        return list(self._store.values())

    def save(self, region: Region) -> Region:
        self._store[region.id] = region
        return region

    def delete(self, region_id: uuid.UUID) -> None:
        self._store.pop(region_id, None)


class FakePlaceRepository:
    def __init__(self, places: list[Place] | None = None) -> None:
        self._places = places or []

    def get(self, place_id: uuid.UUID) -> Place | None:
        return None

    def list_all(self) -> list[Place]:
        return list(self._places)

    def search_by_name(self, query: str) -> list[Place]:
        return []

    def save(self, place: Place) -> Place:
        return place

    def delete(self, place_id: uuid.UUID) -> None:
        pass


class TestRegionService:
    def setup_method(self) -> None:
        self.region_repo = FakeRegionRepository()
        self.place_repo = FakePlaceRepository()
        self.service = RegionService(region_repo=self.region_repo, place_repo=self.place_repo)

    def test_create_returns_region(self) -> None:
        region = self.service.create(name="Western Europe", region_type="continent")
        assert region.name == "Western Europe"
        assert region.region_type == "continent"
        assert region.id is not None
        assert region.region_code is None

    def test_create_with_region_code(self) -> None:
        region = self.service.create(name="France", region_type="country", region_code="FR")
        assert region.region_code == "FR"

    def test_create_saves_to_repo(self) -> None:
        region = self.service.create(name="France", region_type="country")
        assert self.region_repo.get(region.id) is not None

    def test_get_existing(self) -> None:
        created = self.service.create(name="France", region_type="country")
        fetched = self.service.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_nonexistent_returns_none(self) -> None:
        result = self.service.get(uuid.uuid4())
        assert result is None

    def test_list_all_empty(self) -> None:
        assert self.service.list_all() == []

    def test_list_all_returns_all_regions(self) -> None:
        self.service.create(name="France", region_type="country")
        self.service.create(name="Germany", region_type="country")
        assert len(self.service.list_all()) == EXPECTED_TWO

    def test_derive_from_places_creates_regions_for_each_country(self) -> None:
        places = [
            Place(
                id=uuid.uuid4(),
                name="Paris",
                latitude=48.85,
                longitude=2.35,
                source="manual",
                country="France",
            ),
            Place(
                id=uuid.uuid4(),
                name="Berlin",
                latitude=52.52,
                longitude=13.4,
                source="manual",
                country="Germany",
            ),
        ]
        self.place_repo = FakePlaceRepository(places=places)
        self.service = RegionService(region_repo=self.region_repo, place_repo=self.place_repo)

        regions = self.service.derive_from_places()
        country_names = {r.name for r in regions}
        assert "France" in country_names
        assert "Germany" in country_names
        assert len(regions) == EXPECTED_TWO

    def test_derive_from_places_deduplication(self) -> None:
        places = [
            Place(
                id=uuid.uuid4(),
                name="Paris",
                latitude=48.85,
                longitude=2.35,
                source="manual",
                country="France",
            ),
            Place(
                id=uuid.uuid4(),
                name="Lyon",
                latitude=45.75,
                longitude=4.83,
                source="manual",
                country="France",
            ),
            Place(
                id=uuid.uuid4(),
                name="Berlin",
                latitude=52.52,
                longitude=13.4,
                source="manual",
                country="Germany",
            ),
        ]
        self.place_repo = FakePlaceRepository(places=places)
        self.service = RegionService(region_repo=self.region_repo, place_repo=self.place_repo)

        regions = self.service.derive_from_places()
        assert len(regions) == EXPECTED_TWO

    def test_derive_from_places_skips_places_without_country(self) -> None:
        places = [
            Place(
                id=uuid.uuid4(),
                name="Unknown",
                latitude=0.0,
                longitude=0.0,
                source="manual",
                country=None,
            ),
            Place(
                id=uuid.uuid4(),
                name="Paris",
                latitude=48.85,
                longitude=2.35,
                source="manual",
                country="France",
            ),
        ]
        self.place_repo = FakePlaceRepository(places=places)
        self.service = RegionService(region_repo=self.region_repo, place_repo=self.place_repo)

        regions = self.service.derive_from_places()
        assert len(regions) == EXPECTED_ONE
        assert regions[0].name == "France"

    def test_derive_from_places_saves_to_repo(self) -> None:
        places = [
            Place(
                id=uuid.uuid4(),
                name="Paris",
                latitude=48.85,
                longitude=2.35,
                source="manual",
                country="France",
            ),
        ]
        self.place_repo = FakePlaceRepository(places=places)
        self.service = RegionService(region_repo=self.region_repo, place_repo=self.place_repo)

        regions = self.service.derive_from_places()
        assert len(self.region_repo.list_all()) >= len(regions)

    def test_derive_from_places_no_duplicate_in_repo(self) -> None:
        places = [
            Place(
                id=uuid.uuid4(),
                name="Paris",
                latitude=48.85,
                longitude=2.35,
                source="manual",
                country="France",
            ),
            Place(
                id=uuid.uuid4(),
                name="Lyon",
                latitude=45.75,
                longitude=4.83,
                source="manual",
                country="France",
            ),
        ]
        self.place_repo = FakePlaceRepository(places=places)
        self.service = RegionService(region_repo=self.region_repo, place_repo=self.place_repo)

        self.service.derive_from_places()
        all_regions = self.region_repo.list_all()
        france_regions = [r for r in all_regions if r.name == "France"]
        assert len(france_regions) == EXPECTED_ONE

    def test_delete_removes_region(self) -> None:
        region = self.service.create(name="France", region_type="country")
        self.service.delete(region.id)
        assert self.region_repo.get(region.id) is None

    def test_delete_nonexistent_does_not_raise(self) -> None:
        self.service.delete(uuid.uuid4())  # should not raise

    def test_derive_from_places_case_sensitive(self) -> None:
        """Verify that 'France' and 'france' are treated as different countries."""
        places = [
            Place(
                id=uuid.uuid4(),
                name="Paris",
                latitude=48.85,
                longitude=2.35,
                source="manual",
                country="France",
            ),
            Place(
                id=uuid.uuid4(),
                name="Lyon",
                latitude=45.76,
                longitude=4.83,
                source="manual",
                country="france",
            ),
        ]
        self.place_repo = FakePlaceRepository(places=places)
        self.service = RegionService(region_repo=self.region_repo, place_repo=self.place_repo)
        regions = self.service.derive_from_places()
        region_names = {r.name for r in regions}
        assert "France" in region_names
        assert "france" in region_names
        assert len(regions) == 2
