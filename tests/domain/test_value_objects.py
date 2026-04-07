from __future__ import annotations

import pytest

from voyages.domain.value_objects import BoundingBox, Coordinates, MapType, OutputFormat

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
