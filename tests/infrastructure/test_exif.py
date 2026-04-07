"""Tests for EXIF GPS extraction service."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from voyages.infrastructure.exif.extractor import PillowExifService


def _make_mock_image_with_gps() -> MagicMock:
    """Create a mock PIL image with GPS EXIF data."""
    mock_img = MagicMock()

    gps_ifd = {
        1: "N",  # GPSLatitudeRef
        2: (48.0, 51.0, 24.0),  # GPSLatitude
        3: "E",  # GPSLongitudeRef
        4: (2.0, 17.0, 40.0),  # GPSLongitude
    }

    exif = MagicMock()
    # Return GPS info tag to indicate presence
    exif.get.side_effect = lambda tag, default=None: (
        True if tag == 34853 else (
            "2024:07:04 18:30:00" if tag == 36867 else default
        )
    )
    exif.__bool__ = lambda self: True
    # get_ifd returns the GPS IFD with GPSTAGS-decoded keys
    exif.get_ifd.return_value = gps_ifd

    mock_img.getexif.return_value = exif
    return mock_img


def _make_mock_image_without_gps() -> MagicMock:
    """Create a mock PIL image without GPS EXIF data."""
    mock_img = MagicMock()

    exif = MagicMock()
    exif.get.return_value = None
    exif.__bool__ = lambda self: True

    mock_img.getexif.return_value = exif
    return mock_img


class TestPillowExifExtraction:
    @patch("voyages.infrastructure.exif.extractor.Image.open")
    def test_extract_with_gps_data(self, mock_open: MagicMock) -> None:
        mock_open.return_value = _make_mock_image_with_gps()
        service = PillowExifService()
        photo = service.extract_from_file(Path("/photos/test.jpg"))

        assert photo is not None
        assert photo.file_path == "/photos/test.jpg"
        # 48 + 51/60 + 24/3600 = 48.856666...
        assert abs(photo.latitude - 48.8567) < 0.001  # type: ignore[operator]
        # 2 + 17/60 + 40/3600 = 2.29444...
        assert abs(photo.longitude - 2.2944) < 0.001  # type: ignore[operator]
        assert photo.taken_at is not None

    @patch("voyages.infrastructure.exif.extractor.Image.open")
    def test_extract_without_gps_data(self, mock_open: MagicMock) -> None:
        mock_open.return_value = _make_mock_image_without_gps()
        service = PillowExifService()
        photo = service.extract_from_file(Path("/photos/no_gps.jpg"))

        assert photo is None


class TestPillowExifDirectory:
    @patch("voyages.infrastructure.exif.extractor.Image.open")
    def test_extract_from_directory(self, mock_open: MagicMock) -> None:
        mock_open.return_value = _make_mock_image_with_gps()

        # Create a mock directory with image files
        mock_dir = MagicMock(spec=Path)
        mock_dir.is_dir.return_value = True

        file1 = MagicMock(spec=Path)
        file1.suffix = ".jpg"
        file1.__lt__ = lambda self, other: str(self) < str(other)

        file2 = MagicMock(spec=Path)
        file2.suffix = ".png"
        file2.__lt__ = lambda self, other: str(self) < str(other)

        file3 = MagicMock(spec=Path)
        file3.suffix = ".txt"  # Not an image
        file3.__lt__ = lambda self, other: str(self) < str(other)

        mock_dir.iterdir.return_value = [file1, file2, file3]

        service = PillowExifService()
        photos = service.extract_from_directory(mock_dir)

        assert len(photos) == 2
        # Image.open should be called twice (once for .jpg, once for .png)
        assert mock_open.call_count == 2
