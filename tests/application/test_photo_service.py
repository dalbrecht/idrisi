from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from voyages.application.photo_service import PhotoService
from voyages.domain.entities import Photo

if TYPE_CHECKING:
    from voyages.domain.value_objects import Coordinates

PHOTO_WITH_GPS = Photo(
    id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
    file_path="/photos/paris.jpg",
    latitude=48.8566,
    longitude=2.3522,
)
PHOTO_NO_GPS = Photo(
    id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
    file_path="/photos/noloc.jpg",
    latitude=None,
    longitude=None,
)


class FakePhotoRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Photo] = {}
        self.save_count = 0

    def get(self, photo_id: uuid.UUID) -> Photo | None:
        return self._store.get(photo_id)

    def list_by_trip(self, trip_id: uuid.UUID) -> list[Photo]:
        return [p for p in self._store.values() if p.trip_id == trip_id]

    def save(self, photo: Photo) -> Photo:
        self._store[photo.id] = photo
        self.save_count += 1
        return photo

    def delete(self, photo_id: uuid.UUID) -> None:
        self._store.pop(photo_id, None)


class FakeExifService:
    def __init__(self, photos: list[Photo] | None = None) -> None:
        self._photos = photos or []

    def extract_from_file(self, file_path: Path) -> Photo | None:
        return None

    def extract_from_directory(self, directory: Path) -> list[Photo]:
        return list(self._photos)


class FakeGeocodingService:
    def search(self, query: str) -> list[Photo]:
        return []

    def reverse_geocode(self, coords: Coordinates) -> None:
        return None


class TestPhotoService:
    def setup_method(self) -> None:
        self.photo_repo = FakePhotoRepository()
        self.exif_service = FakeExifService()
        self.geocoding = FakeGeocodingService()
        self.service = PhotoService(
            photo_repo=self.photo_repo,
            exif_service=self.exif_service,
            geocoding=self.geocoding,
        )

    def test_import_from_directory_returns_photos_with_gps(self) -> None:
        self.exif_service = FakeExifService(photos=[PHOTO_WITH_GPS, PHOTO_NO_GPS])
        self.service = PhotoService(
            photo_repo=self.photo_repo,
            exif_service=self.exif_service,
            geocoding=self.geocoding,
        )
        photos = self.service.import_from_directory(Path("/photos"))
        assert len(photos) == 1
        assert photos[0].file_path == "/photos/paris.jpg"

    def test_import_from_directory_skips_no_gps(self) -> None:
        self.exif_service = FakeExifService(photos=[PHOTO_NO_GPS])
        self.service = PhotoService(
            photo_repo=self.photo_repo,
            exif_service=self.exif_service,
            geocoding=self.geocoding,
        )
        photos = self.service.import_from_directory(Path("/photos"))
        assert photos == []

    def test_import_from_directory_saves_photos(self) -> None:
        self.exif_service = FakeExifService(photos=[PHOTO_WITH_GPS])
        self.service = PhotoService(
            photo_repo=self.photo_repo,
            exif_service=self.exif_service,
            geocoding=self.geocoding,
        )
        self.service.import_from_directory(Path("/photos"))
        assert self.photo_repo.save_count == 1

    def test_dry_run_does_not_save(self) -> None:
        self.exif_service = FakeExifService(photos=[PHOTO_WITH_GPS])
        self.service = PhotoService(
            photo_repo=self.photo_repo,
            exif_service=self.exif_service,
            geocoding=self.geocoding,
        )
        photos = self.service.import_from_directory(Path("/photos"), dry_run=True)
        assert len(photos) == 1
        assert self.photo_repo.save_count == 0

    def test_dry_run_still_returns_gps_photos(self) -> None:
        self.exif_service = FakeExifService(photos=[PHOTO_WITH_GPS, PHOTO_NO_GPS])
        self.service = PhotoService(
            photo_repo=self.photo_repo,
            exif_service=self.exif_service,
            geocoding=self.geocoding,
        )
        photos = self.service.import_from_directory(Path("/photos"), dry_run=True)
        assert len(photos) == 1

    def test_assign_to_trip(self) -> None:
        self.photo_repo.save(PHOTO_WITH_GPS)
        trip_id = uuid.uuid4()
        updated = self.service.assign_to_trip(PHOTO_WITH_GPS.id, trip_id)
        assert updated.trip_id == trip_id

    def test_assign_to_trip_persists(self) -> None:
        self.photo_repo.save(PHOTO_WITH_GPS)
        trip_id = uuid.uuid4()
        self.service.assign_to_trip(PHOTO_WITH_GPS.id, trip_id)
        fetched = self.photo_repo.get(PHOTO_WITH_GPS.id)
        assert fetched is not None
        assert fetched.trip_id == trip_id

    def test_assign_to_place(self) -> None:
        self.photo_repo.save(PHOTO_WITH_GPS)
        place_id = uuid.uuid4()
        updated = self.service.assign_to_place(PHOTO_WITH_GPS.id, place_id)
        assert updated.place_id == place_id

    def test_assign_to_place_persists(self) -> None:
        self.photo_repo.save(PHOTO_WITH_GPS)
        place_id = uuid.uuid4()
        self.service.assign_to_place(PHOTO_WITH_GPS.id, place_id)
        fetched = self.photo_repo.get(PHOTO_WITH_GPS.id)
        assert fetched is not None
        assert fetched.place_id == place_id
