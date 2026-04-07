from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


class VoyagesError(Exception):
    """Base error class for all Voyages domain errors."""


class EntityNotFoundError(VoyagesError):
    """Raised when a domain entity cannot be found by its ID."""

    def __init__(self, entity_type: str, entity_id: UUID) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} not found: {entity_id}")


class PlaceNotFoundError(EntityNotFoundError):
    """Raised when a Place entity cannot be found."""

    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_type="Place", entity_id=entity_id)


class TripNotFoundError(EntityNotFoundError):
    """Raised when a Trip entity cannot be found."""

    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_type="Trip", entity_id=entity_id)


class ProjectNotFoundError(EntityNotFoundError):
    """Raised when a Project entity cannot be found."""

    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_type="Project", entity_id=entity_id)


class RegionNotFoundError(EntityNotFoundError):
    """Raised when a Region entity cannot be found."""

    def __init__(self, entity_id: UUID) -> None:
        super().__init__(entity_type="Region", entity_id=entity_id)


class BadRequestError(VoyagesError):
    """Raised for malformed client input (invalid UUIDs, enum values, etc.)."""


class PhotoNotFoundError(EntityNotFoundError):
    """Raised when a photo cannot be found."""

    def __init__(self, entity_id: UUID) -> None:
        super().__init__("Photo", entity_id)


class RenderError(VoyagesError):
    """Raised when map rendering fails."""
