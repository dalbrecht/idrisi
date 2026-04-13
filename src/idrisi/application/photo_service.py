from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import uuid
    from pathlib import Path

    from idrisi.application.interfaces import ExifService, GeocodingService, PhotoRepository
    from idrisi.domain.entities import Photo

from idrisi.domain.errors import PhotoNotFoundError


class PhotoService:
    """Application service for managing Photos."""

    def __init__(
        self,
        photo_repo: PhotoRepository,
        exif_service: ExifService,
        geocoding: GeocodingService,
    ) -> None:
        self._photo_repo = photo_repo
        self._exif_service = exif_service
        self._geocoding = geocoding

    def import_from_directory(
        self,
        directory: Path,
        dry_run: bool = False,
    ) -> list[Photo]:
        """Extract photos from a directory, filter out those without GPS, and optionally save.

        When dry_run=True the photos are returned but not persisted.
        """
        candidates = self._exif_service.extract_from_directory(directory)
        photos_with_gps = [
            p for p in candidates if p.latitude is not None and p.longitude is not None
        ]
        if not dry_run:
            for photo in photos_with_gps:
                self._photo_repo.save(photo)
        return photos_with_gps

    def assign_to_trip(self, photo_id: uuid.UUID, trip_id: uuid.UUID) -> Photo:
        """Assign a photo to a trip and persist the change."""
        photo = self._photo_repo.get(photo_id)
        if photo is None:
            raise PhotoNotFoundError(photo_id)
        photo.trip_id = trip_id
        return self._photo_repo.save(photo)

    def assign_to_place(self, photo_id: uuid.UUID, place_id: uuid.UUID) -> Photo:
        """Assign a photo to a place and persist the change."""
        photo = self._photo_repo.get(photo_id)
        if photo is None:
            raise PhotoNotFoundError(photo_id)
        photo.place_id = place_id
        return self._photo_repo.save(photo)
