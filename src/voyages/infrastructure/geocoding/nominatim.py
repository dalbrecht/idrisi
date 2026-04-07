"""Nominatim geocoding client using httpx."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import uuid4

import httpx

from voyages.domain.entities import Place

if TYPE_CHECKING:
    from voyages.domain.value_objects import Coordinates

_BASE_URL = "https://nominatim.openstreetmap.org"
_USER_AGENT = "Voyages/0.1.0 (map toolbox)"
_HEADERS = {"User-Agent": _USER_AGENT}


class NominatimGeocodingService:
    """Geocoding service backed by OpenStreetMap Nominatim."""

    def search(self, query: str) -> list[Place]:
        """Search for places by name.

        Args:
            query: Free-form search string.

        Returns:
            List of matching Place entities (up to 10).
        """
        response = httpx.get(
            f"{_BASE_URL}/search",
            params={
                "q": query,
                "format": "json",
                "addressdetails": "1",
                "limit": "10",
            },
            headers=_HEADERS,
        )
        response.raise_for_status()
        results: list[dict[str, Any]] = response.json()
        return [self._parse_search_result(r) for r in results]

    def reverse_geocode(self, coords: Coordinates) -> Place | None:
        """Reverse-geocode coordinates to a place.

        Args:
            coords: Latitude/longitude to look up.

        Returns:
            A Place entity or None if the lookup fails.
        """
        response = httpx.get(
            f"{_BASE_URL}/reverse",
            params={
                "lat": str(coords.latitude),
                "lon": str(coords.longitude),
                "format": "json",
                "addressdetails": "1",
            },
            headers=_HEADERS,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        if "error" in data:
            return None
        return self._parse_search_result(data)

    @staticmethod
    def _parse_search_result(data: dict[str, Any]) -> Place:
        address: dict[str, Any] = data.get("address", {})
        return Place(
            id=uuid4(),
            name=str(data.get("display_name", "")),
            latitude=float(data["lat"]),
            longitude=float(data["lon"]),
            country=address.get("country"),
            admin1=address.get("state"),
            source="nominatim",
        )
