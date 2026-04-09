"""Service for importing macOS Photos albums into Voyages projects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from voyages.application.clustering import cluster_photos
from voyages.domain.value_objects import Coordinates, MapType

if TYPE_CHECKING:
    from uuid import UUID

    from voyages.application.interfaces import GeocodingService, PhotosLibraryPort
    from voyages.application.place_service import PlaceService
    from voyages.application.project_service import ProjectService
    from voyages.application.trip_service import TripService
    from voyages.domain.entities import Project
    from voyages.domain.value_objects import AlbumSummary, PhotoCluster


@dataclass
class AlbumImportResult:
    """Summary of an album import operation."""

    project_name: str
    total_photos: int
    geotagged_photos: int
    cluster_count: int
    place_names: list[str]


class AlbumService:
    """Orchestrates importing a Photos album into a Voyages project."""

    def __init__(
        self,
        photos_library: PhotosLibraryPort,
        place_service: PlaceService,
        trip_service: TripService,
        project_service: ProjectService,
        geocoding: GeocodingService,
    ) -> None:
        self._photos_library = photos_library
        self._place_service = place_service
        self._trip_service = trip_service
        self._project_service = project_service
        self._geocoding = geocoding

    def list_albums(self) -> list[AlbumSummary]:
        """Return all albums from the photos library."""
        return self._photos_library.list_albums()

    def get_project_by_name(self, name: str) -> Project | None:
        """Check if a project with the given name already exists."""
        return self._project_service.get_by_name(name)

    def delete_project(self, project_id: UUID) -> None:
        """Delete a project by ID."""
        self._project_service.delete(project_id)

    def preview_album(
        self,
        album_id: str,
        project_name: str,
        total_album_photos: int,
        eps_km: float = 0.5,
        min_samples: int = 1,
    ) -> AlbumImportResult:
        """Preview what an album import would produce, without persisting anything.

        Args:
            album_id: The album identifier to preview.
            project_name: Name that would be used for the project.
            total_album_photos: Total photo count in the album (including non-geotagged).
            eps_km: DBSCAN cluster radius in kilometers.
            min_samples: Minimum photos per cluster.

        Returns:
            AlbumImportResult with preview statistics.

        Raises:
            ValueError: If the album has no geotagged photos.
        """
        photos = self._photos_library.get_album_photos(album_id)

        if not photos:
            msg = "No geotagged photos found in album. Nothing to import."
            raise ValueError(msg)

        clusters = cluster_photos(photos, eps_km=eps_km, min_samples=min_samples)
        place_names = [self._name_cluster(c, i + 1) for i, c in enumerate(clusters)]

        return AlbumImportResult(
            project_name=project_name,
            total_photos=total_album_photos,
            geotagged_photos=len(photos),
            cluster_count=len(clusters),
            place_names=place_names,
        )

    def import_album(
        self,
        album_id: str,
        project_name: str,
        total_album_photos: int,
        eps_km: float = 0.5,
        min_samples: int = 1,
        style: str = "default",
    ) -> AlbumImportResult:
        """Import an album as a Voyages project.

        Fetches geotagged photos, clusters them, creates Places and a Trip,
        then wires everything into a new Project.

        Args:
            album_id: The album identifier to import.
            project_name: Name for the created project.
            total_album_photos: Total photo count in the album (including non-geotagged).
            eps_km: DBSCAN cluster radius in kilometers.
            min_samples: Minimum photos per cluster.
            style: Map style name to store in project config.

        Returns:
            AlbumImportResult with summary statistics.

        Raises:
            ValueError: If the album has no geotagged photos.
        """
        photos = self._photos_library.get_album_photos(album_id)
        geotagged_count = len(photos)

        if not photos:
            msg = "No geotagged photos found in album. Nothing to import."
            raise ValueError(msg)

        clusters = cluster_photos(photos, eps_km=eps_km, min_samples=min_samples)

        place_names: list[str] = []
        place_ids = []

        for i, cluster in enumerate(clusters):
            name = self._name_cluster(cluster, i + 1)
            place_names.append(name)
            place = self._place_service.create(
                name=name,
                lat=cluster.centroid_lat,
                lon=cluster.centroid_lon,
                source="photos-album",
            )
            place_ids.append(place.id)

        trip = self._trip_service.create(
            name=project_name,
            start_date=clusters[0].earliest.date() if clusters else None,
            end_date=clusters[-1].latest.date() if clusters else None,
        )

        for position, pid in enumerate(place_ids):
            self._trip_service.add_stop(
                trip_id=trip.id,
                place_id=pid,
                arrived_at=clusters[position].earliest,
                departed_at=clusters[position].latest,
            )

        project = self._project_service.create(
            name=project_name,
            map_type=MapType.ROUTE,
            description=(
                f"Imported from Photos album"
                f" ({geotagged_count} photos, {len(clusters)} stops)"
            ),
            config={"style": style},
        )

        for pid in place_ids:
            self._project_service.add_place(project.id, pid)
        self._project_service.add_trip(project.id, trip.id)

        return AlbumImportResult(
            project_name=project_name,
            total_photos=total_album_photos,
            geotagged_photos=geotagged_count,
            cluster_count=len(clusters),
            place_names=place_names,
        )

    def _name_cluster(self, cluster: PhotoCluster, position: int) -> str:
        """Attempt to reverse-geocode a cluster centroid, falling back to coordinates."""
        coords = Coordinates(latitude=cluster.centroid_lat, longitude=cluster.centroid_lon)
        place = self._geocoding.reverse_geocode(coords)
        if place is not None:
            return place.name

        lat = cluster.centroid_lat
        lon = cluster.centroid_lon
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        return f"Stop {position} ({abs(lat):.2f}\u00b0{lat_dir}, {abs(lon):.2f}\u00b0{lon_dir})"
