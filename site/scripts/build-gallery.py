"""Render example maps for the marketing-site gallery.

Run from the worktree root using the repo's venv Python directly:

    /Users/donaldalbrecht/Projects/Voyages/.venv/bin/python \
        site/scripts/build-gallery.py

Or from the repo root with UV_NO_SYNC=1:

    UV_NO_SYNC=1 uv run python \
        .claude/worktrees/marketing-site/site/scripts/build-gallery.py

Writes PNGs to site/public/gallery/. Re-run whenever the render
pipeline or sample data changes. The Cloudflare Pages build does *not*
invoke Python — it ships the already-committed PNGs.
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from idrisi.application.place_service import PlaceService
from idrisi.application.project_service import ProjectService
from idrisi.domain.entities import Trip, TripStop
from idrisi.domain.value_objects import MapType, OutputFormat
from idrisi.infrastructure.db.repository import (
    SqlPlaceRepository,
    SqlProjectRepository,
    SqlTripRepository,
)
from idrisi.infrastructure.db.session import create_engine_and_tables, get_session
from idrisi.infrastructure.renderer.engine import RenderEngine
from idrisi.infrastructure.renderer.styles import load_style


# A recognisable Kyushu, Japan loop — widely-documented tourist coordinates.
KYUSHU_LOOP = [
    ("Fukuoka",   33.5904, 130.4017),
    ("Nagasaki",  32.7503, 129.8777),
    ("Kumamoto",  32.8032, 130.7079),
    ("Mount Aso", 32.8842, 131.1042),
    ("Beppu",     33.2846, 131.4910),
    ("Kagoshima", 31.5966, 130.5571),
    ("Miyazaki",  31.9077, 131.4202),
]


class _NoopGeocoding:
    """No-network stub so PlaceService can be constructed without I/O."""

    def search(self, query: str):  # type: ignore[no-untyped-def]
        return []

    def reverse_geocode(self, coords):  # type: ignore[no-untyped-def]
        return None


def _build_sample_data() -> tuple[list, Trip]:
    """Create an in-memory DB, insert places, and return (places, trip)."""
    engine = create_engine_and_tables("sqlite:///:memory:")
    session = get_session(engine)

    place_repo = SqlPlaceRepository(session)
    project_repo = SqlProjectRepository(session)
    trip_repo = SqlTripRepository(session)

    place_svc = PlaceService(place_repo=place_repo, geocoding=_NoopGeocoding())
    project_svc = ProjectService(project_repo=project_repo)

    # Persist places
    places = []
    for title, lat, lon in KYUSHU_LOOP:
        p = place_svc.create(name=title, lat=lat, lon=lon, source="manual", country="Japan")
        places.append(p)

    # Persist a project (used by travel / region maps)
    project = project_svc.create(name="Kyushu loop", map_type=MapType.TRAVEL)
    for p in places:
        project = project_svc.add_place(project.id, p.id)

    # Build a Trip with ordered stops (required by render_route_map)
    trip = Trip(
        id=uuid.uuid4(),
        name="Kyushu route",
    )
    for position, p in enumerate(places):
        trip.stops.append(TripStop(place_id=p.id, position=position))
    trip = trip_repo.save(trip)

    session.close()
    return places, trip


def main() -> None:
    gallery = Path("site/public/gallery")
    if gallery.exists():
        shutil.rmtree(gallery)
    gallery.mkdir(parents=True)

    places, trip = _build_sample_data()
    style = load_style("default")
    engine = RenderEngine(style=style)

    # --- travel map ---
    engine.render_travel_map(
        places=places,
        regions=[],
        output_path=str(gallery / "kyushu-travel.png"),
        output_format=OutputFormat.PNG,
    )

    # --- route map (requires Trip object) ---
    engine.render_route_map(
        trip=trip,
        places=places,
        output_path=str(gallery / "kyushu-route.png"),
        output_format=OutputFormat.PNG,
    )

    # --- region map ---
    engine.render_region_map(
        places=places,
        regions=[],
        output_path=str(gallery / "kyushu-region.png"),
        output_format=OutputFormat.PNG,
        config={
            "center_lat": 32.5,
            "center_lon": 130.8,
            "extent": 4,
        },
    )

    print("Wrote:")
    for p in sorted(gallery.glob("*.png")):
        print(f"  {p}  ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
