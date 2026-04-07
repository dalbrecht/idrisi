from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from voyages.domain.entities import Photo, Place, Project, Region, Trip, TripStop
from voyages.domain.value_objects import MapType

EIFFEL_LAT = 48.8584
EIFFEL_LON = 2.2945
PARIS_LAT = 48.8566
PARIS_LON = 2.3522
LONDON_LAT = 51.5074
LONDON_LON = -0.1278
BERLIN_LAT = 52.52
BERLIN_LON = 13.405


class TestPlace:
    def test_basic_creation(self) -> None:
        place_id = uuid.uuid4()
        place = Place(
            id=place_id,
            name="Paris",
            latitude=PARIS_LAT,
            longitude=PARIS_LON,
            source="manual",
        )
        assert place.id == place_id
        assert place.name == "Paris"
        assert place.source == "manual"

    def test_optional_fields_default_none(self) -> None:
        place = Place(
            id=uuid.uuid4(),
            name="London",
            latitude=LONDON_LAT,
            longitude=LONDON_LON,
            source="nominatim",
        )
        assert place.country is None
        assert place.admin1 is None
        assert place.category is None
        assert place.notes is None
        assert place.created_at is None
        assert place.updated_at is None

    def test_optional_fields_provided(self) -> None:
        now = datetime.now(tz=UTC)
        place = Place(
            id=uuid.uuid4(),
            name="Berlin",
            latitude=BERLIN_LAT,
            longitude=BERLIN_LON,
            source="manual",
            country="Germany",
            admin1="Berlin",
            category="city",
            notes="Capital city",
            created_at=now,
            updated_at=now,
        )
        assert place.country == "Germany"
        assert place.admin1 == "Berlin"
        assert place.category == "city"
        assert place.notes == "Capital city"
        assert place.created_at == now
        assert place.updated_at == now


class TestTripStop:
    def test_basic_creation(self) -> None:
        place_id = uuid.uuid4()
        stop = TripStop(place_id=place_id, position=1)
        assert stop.place_id == place_id
        assert stop.position == 1

    def test_optional_fields_default_none(self) -> None:
        stop = TripStop(place_id=uuid.uuid4(), position=0)
        assert stop.arrived_at is None
        assert stop.departed_at is None

    def test_optional_fields_provided(self) -> None:
        arrived = datetime(2024, 6, 1, 10, 0, tzinfo=UTC)
        departed = datetime(2024, 6, 3, 14, 0, tzinfo=UTC)
        stop = TripStop(
            place_id=uuid.uuid4(),
            position=2,
            arrived_at=arrived,
            departed_at=departed,
        )
        assert stop.arrived_at == arrived
        assert stop.departed_at == departed


class TestTrip:
    def test_basic_creation(self) -> None:
        trip_id = uuid.uuid4()
        trip = Trip(id=trip_id, name="Europe 2024")
        assert trip.id == trip_id
        assert trip.name == "Europe 2024"

    def test_optional_fields_default_none(self) -> None:
        trip = Trip(id=uuid.uuid4(), name="Asia Tour")
        assert trip.description is None
        assert trip.start_date is None
        assert trip.end_date is None

    def test_stops_default_empty_list(self) -> None:
        trip = Trip(id=uuid.uuid4(), name="Road Trip")
        assert trip.stops == []

    def test_stops_independent_between_instances(self) -> None:
        trip1 = Trip(id=uuid.uuid4(), name="Trip 1")
        trip2 = Trip(id=uuid.uuid4(), name="Trip 2")
        trip1.stops.append(TripStop(place_id=uuid.uuid4(), position=0))
        assert len(trip2.stops) == 0

    def test_optional_fields_provided(self) -> None:
        start = date(2024, 6, 1)
        end = date(2024, 6, 30)
        trip = Trip(
            id=uuid.uuid4(),
            name="Summer Trip",
            description="A great summer trip",
            start_date=start,
            end_date=end,
        )
        assert trip.description == "A great summer trip"
        assert trip.start_date == start
        assert trip.end_date == end


class TestRegion:
    def test_basic_creation(self) -> None:
        region_id = uuid.uuid4()
        region = Region(id=region_id, name="Western Europe", region_type="continent")
        assert region.id == region_id
        assert region.name == "Western Europe"
        assert region.region_type == "continent"

    def test_region_code_default_none(self) -> None:
        region = Region(id=uuid.uuid4(), name="France", region_type="country")
        assert region.region_code is None

    def test_region_code_provided(self) -> None:
        region = Region(
            id=uuid.uuid4(), name="France", region_type="country", region_code="FR"
        )
        assert region.region_code == "FR"


class TestProject:
    def test_basic_creation(self) -> None:
        project_id = uuid.uuid4()
        project = Project(
            id=project_id,
            name="My Travel Map",
            map_type=MapType.TRAVEL,
        )
        assert project.id == project_id
        assert project.name == "My Travel Map"
        assert project.map_type is MapType.TRAVEL

    def test_optional_description_default_none(self) -> None:
        project = Project(id=uuid.uuid4(), name="Test", map_type=MapType.REGION)
        assert project.description is None

    def test_list_fields_default_empty(self) -> None:
        project = Project(id=uuid.uuid4(), name="Test", map_type=MapType.ROUTE)
        assert project.config == {}
        assert project.place_ids == []
        assert project.trip_ids == []
        assert project.region_ids == []

    def test_list_fields_independent_between_instances(self) -> None:
        p1 = Project(id=uuid.uuid4(), name="P1", map_type=MapType.TRAVEL)
        p2 = Project(id=uuid.uuid4(), name="P2", map_type=MapType.TRAVEL)
        p1.place_ids.append(uuid.uuid4())
        assert len(p2.place_ids) == 0

    def test_description_provided(self) -> None:
        project = Project(
            id=uuid.uuid4(),
            name="Map",
            map_type=MapType.TRAVEL,
            description="A detailed travel map",
        )
        assert project.description == "A detailed travel map"


class TestPhoto:
    def test_basic_creation(self) -> None:
        photo_id = uuid.uuid4()
        photo = Photo(id=photo_id, file_path="/photos/paris.jpg")
        assert photo.id == photo_id
        assert photo.file_path == "/photos/paris.jpg"

    def test_optional_fields_default_none(self) -> None:
        photo = Photo(id=uuid.uuid4(), file_path="/photos/test.jpg")
        assert photo.latitude is None
        assert photo.longitude is None
        assert photo.taken_at is None
        assert photo.place_id is None
        assert photo.trip_id is None

    def test_optional_fields_provided(self) -> None:
        place_id = uuid.uuid4()
        trip_id = uuid.uuid4()
        taken = datetime(2024, 7, 15, 12, 0, tzinfo=UTC)
        photo = Photo(
            id=uuid.uuid4(),
            file_path="/photos/eiffel.jpg",
            latitude=EIFFEL_LAT,
            longitude=EIFFEL_LON,
            taken_at=taken,
            place_id=place_id,
            trip_id=trip_id,
        )
        assert photo.latitude == EIFFEL_LAT
        assert photo.longitude == EIFFEL_LON
        assert photo.taken_at == taken
        assert photo.place_id == place_id
        assert photo.trip_id == trip_id
