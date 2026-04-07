"""Tests for SQLAlchemy models and session management."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import inspect

from voyages.infrastructure.db.models import PlaceModel
from voyages.infrastructure.db.session import create_engine_and_tables, get_session


@pytest.fixture
def engine():
    return create_engine_and_tables("sqlite:///:memory:")


@pytest.fixture
def session(engine):
    s = get_session(engine)
    yield s
    s.close()


def test_tables_created(engine) -> None:
    """All expected tables should be present after engine creation."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    expected = {
        "places",
        "trips",
        "trip_stops",
        "regions",
        "projects",
        "project_places",
        "project_trips",
        "project_regions",
        "photos",
    }
    assert expected.issubset(table_names)


def test_insert_and_read_place(session) -> None:
    """Should be able to insert and retrieve a PlaceModel."""
    place_id = str(uuid4())
    place = PlaceModel(
        id=place_id,
        name="Paris",
        latitude=48.8566,
        longitude=2.3522,
        country="France",
        admin1="Ile-de-France",
        source="manual",
    )
    session.add(place)
    session.commit()

    loaded = session.get(PlaceModel, place_id)
    assert loaded is not None
    assert loaded.name == "Paris"
    assert loaded.latitude == pytest.approx(48.8566)
    assert loaded.longitude == pytest.approx(2.3522)
    assert loaded.country == "France"
    assert loaded.source == "manual"
