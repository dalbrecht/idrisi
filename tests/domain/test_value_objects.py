from __future__ import annotations

from datetime import UTC, datetime

import pytest

from idrisi.domain.value_objects import (
    AlbumSummary,
    BoundingBox,
    Coordinates,
    GeotaggedPhoto,
    MapType,
    OutputFormat,
    PhotoCluster,
)

LAT_VALID = 45.0
LON_VALID = 90.0
LAT_MIN = -90.0
LAT_MAX = 90.0
LON_MIN = -180.0
LON_MAX = 180.0


class TestCoordinates:
    def test_valid_coordinates(self) -> None:
        coord = Coordinates(latitude=LAT_VALID, longitude=LON_VALID)
        assert coord.latitude == LAT_VALID
        assert coord.longitude == LON_VALID

    def test_boundary_latitude_min(self) -> None:
        coord = Coordinates(latitude=LAT_MIN, longitude=0.0)
        assert coord.latitude == LAT_MIN

    def test_boundary_latitude_max(self) -> None:
        coord = Coordinates(latitude=LAT_MAX, longitude=0.0)
        assert coord.latitude == LAT_MAX

    def test_boundary_longitude_min(self) -> None:
        coord = Coordinates(latitude=0.0, longitude=LON_MIN)
        assert coord.longitude == LON_MIN

    def test_boundary_longitude_max(self) -> None:
        coord = Coordinates(latitude=0.0, longitude=LON_MAX)
        assert coord.longitude == LON_MAX

    def test_invalid_latitude_too_low(self) -> None:
        with pytest.raises(ValueError, match="Latitude"):
            Coordinates(latitude=-91.0, longitude=0.0)

    def test_invalid_latitude_too_high(self) -> None:
        with pytest.raises(ValueError, match="Latitude"):
            Coordinates(latitude=90.1, longitude=0.0)

    def test_invalid_longitude_too_low(self) -> None:
        with pytest.raises(ValueError, match="Longitude"):
            Coordinates(latitude=0.0, longitude=-181.0)

    def test_invalid_longitude_too_high(self) -> None:
        with pytest.raises(ValueError, match="Longitude"):
            Coordinates(latitude=0.0, longitude=180.1)

    def test_frozen(self) -> None:
        coord = Coordinates(latitude=0.0, longitude=0.0)
        with pytest.raises(AttributeError):
            coord.latitude = 10.0  # type: ignore[misc]

    def test_nan_latitude_error_message_is_explicit(self) -> None:
        with pytest.raises(ValueError, match="NaN"):
            Coordinates(latitude=float("nan"), longitude=0.0)

    def test_inf_latitude_error_message_is_explicit(self) -> None:
        with pytest.raises(ValueError, match="infinite"):
            Coordinates(latitude=float("inf"), longitude=0.0)

    def test_nan_longitude_error_message_is_explicit(self) -> None:
        with pytest.raises(ValueError, match="NaN"):
            Coordinates(latitude=0.0, longitude=float("nan"))

    def test_inf_longitude_error_message_is_explicit(self) -> None:
        with pytest.raises(ValueError, match="infinite"):
            Coordinates(latitude=0.0, longitude=float("inf"))


class TestBoundingBox:
    def test_valid_bounding_box(self) -> None:
        sw = Coordinates(latitude=10.0, longitude=-20.0)
        ne = Coordinates(latitude=50.0, longitude=30.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        assert bbox.southwest == sw
        assert bbox.northeast == ne

    def test_equal_latitude_is_valid(self) -> None:
        sw = Coordinates(latitude=10.0, longitude=-20.0)
        ne = Coordinates(latitude=10.0, longitude=30.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        assert bbox.southwest.latitude == bbox.northeast.latitude

    def test_invalid_sw_latitude_greater_than_ne(self) -> None:
        sw = Coordinates(latitude=50.0, longitude=-20.0)
        ne = Coordinates(latitude=10.0, longitude=30.0)
        with pytest.raises(ValueError, match=r"southwest\.latitude"):
            BoundingBox(southwest=sw, northeast=ne)

    def test_contains_point_inside(self) -> None:
        sw = Coordinates(latitude=10.0, longitude=-20.0)
        ne = Coordinates(latitude=50.0, longitude=30.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        point = Coordinates(latitude=30.0, longitude=5.0)
        assert bbox.contains(point) is True

    def test_contains_point_outside_lat(self) -> None:
        sw = Coordinates(latitude=10.0, longitude=-20.0)
        ne = Coordinates(latitude=50.0, longitude=30.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        point = Coordinates(latitude=60.0, longitude=5.0)
        assert bbox.contains(point) is False

    def test_contains_point_outside_lon(self) -> None:
        sw = Coordinates(latitude=10.0, longitude=-20.0)
        ne = Coordinates(latitude=50.0, longitude=30.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        point = Coordinates(latitude=30.0, longitude=40.0)
        assert bbox.contains(point) is False

    def test_contains_point_on_boundary(self) -> None:
        sw = Coordinates(latitude=10.0, longitude=-20.0)
        ne = Coordinates(latitude=50.0, longitude=30.0)
        bbox = BoundingBox(southwest=sw, northeast=ne)
        point = Coordinates(latitude=10.0, longitude=-20.0)
        assert bbox.contains(point) is True


class TestMapType:
    def test_travel_value(self) -> None:
        assert MapType.TRAVEL.value == "travel"

    def test_region_value(self) -> None:
        assert MapType.REGION.value == "region"

    def test_route_value(self) -> None:
        assert MapType.ROUTE.value == "route"

    def test_enum_lookup(self) -> None:
        assert MapType("travel") is MapType.TRAVEL


class TestOutputFormat:
    def test_svg_value(self) -> None:
        assert OutputFormat.SVG.value == "svg"

    def test_pdf_value(self) -> None:
        assert OutputFormat.PDF.value == "pdf"

    def test_png_value(self) -> None:
        assert OutputFormat.PNG.value == "png"

    def test_webp_value(self) -> None:
        assert OutputFormat.WEBP.value == "webp"

    def test_eps_value(self) -> None:
        assert OutputFormat.EPS.value == "eps"

    def test_svg_extension(self) -> None:
        assert OutputFormat.SVG.extension == ".svg"

    def test_pdf_extension(self) -> None:
        assert OutputFormat.PDF.extension == ".pdf"

    def test_png_extension(self) -> None:
        assert OutputFormat.PNG.extension == ".png"

    def test_webp_extension(self) -> None:
        assert OutputFormat.WEBP.extension == ".webp"

    def test_eps_extension(self) -> None:
        assert OutputFormat.EPS.extension == ".eps"


TOKYO_LAT = 35.6762
TOKYO_LON = 139.6503
OSAKA_LAT = 34.6937
OSAKA_LON = 135.5023


class TestAlbumSummary:
    def test_create(self) -> None:
        album = AlbumSummary(id="abc123", title="Japan 2024", photo_count=347)
        assert album.id == "abc123"
        assert album.title == "Japan 2024"
        assert album.photo_count == 347

    def test_frozen(self) -> None:
        album = AlbumSummary(id="abc123", title="Japan 2024", photo_count=347)
        try:
            album.title = "Changed"  # type: ignore[misc]
            msg = "Should have raised"
            raise AssertionError(msg)
        except AttributeError:
            pass


class TestGeotaggedPhoto:
    def test_create(self) -> None:
        ts = datetime(2024, 3, 15, 10, 30, 0, tzinfo=UTC)
        photo = GeotaggedPhoto(
            latitude=TOKYO_LAT,
            longitude=TOKYO_LON,
            timestamp=ts,
            path="/photos/img1.jpg",
        )
        assert photo.latitude == TOKYO_LAT
        assert photo.longitude == TOKYO_LON
        assert photo.timestamp == ts
        assert photo.path == "/photos/img1.jpg"

    def test_frozen(self) -> None:
        ts = datetime(2024, 3, 15, 10, 30, 0, tzinfo=UTC)
        photo = GeotaggedPhoto(
            latitude=TOKYO_LAT,
            longitude=TOKYO_LON,
            timestamp=ts,
            path="/p.jpg",
        )
        try:
            photo.latitude = 0.0  # type: ignore[misc]
            msg = "Should have raised"
            raise AssertionError(msg)
        except AttributeError:
            pass


class TestPhotoCluster:
    def test_create(self) -> None:
        early = datetime(2024, 3, 15, 9, 0, 0, tzinfo=UTC)
        late = datetime(2024, 3, 15, 17, 0, 0, tzinfo=UTC)
        cluster = PhotoCluster(
            centroid_lat=TOKYO_LAT,
            centroid_lon=TOKYO_LON,
            photo_count=47,
            earliest=early,
            latest=late,
            representative_path="/photos/best.jpg",
        )
        assert cluster.centroid_lat == TOKYO_LAT
        assert cluster.centroid_lon == TOKYO_LON
        assert cluster.photo_count == 47
        assert cluster.earliest == early
        assert cluster.latest == late
        assert cluster.representative_path == "/photos/best.jpg"
