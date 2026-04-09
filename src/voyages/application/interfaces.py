from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pathlib import Path
    from uuid import UUID

    from voyages.domain.entities import Photo, Place, Project, Region, Trip
    from voyages.domain.value_objects import (
        AlbumSummary,
        Coordinates,
        GeotaggedPhoto,
        OutputFormat,
    )


class PlaceRepository(Protocol):
    """Protocol for Place persistence."""

    def get(self, place_id: UUID) -> Place | None: ...

    def list_all(self) -> list[Place]: ...

    def search_by_name(self, query: str) -> list[Place]: ...

    def save(self, place: Place) -> Place: ...

    def delete(self, place_id: UUID) -> None: ...


class TripRepository(Protocol):
    """Protocol for Trip persistence."""

    def get(self, trip_id: UUID) -> Trip | None: ...

    def list_all(self) -> list[Trip]: ...

    def save(self, trip: Trip) -> Trip: ...

    def delete(self, trip_id: UUID) -> None: ...


class RegionRepository(Protocol):
    """Protocol for Region persistence."""

    def get(self, region_id: UUID) -> Region | None: ...

    def list_all(self) -> list[Region]: ...

    def save(self, region: Region) -> Region: ...

    def delete(self, region_id: UUID) -> None: ...


class ProjectRepository(Protocol):
    """Protocol for Project persistence."""

    def get(self, project_id: UUID) -> Project | None: ...

    def get_by_name(self, name: str) -> Project | None: ...

    def list_all(self) -> list[Project]: ...

    def save(self, project: Project) -> Project: ...

    def delete(self, project_id: UUID) -> None: ...


class PhotoRepository(Protocol):
    """Protocol for Photo persistence."""

    def get(self, photo_id: UUID) -> Photo | None: ...

    def list_by_trip(self, trip_id: UUID) -> list[Photo]: ...

    def save(self, photo: Photo) -> Photo: ...

    def delete(self, photo_id: UUID) -> None: ...


class GeocodingService(Protocol):
    """Protocol for geocoding operations."""

    def search(self, query: str) -> list[Place]: ...

    def reverse_geocode(self, coords: Coordinates) -> Place | None: ...


class ExifService(Protocol):
    """Protocol for EXIF metadata extraction."""

    def extract_from_file(self, file_path: Path) -> Photo | None: ...

    def extract_from_directory(self, directory: Path) -> list[Photo]: ...


class MapRenderer(Protocol):
    """Protocol for map rendering."""

    def render(
        self,
        project: Project,
        output_format: OutputFormat,
        output_path: Path,
        **kwargs: Any,
    ) -> None: ...


class PhotosLibraryPort(Protocol):
    """Protocol for accessing a photo library (e.g., macOS Photos.app)."""

    def list_albums(self) -> list[AlbumSummary]: ...

    def get_album_photos(self, album_id: str) -> list[GeotaggedPhoto]: ...
