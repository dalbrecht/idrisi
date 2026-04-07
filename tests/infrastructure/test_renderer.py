from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import uuid4

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
