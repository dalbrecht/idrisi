from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

_LAT_MIN: float = -90.0
_LAT_MAX: float = 90.0
_LON_MIN: float = -180.0
_LON_MAX: float = 180.0


def _validate_finite(name: str, value: float) -> None:
    """Raise ValueError if value is NaN or infinite."""
    if not math.isfinite(value):
        kind = "NaN" if math.isnan(value) else "infinite"
        msg = f"{name} must be a finite number, got {kind}"
        raise ValueError(msg)


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        _validate_finite("Latitude", self.latitude)
        _validate_finite("Longitude", self.longitude)
        if not _LAT_MIN <= self.latitude <= _LAT_MAX:
            msg = f"Latitude must be between -90 and 90, got {self.latitude}"
            raise ValueError(msg)
        if not _LON_MIN <= self.longitude <= _LON_MAX:
            msg = f"Longitude must be between -180 and 180, got {self.longitude}"
            raise ValueError(msg)


@dataclass(frozen=True)
class BoundingBox:
    southwest: Coordinates
    northeast: Coordinates

    def __post_init__(self) -> None:
        if self.southwest.latitude > self.northeast.latitude:
            msg = (
                f"southwest.latitude ({self.southwest.latitude}) must be <= "
                f"northeast.latitude ({self.northeast.latitude})"
            )
            raise ValueError(msg)

    def contains(self, point: Coordinates) -> bool:
        return (
            self.southwest.latitude <= point.latitude <= self.northeast.latitude
            and self.southwest.longitude <= point.longitude <= self.northeast.longitude
        )


class MapType(Enum):
    TRAVEL = "travel"
    REGION = "region"
    ROUTE = "route"


class OutputFormat(Enum):
    SVG = "svg"
    PDF = "pdf"
    PNG = "png"
    WEBP = "webp"
    EPS = "eps"

    @property
    def extension(self) -> str:
        return f".{self.value}"


@dataclass(frozen=True)
class AlbumSummary:
    """Lightweight album metadata for the picker."""

    id: str
    title: str
    photo_count: int


@dataclass(frozen=True)
class GeotaggedPhoto:
    """A photo with location and time — intermediate type, not persisted."""

    latitude: float
    longitude: float
    timestamp: datetime
    path: str


@dataclass(frozen=True)
class PhotoCluster:
    """Result of clustering — a group of photos collapsed to one point."""

    centroid_lat: float
    centroid_lon: float
    photo_count: int
    earliest: datetime
    latest: datetime
    representative_path: str
