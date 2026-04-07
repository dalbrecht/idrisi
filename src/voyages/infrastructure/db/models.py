"""SQLAlchemy ORM models for all Voyages domain entities."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    __allow_unmapped__ = True


class PlaceModel(Base):
    __tablename__ = "places"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    country = Column(String, nullable=True)
    admin1 = Column(String, nullable=True)
    category = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String, nullable=False)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)


class TripModel(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)

    stops: list[TripStopModel] = relationship(
        "TripStopModel",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripStopModel.position",
    )


class TripStopModel(Base):
    __tablename__ = "trip_stops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    place_id = Column(String(36), ForeignKey("places.id"), nullable=False)
    position = Column(Integer, nullable=False)
    arrived_at = Column(String, nullable=True)
    departed_at = Column(String, nullable=True)

    trip: TripModel = relationship("TripModel", back_populates="stops")


class RegionModel(Base):
    __tablename__ = "regions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    region_type = Column(String, nullable=False)
    region_code = Column(String, nullable=True)


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    map_type = Column(String, nullable=False)
    config = Column(Text, nullable=True)  # JSON string


class ProjectPlaceModel(Base):
    __tablename__ = "project_places"

    project_id = Column(String(36), ForeignKey("projects.id"), primary_key=True)
    place_id = Column(String(36), ForeignKey("places.id"), primary_key=True)


class ProjectTripModel(Base):
    __tablename__ = "project_trips"

    project_id = Column(String(36), ForeignKey("projects.id"), primary_key=True)
    trip_id = Column(String(36), ForeignKey("trips.id"), primary_key=True)


class ProjectRegionModel(Base):
    __tablename__ = "project_regions"

    project_id = Column(String(36), ForeignKey("projects.id"), primary_key=True)
    region_id = Column(String(36), ForeignKey("regions.id"), primary_key=True)


class PhotoModel(Base):
    __tablename__ = "photos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    file_path = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    taken_at = Column(String, nullable=True)
    place_id = Column(String(36), ForeignKey("places.id"), nullable=True)
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=True)
