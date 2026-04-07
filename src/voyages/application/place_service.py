from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from voyages.domain.entities import Place

if TYPE_CHECKING:
    from voyages.application.interfaces import GeocodingService, PlaceRepository


class PlaceService:
    """Application service for managing Places."""

    def __init__(self, place_repo: PlaceRepository, geocoding: GeocodingService) -> None:
        self._place_repo = place_repo
        self._geocoding = geocoding

    def create(
        self,
        name: str,
        lat: float,
        lon: float,
        source: str,
        country: str | None = None,
        admin1: str | None = None,
        category: str | None = None,
        notes: str | None = None,
    ) -> Place:
        """Create a new Place and persist it."""
        place = Place(
            id=uuid.uuid4(),
            name=name,
            latitude=lat,
            longitude=lon,
            source=source,
            country=country,
            admin1=admin1,
            category=category,
            notes=notes,
        )
        return self._place_repo.save(place)

    def get(self, place_id: uuid.UUID) -> Place | None:
        """Return the Place with the given ID, or None if not found."""
        return self._place_repo.get(place_id)

    def list_all(self) -> list[Place]:
        """Return all stored Places."""
        return self._place_repo.list_all()

    def search(self, query: str) -> list[Place]:
        """Search for Places using the geocoding service."""
        return self._geocoding.search(query)

    def update(self, place: Place) -> Place:
        """Persist an updated Place and return it."""
        return self._place_repo.save(place)

    def delete(self, place_id: uuid.UUID) -> None:
        """Delete the Place with the given ID."""
        self._place_repo.delete(place_id)
