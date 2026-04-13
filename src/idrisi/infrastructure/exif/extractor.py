"""EXIF GPS extraction service using Pillow."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS  # noqa: F401

from idrisi.domain.entities import Photo

if TYPE_CHECKING:
    from pathlib import Path

_GPS_INFO_TAG = 34853
_DATETIME_ORIGINAL_TAG = 36867
_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".heic", ".heif", ".tiff"})


class PillowExifService:
    """EXIF metadata extraction service backed by Pillow."""

    def extract_from_file(self, file_path: Path) -> Photo | None:
        """Extract GPS and datetime metadata from an image file.

        Args:
            file_path: Path to the image file.

        Returns:
            A Photo entity with GPS data, or None if no GPS data is present.
        """
        try:
            img = Image.open(file_path)
        except Exception:
            return None

        exif_data = img.getexif()
        if not exif_data:
            return None

        gps_info = exif_data.get(_GPS_INFO_TAG)
        if not gps_info:
            return None

        # Parse GPS coordinates
        gps_data: dict[str, object] = {}
        if isinstance(gps_info, dict):
            gps_data = gps_info
        else:
            # IFD-style: need to get the sub-IFD
            ifd = exif_data.get_ifd(_GPS_INFO_TAG)
            if not ifd:
                return None
            gps_data = {GPSTAGS.get(k, k): v for k, v in ifd.items()}

        latitude = self._parse_gps_coord(
            gps_data.get("GPSLatitude"),
            gps_data.get("GPSLatitudeRef"),
        )
        longitude = self._parse_gps_coord(
            gps_data.get("GPSLongitude"),
            gps_data.get("GPSLongitudeRef"),
        )

        if latitude is None or longitude is None:
            return None

        # Parse datetime
        taken_at = self._parse_datetime(exif_data.get(_DATETIME_ORIGINAL_TAG))

        return Photo(
            id=uuid4(),
            file_path=str(file_path),
            latitude=latitude,
            longitude=longitude,
            taken_at=taken_at,
        )

    def extract_from_directory(self, directory: Path) -> list[Photo]:
        """Extract photos with GPS data from all image files in a directory.

        Args:
            directory: Path to the directory to scan.

        Returns:
            List of Photo entities with GPS data.
        """
        photos: list[Photo] = []
        if not directory.is_dir():
            return photos
        for file_path in sorted(directory.iterdir()):
            if file_path.suffix.lower() in _IMAGE_EXTENSIONS:
                photo = self.extract_from_file(file_path)
                if photo is not None:
                    photos.append(photo)
        return photos

    @staticmethod
    def _parse_gps_coord(
        coord_data: object,
        ref: object,
    ) -> float | None:
        """Parse GPS coordinate from EXIF tuple format.

        Args:
            coord_data: Tuple of (degrees, minutes, seconds) as IFDRational values.
            ref: Reference direction (N/S/E/W).

        Returns:
            Decimal degrees, or None if parsing fails.
        """
        if coord_data is None or ref is None:
            return None
        try:
            if not isinstance(coord_data, tuple) or len(coord_data) < 3:  # noqa: PLR2004
                return None
            degrees = float(coord_data[0])
            minutes = float(coord_data[1])
            seconds = float(coord_data[2])
            decimal = degrees + minutes / 60.0 + seconds / 3600.0
            ref_str = str(ref)
            if ref_str in ("S", "W"):
                decimal = -decimal
            return decimal
        except (TypeError, ValueError, IndexError):
            return None

    @staticmethod
    def _parse_datetime(dt_string: object) -> datetime | None:
        """Parse EXIF datetime string.

        Args:
            dt_string: String in "YYYY:MM:DD HH:MM:SS" format.

        Returns:
            A datetime object, or None if parsing fails.
        """
        if dt_string is None:
            return None
        try:
            return datetime.strptime(str(dt_string), "%Y:%m:%d %H:%M:%S").replace(tzinfo=UTC)
        except (ValueError, TypeError):
            return None
