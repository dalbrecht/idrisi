from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from voyages.application.album_service import AlbumImportResult, AlbumService
from voyages.application.place_service import PlaceService
from voyages.application.project_service import ProjectService
from voyages.application.trip_service import TripService
from voyages.domain.entities import Place, Trip
from voyages.domain.value_objects import AlbumSummary, GeotaggedPhoto, MapType

if TYPE_CHECKING:
    from voyages.domain.value_objects import Coordinates

TOKYO_LAT = 35.6762
TOKYO_LON = 139.6503
OSAKA_LAT = 34.6937
OSAKA_LON = 135.5023
EXPECTED_TWO = 2
EXPECTED_THREE = 3


class FakePhotosLibrary:
    def __init__(
        self,
        albums: list[AlbumSummary] | None = None,
        photos: dict[str, list[GeotaggedPhoto]] | None = None,
    ) -> None:
        self._albums = albums or []
        self._photos = photos or {}

    def list_albums(self) -> list[AlbumSummary]:
        return list(self._albums)

    def get_album_photos(self, album_id: str) -> list[GeotaggedPhoto]:
        return list(self._photos.get(album_id, []))


class FakePlaceRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Place] = {}

    def get(self, place_id: uuid.UUID) -> Place | None:
        return self._store.get(place_id)

    def list_all(self) -> list[Place]:
        return list(self._store.values())

    def search_by_name(self, query: str) -> list[Place]:
        return []

    def save(self, place: Place) -> Place:
        self._store[place.id] = place
        return place

    def delete(self, place_id: uuid.UUID) -> None:
        self._store.pop(place_id, None)


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


class FakeProjectRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, object] = {}
        self._by_name: dict[str, object] = {}

    def get(self, project_id: uuid.UUID) -> object | None:
        return self._store.get(project_id)

    def get_by_name(self, name: str) -> object | None:
        return self._by_name.get(name)

    def list_all(self) -> list[object]:
        return list(self._store.values())

    def save(self, project: object) -> object:
        self._store[project.id] = project  # type: ignore[union-attr]
        self._by_name[project.name] = project  # type: ignore[union-attr]
        return project

    def delete(self, project_id: uuid.UUID) -> None:
        self._store.pop(project_id, None)


class FakeGeocodingService:
    def __init__(self) -> None:
        self._call_count = 0

    def search(self, query: str) -> list[Place]:
        return []

    def reverse_geocode(self, coords: Coordinates) -> Place | None:
        self._call_count += 1
        return Place(
            id=uuid.uuid4(),
            name=f"Place {self._call_count}",
            latitude=coords.latitude,
            longitude=coords.longitude,
            source="nominatim",
            country="Japan",
        )


class FailingGeocodingService:
    def search(self, query: str) -> list[Place]:
        return []

    def reverse_geocode(self, coords: Coordinates) -> Place | None:
        return None


def _make_service(
    photos_lib: FakePhotosLibrary | None = None,
    geocoding: FakeGeocodingService | FailingGeocodingService | None = None,
) -> tuple[AlbumService, FakePlaceRepository, FakeTripRepository, FakeProjectRepository]:
    place_repo = FakePlaceRepository()
    trip_repo = FakeTripRepository()
    project_repo = FakeProjectRepository()
    geo = geocoding or FakeGeocodingService()
    lib = photos_lib or FakePhotosLibrary()

    place_svc = PlaceService(place_repo=place_repo, geocoding=geo)
    trip_svc = TripService(trip_repo=trip_repo)
    project_svc = ProjectService(project_repo=project_repo)

    svc = AlbumService(
        photos_library=lib,
        place_service=place_svc,
        trip_service=trip_svc,
        project_service=project_svc,
        geocoding=geo,
    )
    return svc, place_repo, trip_repo, project_repo


def _sample_photos(album_id: str = "abc") -> tuple[FakePhotosLibrary, str]:
    photos = [
        GeotaggedPhoto(
            latitude=TOKYO_LAT,
            longitude=TOKYO_LON,
            timestamp=datetime(2024, 3, 15, 10, 0, 0, tzinfo=UTC),
            path="/photos/tokyo1.jpg",
        ),
        GeotaggedPhoto(
            latitude=TOKYO_LAT + 0.001,
            longitude=TOKYO_LON + 0.001,
            timestamp=datetime(2024, 3, 15, 14, 0, 0, tzinfo=UTC),
            path="/photos/tokyo2.jpg",
        ),
        GeotaggedPhoto(
            latitude=OSAKA_LAT,
            longitude=OSAKA_LON,
            timestamp=datetime(2024, 3, 16, 10, 0, 0, tzinfo=UTC),
            path="/photos/osaka1.jpg",
        ),
    ]
    albums = [AlbumSummary(id=album_id, title="Japan 2024", photo_count=3)]
    lib = FakePhotosLibrary(albums=albums, photos={album_id: photos})
    return lib, album_id


class TestAlbumServiceListAlbums:
    def test_list_albums(self) -> None:
        albums = [
            AlbumSummary(id="a1", title="Japan", photo_count=100),
            AlbumSummary(id="a2", title="Iceland", photo_count=50),
        ]
        lib = FakePhotosLibrary(albums=albums)
        svc, *_ = _make_service(photos_lib=lib)
        result = svc.list_albums()
        assert len(result) == EXPECTED_TWO
        assert result[0].title == "Japan"

    def test_list_albums_empty(self) -> None:
        svc, *_ = _make_service()
        result = svc.list_albums()
        assert result == []


class TestAlbumServicePreview:
    def test_preview_does_not_persist(self) -> None:
        lib, album_id = _sample_photos()
        svc, place_repo, trip_repo, project_repo = _make_service(photos_lib=lib)
        result = svc.preview_album(
            album_id=album_id,
            project_name="Japan 2024",
            total_album_photos=5,
        )
        assert isinstance(result, AlbumImportResult)
        assert result.cluster_count == EXPECTED_TWO
        assert result.total_photos == 5
        assert result.geotagged_photos == EXPECTED_THREE
        # Nothing should be persisted
        assert place_repo.list_all() == []
        assert trip_repo.list_all() == []
        assert project_repo.list_all() == []


class TestAlbumServiceImport:
    def test_import_creates_places_for_each_cluster(self) -> None:
        lib, album_id = _sample_photos()
        svc, place_repo, _, _ = _make_service(photos_lib=lib)
        svc.import_album(
            album_id=album_id,
            project_name="Japan 2024",
            total_album_photos=3,
        )
        assert len(place_repo.list_all()) == EXPECTED_TWO  # Tokyo cluster + Osaka

    def test_import_creates_trip_with_ordered_stops(self) -> None:
        lib, album_id = _sample_photos()
        svc, _, trip_repo, _ = _make_service(photos_lib=lib)
        svc.import_album(
            album_id=album_id,
            project_name="Japan 2024",
            total_album_photos=3,
        )
        trips = trip_repo.list_all()
        assert len(trips) == 1
        trip = trips[0]
        assert trip.name == "Japan 2024"
        assert len(trip.stops) == EXPECTED_TWO
        assert trip.stops[0].position == 0
        assert trip.stops[1].position == 1

    def test_import_creates_route_project(self) -> None:
        lib, album_id = _sample_photos()
        svc, _, _, project_repo = _make_service(photos_lib=lib)
        svc.import_album(
            album_id=album_id,
            project_name="Japan 2024",
            total_album_photos=3,
        )
        projects = project_repo.list_all()
        assert len(projects) == 1
        project = projects[0]
        assert project.name == "Japan 2024"
        assert project.map_type == MapType.ROUTE

    def test_import_returns_result(self) -> None:
        lib, album_id = _sample_photos()
        svc, *_ = _make_service(photos_lib=lib)
        result = svc.import_album(
            album_id=album_id,
            project_name="Japan 2024",
            total_album_photos=3,
        )
        assert isinstance(result, AlbumImportResult)
        assert result.total_photos == EXPECTED_THREE
        assert result.geotagged_photos == EXPECTED_THREE
        assert result.cluster_count == EXPECTED_TWO
        assert result.project_name == "Japan 2024"

    def test_import_with_custom_eps(self) -> None:
        lib, album_id = _sample_photos()
        svc, place_repo, _, _ = _make_service(photos_lib=lib)
        result = svc.import_album(
            album_id=album_id,
            project_name="Japan 2024",
            total_album_photos=3,
            eps_km=500.0,
        )
        assert result.cluster_count == 1
        assert len(place_repo.list_all()) == 1

    def test_import_empty_album(self) -> None:
        lib = FakePhotosLibrary(
            albums=[AlbumSummary(id="empty", title="Empty", photo_count=0)],
            photos={"empty": []},
        )
        svc, *_ = _make_service(photos_lib=lib)
        with pytest.raises(ValueError, match="No geotagged photos"):
            svc.import_album(album_id="empty", project_name="Empty", total_album_photos=0)

    def test_import_geocoding_failure_uses_coordinate_label(self) -> None:
        lib, album_id = _sample_photos()
        svc, place_repo, _, _ = _make_service(
            photos_lib=lib,
            geocoding=FailingGeocodingService(),
        )
        svc.import_album(
            album_id=album_id,
            project_name="Japan 2024",
            total_album_photos=3,
        )
        places = place_repo.list_all()
        assert all("\u00b0N" in p.name or "\u00b0S" in p.name for p in places)

    def test_import_project_has_trip_and_place_ids(self) -> None:
        lib, album_id = _sample_photos()
        svc, _, trip_repo, project_repo = _make_service(photos_lib=lib)
        svc.import_album(
            album_id=album_id,
            project_name="Japan 2024",
            total_album_photos=3,
        )
        projects = project_repo.list_all()
        project = projects[0]
        assert len(project.trip_ids) == 1
        assert len(project.place_ids) == EXPECTED_TWO
        trips = trip_repo.list_all()
        assert project.trip_ids[0] == trips[0].id
