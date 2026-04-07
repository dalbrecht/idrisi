from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import date, datetime
    from uuid import UUID

    from voyages.domain.value_objects import MapType


@dataclass
class Place:
    id: UUID
    name: str
    latitude: float
    longitude: float
    source: str
    country: str | None = None
    admin1: str | None = None
    category: str | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class TripStop:
    place_id: UUID
    position: int
    arrived_at: datetime | None = None
    departed_at: datetime | None = None


@dataclass
class Trip:
    id: UUID
    name: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    stops: list[TripStop] = field(default_factory=list)


@dataclass
class Region:
    id: UUID
    name: str
    region_type: str
    region_code: str | None = None


@dataclass
class Project:
    id: UUID
    name: str
    map_type: MapType
    description: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    place_ids: list[UUID] = field(default_factory=list)
    trip_ids: list[UUID] = field(default_factory=list)
    region_ids: list[UUID] = field(default_factory=list)


@dataclass
class Photo:
    id: UUID
    file_path: str
    latitude: float | None = None
    longitude: float | None = None
    taken_at: datetime | None = None
    place_id: UUID | None = None
    trip_id: UUID | None = None
