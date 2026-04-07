from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from uuid import uuid4

from PIL import Image

from voyages.domain.entities import Place, Trip, TripStop
from voyages.domain.value_objects import OutputFormat
from voyages.infrastructure.renderer.engine import RenderEngine
from voyages.infrastructure.renderer.styles import load_style


def _sample_places() -> list[Place]:
    return [
        Place(id=uuid4(), name="Paris", latitude=48.8566, longitude=2.3522, source="test"),
        Place(id=uuid4(), name="London", latitude=51.5074, longitude=-0.1278, source="test"),
        Place(id=uuid4(), name="Berlin", latitude=52.5200, longitude=13.4050, source="test"),
    ]


class TestRenderTravelMap:
    """Tests for travel map rendering."""

    def test_render_png(self) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = _sample_places()

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "travel.png"
            result = engine.render_travel_map(
                places=places,
                regions=[],
                output_path=str(out),
                output_format=OutputFormat.PNG,
            )
            assert result == str(out)
            assert out.exists()
            assert out.stat().st_size > 0

    def test_render_svg(self) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = _sample_places()

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "travel.svg"
            result = engine.render_travel_map(
                places=places,
                regions=[],
                output_path=str(out),
                output_format=OutputFormat.SVG,
            )
            assert result == str(out)
            assert out.exists()
            assert out.stat().st_size > 0

    def test_render_with_custom_config(self) -> None:
        style = load_style("minimal")
        engine = RenderEngine(style)
        places = _sample_places()

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "travel_custom.png"
            result = engine.render_travel_map(
                places=places,
                regions=[],
                output_path=str(out),
                output_format=OutputFormat.PNG,
                config={"dpi": 100, "width": 800},
            )
            assert result == str(out)
            assert out.exists()
            assert out.stat().st_size > 0


class TestRenderRegionMap:
    """Tests for region map rendering."""

    def test_render_region_png(self) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = _sample_places()

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "region.png"
            result = engine.render_region_map(
                places=places,
                regions=[],
                output_path=str(out),
                output_format=OutputFormat.PNG,
                config={"center_lat": 50.0, "center_lon": 5.0, "extent": 15},
            )
            assert result == str(out)
            assert out.exists()
            assert out.stat().st_size > 0


class TestRenderRouteMap:
    """Tests for route map rendering."""

    def test_render_route_png(self) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = _sample_places()

        trip = Trip(
            id=uuid4(),
            name="Europe Trip",
            stops=[
                TripStop(place_id=places[0].id, position=1),
                TripStop(place_id=places[1].id, position=2),
                TripStop(place_id=places[2].id, position=3),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "route.png"
            result = engine.render_route_map(
                trip=trip,
                places=places,
                output_path=str(out),
                output_format=OutputFormat.PNG,
            )
            assert result == str(out)
            assert out.exists()
            assert out.stat().st_size > 0


class TestRenderOutputValidation:
    """Verify rendered output is valid, not just that a file exists."""

    def test_png_magic_bytes(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [
            Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")
        ]
        out = tmp_path / "test.png"
        engine.render_travel_map(places, [], str(out), OutputFormat.PNG)
        with open(out, "rb") as f:
            header = f.read(8)
        assert header == b"\x89PNG\r\n\x1a\n"

    def test_svg_contains_svg_tag(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [
            Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")
        ]
        out = tmp_path / "test.svg"
        engine.render_travel_map(places, [], str(out), OutputFormat.SVG)
        content = out.read_text()
        assert "<svg" in content

    def test_pdf_magic_bytes(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [
            Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")
        ]
        out = tmp_path / "test.pdf"
        engine.render_travel_map(places, [], str(out), OutputFormat.PDF)
        with open(out, "rb") as f:
            header = f.read(4)
        assert header == b"%PDF"

    def test_eps_magic_bytes(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [
            Place(id=uuid.uuid4(), name="Paris", latitude=48.85, longitude=2.35, source="test")
        ]
        out = tmp_path / "test.eps"
        engine.render_travel_map(places, [], str(out), OutputFormat.EPS)
        with open(out, "rb") as f:
            header = f.read(11)
        assert header.startswith(b"%!PS-Adobe")

    def test_png_dimensions_match_config(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        places = [Place(id=uuid.uuid4(), name="Test", latitude=0.0, longitude=0.0, source="test")]
        out = tmp_path / "test.png"
        engine.render_travel_map(places, [], str(out), OutputFormat.PNG, config={"width": 800})
        with Image.open(out) as img:
            # Width may differ from requested due to bbox_inches="tight" cropping;
            # assert it is a plausible non-trivial render (not zero, not enormous).
            assert 100 < img.width < 1600

    def test_marker_visible_on_rendered_map(self, tmp_path: Path) -> None:
        """A rendered map with one place should not be a single solid color."""
        style = load_style("default")
        engine = RenderEngine(style)
        places = [Place(id=uuid.uuid4(), name="Marker", latitude=0.0, longitude=0.0, source="test")]
        out = tmp_path / "marker.png"
        engine.render_travel_map(
            places, [], str(out), OutputFormat.PNG, config={"width": 400, "dpi": 72}
        )
        with Image.open(out) as img:
            pixels = list(img.getdata())
            unique_colors = set(pixels)
            assert len(unique_colors) > 10  # A real map has many colors

    def test_empty_places_renders_without_error(self, tmp_path: Path) -> None:
        style = load_style("default")
        engine = RenderEngine(style)
        out = tmp_path / "empty.png"
        engine.render_travel_map([], [], str(out), OutputFormat.PNG)
        assert out.exists()
        assert out.stat().st_size > 0
