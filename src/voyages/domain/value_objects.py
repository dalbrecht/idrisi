from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

_LAT_MIN: float = -90.0
_LAT_MAX: float = 90.0
_LON_MIN: float = -180.0
_LON_MAX: float = 180.0


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if math.isnan(self.latitude) or math.isinf(self.latitude):
            kind = "NaN" if math.isnan(self.latitude) else "infinite"
            msg = f"Latitude must be a finite number, got {kind}"
            raise ValueError(msg)
        if math.isnan(self.longitude) or math.isinf(self.longitude):
            kind = "NaN" if math.isnan(self.longitude) else "infinite"
            msg = f"Longitude must be a finite number, got {kind}"
            raise ValueError(msg)
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
