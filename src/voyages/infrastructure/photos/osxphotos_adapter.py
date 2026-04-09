"""macOS Photos.app adapter using osxphotos."""

from __future__ import annotations

from datetime import UTC

import osxphotos

from voyages.domain.value_objects import AlbumSummary, GeotaggedPhoto


class OsxPhotosAdapter:
    """Reads albums and geotagged photos from the macOS Photos library."""

    def __init__(self) -> None:
        self._db: osxphotos.PhotosDB | None = None

    def _get_db(self) -> osxphotos.PhotosDB:
        if self._db is None:
            self._db = osxphotos.PhotosDB()
        return self._db

    def list_albums(self) -> list[AlbumSummary]:
        """Return all user-created albums with photo counts."""
        db = self._get_db()
        album_names: list[str] = db.album_info
        results: list[AlbumSummary] = []
        for album in album_names:
            results.append(
                AlbumSummary(
                    id=album.uuid,
                    title=album.title,
                    photo_count=len(album.photos),
                )
            )
        return results

    def get_album_photos(self, album_id: str) -> list[GeotaggedPhoto]:
        """Return geotagged photos from the specified album.

        Only photos with valid GPS coordinates and timestamps are included.

        Args:
            album_id: The UUID of the album to read.

        Returns:
            List of GeotaggedPhoto objects, filtered to those with GPS data.
        """
        db = self._get_db()
        albums = [a for a in db.album_info if a.uuid == album_id]
        if not albums:
            return []

        album = albums[0]
        results: list[GeotaggedPhoto] = []

        for photo in album.photos:
            location = photo.location
            if location is None or location == (None, None):
                continue

            lat, lon = location
            if lat is None or lon is None:
                continue

            taken_at = photo.date
            if taken_at is None:
                continue

            if taken_at.tzinfo is None:
                taken_at = taken_at.replace(tzinfo=UTC)

            results.append(
                GeotaggedPhoto(
                    latitude=float(lat),
                    longitude=float(lon),
                    timestamp=taken_at,
                    path=str(photo.original_filename),
                )
            )

        return results
