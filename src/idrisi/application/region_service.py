from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from idrisi.domain.entities import Region

if TYPE_CHECKING:
    from idrisi.application.interfaces import PlaceRepository, RegionRepository


class RegionService:
    """Application service for managing Regions."""

    def __init__(self, region_repo: RegionRepository, place_repo: PlaceRepository) -> None:
        self._region_repo = region_repo
        self._place_repo = place_repo

    def create(
        self,
        name: str,
        region_type: str,
        region_code: str | None = None,
    ) -> Region:
        """Create a new Region and persist it."""
        region = Region(
            id=uuid.uuid4(),
            name=name,
            region_type=region_type,
            region_code=region_code,
        )
        return self._region_repo.save(region)

    def get(self, region_id: uuid.UUID) -> Region | None:
        """Return the Region with the given ID, or None if not found."""
        return self._region_repo.get(region_id)

    def list_all(self) -> list[Region]:
        """Return all stored Regions."""
        return self._region_repo.list_all()

    def derive_from_places(self) -> list[Region]:
        """Scan all places and create a Region for each unique country found.

        Skips places that have no country set. Avoids creating duplicate
        regions for countries that already exist in the repository.
        """
        places = self._place_repo.list_all()
        existing_regions = self._region_repo.list_all()
        existing_country_names = {r.name for r in existing_regions if r.region_type == "country"}

        seen_countries: set[str] = set()
        new_regions: list[Region] = []

        for place in places:
            country = place.country
            if country is None:
                continue
            if country in existing_country_names or country in seen_countries:
                continue
            seen_countries.add(country)
            region = Region(
                id=uuid.uuid4(),
                name=country,
                region_type="country",
            )
            self._region_repo.save(region)
            new_regions.append(region)

        return new_regions

    def delete(self, region_id: uuid.UUID) -> None:
        """Delete the Region with the given ID."""
        self._region_repo.delete(region_id)
