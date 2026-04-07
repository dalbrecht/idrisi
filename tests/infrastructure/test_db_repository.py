"""Tests for SQLAlchemy repository implementations."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

import pytest

from voyages.domain.entities import Photo, Place, Project, Region, Trip, TripStop
from voyages.domain.value_objects import MapType
from voyages.infrastructure.db.repository import (
    SqlPhotoRepository,
    SqlPlaceRepository,
    SqlProjectRepository,
    SqlRegionRepository,
    SqlTripRepository,
)
from voyages.infrastructure.db.session import create_engine_and_tables, get_session


@pytest.fixture
def engine():
    return create_engine_and_tables("sqlite:///:memory:")


@pytest.fixture
def session(engine):
    s = get_session(engine)
    yield s
    s.close()


# ---- Place ----


class TestSqlPlaceRepository:
    def test_save_and_get(self, session) -> None:
        repo = SqlPlaceRepository(session)
        place = Place(
            id=uuid4(),
            name="Tokyo",
            latitude=35.6762,
            longitude=139.6503,
            source="manual",
            country="Japan",
            admin1="Tokyo",
        )
        repo.save(place)
        loaded = repo.get(place.id)
        assert loaded is not None
        assert loaded.name == "Tokyo"
        assert loaded.country == "Japan"

    def test_list_all(self, session) -> None:
        repo = SqlPlaceRepository(session)
        repo.save(Place(id=uuid4(), name="A", latitude=0, longitude=0, source="test"))
        repo.save(Place(id=uuid4(), name="B", latitude=1, longitude=1, source="test"))
        assert len(repo.list_all()) == 2

    def test_search_by_name(self, session) -> None:
        repo = SqlPlaceRepository(session)
        repo.save(Place(id=uuid4(), name="Paris", latitude=0, longitude=0, source="test"))
        repo.save(Place(id=uuid4(), name="Parma", latitude=0, longitude=0, source="test"))
        repo.save(Place(id=uuid4(), name="London", latitude=0, longitude=0, source="test"))
        results = repo.search_by_name("par")
        assert len(results) == 2

    def test_delete(self, session) -> None:
        repo = SqlPlaceRepository(session)
        pid = uuid4()
        repo.save(Place(id=pid, name="Gone", latitude=0, longitude=0, source="test"))
        repo.delete(pid)
        assert repo.get(pid) is None

    def test_upsert(self, session) -> None:
        repo = SqlPlaceRepository(session)
        pid = uuid4()
        repo.save(Place(id=pid, name="V1", latitude=0, longitude=0, source="test"))
        repo.save(Place(id=pid, name="V2", latitude=1, longitude=1, source="test"))
        loaded = repo.get(pid)
        assert loaded is not None
        assert loaded.name == "V2"
        assert len(repo.list_all()) == 1


# ---- Trip ----


class TestSqlTripRepository:
    def test_save_and_get_with_stops(self, session) -> None:
        place_repo = SqlPlaceRepository(session)
        p1 = Place(id=uuid4(), name="Start", latitude=0, longitude=0, source="test")
        p2 = Place(id=uuid4(), name="End", latitude=1, longitude=1, source="test")
        place_repo.save(p1)
        place_repo.save(p2)

        repo = SqlTripRepository(session)
        trip = Trip(
            id=uuid4(),
            name="Road Trip",
            description="Cross country",
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 15),
            stops=[
                TripStop(place_id=p1.id, position=0),
                TripStop(place_id=p2.id, position=1),
            ],
        )
        repo.save(trip)
        loaded = repo.get(trip.id)
        assert loaded is not None
        assert loaded.name == "Road Trip"
        assert len(loaded.stops) == 2
        assert loaded.stops[0].place_id == p1.id
        assert loaded.stops[1].place_id == p2.id

    def test_list_all(self, session) -> None:
        repo = SqlTripRepository(session)
        repo.save(Trip(id=uuid4(), name="T1"))
        repo.save(Trip(id=uuid4(), name="T2"))
        assert len(repo.list_all()) == 2

    def test_delete(self, session) -> None:
        repo = SqlTripRepository(session)
        tid = uuid4()
        repo.save(Trip(id=tid, name="Delete Me"))
        repo.delete(tid)
        assert repo.get(tid) is None


# ---- Region ----


class TestSqlRegionRepository:
    def test_save_and_get(self, session) -> None:
        repo = SqlRegionRepository(session)
        region = Region(
            id=uuid4(),
            name="Bavaria",
            region_type="state",
            region_code="DE-BY",
        )
        repo.save(region)
        loaded = repo.get(region.id)
        assert loaded is not None
        assert loaded.name == "Bavaria"
        assert loaded.region_code == "DE-BY"

    def test_list_all(self, session) -> None:
        repo = SqlRegionRepository(session)
        repo.save(Region(id=uuid4(), name="R1", region_type="country"))
        repo.save(Region(id=uuid4(), name="R2", region_type="state"))
        assert len(repo.list_all()) == 2

    def test_delete(self, session) -> None:
        repo = SqlRegionRepository(session)
        rid = uuid4()
        repo.save(Region(id=rid, name="Gone", region_type="country"))
        repo.delete(rid)
        assert repo.get(rid) is None


# ---- Project ----


class TestSqlProjectRepository:
    def test_save_and_get_with_associations(self, session) -> None:
        # Prerequisite entities
        place_repo = SqlPlaceRepository(session)
        trip_repo = SqlTripRepository(session)
        region_repo = SqlRegionRepository(session)

        p = Place(id=uuid4(), name="P", latitude=0, longitude=0, source="test")
        t = Trip(id=uuid4(), name="T")
        r = Region(id=uuid4(), name="R", region_type="country")
        place_repo.save(p)
        trip_repo.save(t)
        region_repo.save(r)

        repo = SqlProjectRepository(session)
        project = Project(
            id=uuid4(),
            name="My Map",
            map_type=MapType.TRAVEL,
            description="A travel map",
            config={"style": "vintage"},
            place_ids=[p.id],
            trip_ids=[t.id],
            region_ids=[r.id],
        )
        repo.save(project)

        loaded = repo.get(project.id)
        assert loaded is not None
        assert loaded.name == "My Map"
        assert loaded.map_type == MapType.TRAVEL
        assert loaded.config == {"style": "vintage"}
        assert p.id in loaded.place_ids
        assert t.id in loaded.trip_ids
        assert r.id in loaded.region_ids

    def test_get_by_name(self, session) -> None:
        repo = SqlProjectRepository(session)
        project = Project(
            id=uuid4(),
            name="Unique Name",
            map_type=MapType.REGION,
        )
        repo.save(project)
        loaded = repo.get_by_name("Unique Name")
        assert loaded is not None
        assert loaded.id == project.id

    def test_get_by_name_not_found(self, session) -> None:
        repo = SqlProjectRepository(session)
        assert repo.get_by_name("Nonexistent") is None

    def test_list_all(self, session) -> None:
        repo = SqlProjectRepository(session)
        repo.save(Project(id=uuid4(), name="P1", map_type=MapType.TRAVEL))
        repo.save(Project(id=uuid4(), name="P2", map_type=MapType.ROUTE))
        assert len(repo.list_all()) == 2

    def test_delete(self, session) -> None:
        repo = SqlProjectRepository(session)
        pid = uuid4()
        repo.save(Project(id=pid, name="Delete", map_type=MapType.TRAVEL))
        repo.delete(pid)
        assert repo.get(pid) is None


# ---- Photo ----


class TestSqlPhotoRepository:
    def test_save_and_get(self, session) -> None:
        repo = SqlPhotoRepository(session)
        photo = Photo(
            id=uuid4(),
            file_path="/photos/sunset.jpg",
            latitude=48.8566,
            longitude=2.3522,
            taken_at=datetime(2024, 7, 4, 18, 30, 0, tzinfo=UTC),
        )
        repo.save(photo)
        loaded = repo.get(photo.id)
        assert loaded is not None
        assert loaded.file_path == "/photos/sunset.jpg"
        assert loaded.latitude == pytest.approx(48.8566)

    def test_list_by_trip(self, session) -> None:
        # Need a trip first
        trip_repo = SqlTripRepository(session)
        t = Trip(id=uuid4(), name="Trip")
        trip_repo.save(t)

        repo = SqlPhotoRepository(session)
        repo.save(Photo(id=uuid4(), file_path="/a.jpg", trip_id=t.id))
        repo.save(Photo(id=uuid4(), file_path="/b.jpg", trip_id=t.id))
        repo.save(Photo(id=uuid4(), file_path="/c.jpg"))  # no trip

        results = repo.list_by_trip(t.id)
        assert len(results) == 2

    def test_delete(self, session) -> None:
        repo = SqlPhotoRepository(session)
        pid = uuid4()
        repo.save(Photo(id=pid, file_path="/gone.jpg"))
        repo.delete(pid)
        assert repo.get(pid) is None
