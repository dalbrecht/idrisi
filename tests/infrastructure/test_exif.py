"""Tests for EXIF GPS extraction service."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from idrisi.infrastructure.exif.extractor import PillowExifService


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
        True if tag == 34853 else ("2024:07:04 18:30:00" if tag == 36867 else default)
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
    @patch("idrisi.infrastructure.exif.extractor.Image.open")
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

    @patch("idrisi.infrastructure.exif.extractor.Image.open")
    def test_extract_without_gps_data(self, mock_open: MagicMock) -> None:
        mock_open.return_value = _make_mock_image_without_gps()
        service = PillowExifService()
        photo = service.extract_from_file(Path("/photos/no_gps.jpg"))

        assert photo is None


class TestPillowExifEdgeCases:
    @patch("idrisi.infrastructure.exif.extractor.Image.open")
    def test_corrupt_image_returns_none(self, mock_open: MagicMock) -> None:
        mock_open.side_effect = OSError("corrupt image")
        service = PillowExifService()
        result = service.extract_from_file(Path("/photos/corrupt.jpg"))
        assert result is None

    @patch("idrisi.infrastructure.exif.extractor.Image.open")
    def test_no_exif_data_returns_none(self, mock_open: MagicMock) -> None:
        mock_img = MagicMock()
        exif = MagicMock()
        exif.__bool__ = lambda self: False
        mock_img.getexif.return_value = exif
        mock_open.return_value = mock_img
        service = PillowExifService()
        result = service.extract_from_file(Path("/photos/no_exif.jpg"))
        assert result is None

    @patch("idrisi.infrastructure.exif.extractor.Image.open")
    def test_missing_lat_lon_returns_none(self, mock_open: MagicMock) -> None:
        mock_img = MagicMock()
        exif = MagicMock()
        # GPS tag present but IFD has no lat/lon
        exif.get.side_effect = lambda tag, default=None: True if tag == 34853 else default
        exif.__bool__ = lambda self: True
        exif.get_ifd.return_value = {}  # empty GPS IFD
        mock_img.getexif.return_value = exif
        mock_open.return_value = mock_img
        service = PillowExifService()
        result = service.extract_from_file(Path("/photos/no_latlon.jpg"))
        assert result is None

    def test_parse_gps_coord_south_ref_negative(self) -> None:
        result = PillowExifService._parse_gps_coord((33.0, 52.0, 0.0), "S")
        assert result is not None
        assert result < 0
        assert abs(result - (-33.8667)) < 0.001

    def test_parse_gps_coord_west_ref_negative(self) -> None:
        result = PillowExifService._parse_gps_coord((118.0, 15.0, 0.0), "W")
        assert result is not None
        assert result < 0
        assert abs(result - (-118.25)) < 0.001

    def test_parse_gps_coord_none_data_returns_none(self) -> None:
        result = PillowExifService._parse_gps_coord(None, "N")
        assert result is None

    def test_parse_gps_coord_none_ref_returns_none(self) -> None:
        result = PillowExifService._parse_gps_coord((48.0, 51.0, 24.0), None)
        assert result is None

    def test_parse_gps_coord_short_tuple_returns_none(self) -> None:
        result = PillowExifService._parse_gps_coord((48.0, 51.0), "N")
        assert result is None

    def test_parse_gps_coord_non_numeric_returns_none(self) -> None:
        result = PillowExifService._parse_gps_coord(("bad", "data", "here"), "N")
        assert result is None

    def test_parse_datetime_none_returns_none(self) -> None:
        result = PillowExifService._parse_datetime(None)
        assert result is None

    def test_parse_datetime_invalid_format_returns_none(self) -> None:
        result = PillowExifService._parse_datetime("not-a-date")
        assert result is None

    def test_parse_datetime_valid_format(self) -> None:
        result = PillowExifService._parse_datetime("2024:07:04 18:30:00")
        assert result is not None
        assert result == datetime(2024, 7, 4, 18, 30, 0, tzinfo=UTC)


class TestPillowExifDirectory:
    @patch("idrisi.infrastructure.exif.extractor.Image.open")
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

    def test_extract_from_non_directory_returns_empty(self) -> None:
        """Covers the early-return branch when directory.is_dir() is False."""
        mock_dir = MagicMock(spec=Path)
        mock_dir.is_dir.return_value = False

        service = PillowExifService()
        photos = service.extract_from_directory(mock_dir)

        assert photos == []

    @patch("idrisi.infrastructure.exif.extractor.Image.open")
    def test_gps_info_as_dict_branch(self, mock_open: MagicMock) -> None:
        """Verifies GPS extraction when gps_info is already a dict rather than an IFD object."""
        mock_img = MagicMock()
        exif = MagicMock()
        # Return a plain dict for GPS info tag so isinstance(gps_info, dict) is True
        gps_dict = {
            "GPSLatitude": (48.0, 51.0, 24.0),
            "GPSLatitudeRef": "N",
            "GPSLongitude": (2.0, 17.0, 40.0),
            "GPSLongitudeRef": "E",
        }
        exif.get.side_effect = lambda tag, default=None: (
            gps_dict if tag == 34853 else ("2024:07:04 18:30:00" if tag == 36867 else default)
        )
        exif.__bool__ = lambda self: True
        mock_img.getexif.return_value = exif
        mock_open.return_value = mock_img

        service = PillowExifService()
        photo = service.extract_from_file(Path("/photos/dict_gps.jpg"))

        assert photo is not None
        assert abs(photo.latitude - 48.8567) < 0.001  # type: ignore[operator]

    @patch("idrisi.infrastructure.exif.extractor.Image.open")
    def test_invalid_gps_coords_returns_none(self, mock_open: MagicMock) -> None:
        """Verifies that invalid GPS coordinate values cause extraction to return None."""
        mock_img = MagicMock()
        exif = MagicMock()
        # GPS info is a dict but coords are invalid (not tuples)
        gps_dict = {
            "GPSLatitude": "invalid",
            "GPSLatitudeRef": "N",
            "GPSLongitude": "invalid",
            "GPSLongitudeRef": "E",
        }
        exif.get.side_effect = lambda tag, default=None: gps_dict if tag == 34853 else default
        exif.__bool__ = lambda self: True
        mock_img.getexif.return_value = exif
        mock_open.return_value = mock_img

        service = PillowExifService()
        photo = service.extract_from_file(Path("/photos/bad_coords.jpg"))

        assert photo is None
