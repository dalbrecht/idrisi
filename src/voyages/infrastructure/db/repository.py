"""SQLAlchemy repository implementations for all domain entities."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Session

from voyages.domain.entities import Photo, Place, Project, Region, Trip, TripStop
from voyages.domain.value_objects import MapType
from voyages.infrastructure.db.models import (
    PhotoModel,
    PlaceModel,
    ProjectModel,
    ProjectPlaceModel,
    ProjectRegionModel,
    ProjectTripModel,
    RegionModel,
    TripModel,
    TripStopModel,
)

if TYPE_CHECKING:
    pass

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
_DATE_FORMAT = "%Y-%m-%d"


def _dt_to_str(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt is not None else None


def _str_to_dt(s: str | None) -> datetime | None:
    if s is None:
        return None
    return datetime.fromisoformat(s)


def _date_to_str(d: date | None) -> str | None:
    return d.isoformat() if d is not None else None


def _str_to_date(s: str | None) -> date | None:
    if s is None:
        return None
    return date.fromisoformat(s)


class SqlPlaceRepository:
    """SQLAlchemy-backed PlaceRepository implementation."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, place_id: UUID) -> Place | None:
        model = self._session.get(PlaceModel, str(place_id))
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self) -> list[Place]:
        models = self._session.query(PlaceModel).all()
        return [self._to_entity(m) for m in models]

    def search_by_name(self, query: str) -> list[Place]:
        models = (
            self._session.query(PlaceModel)
            .filter(PlaceModel.name.ilike(f"%{query}%"))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, place: Place) -> Place:
        existing = self._session.get(PlaceModel, str(place.id))
        if existing is not None:
            existing.name = place.name
            existing.latitude = place.latitude
            existing.longitude = place.longitude
            existing.country = place.country
            existing.admin1 = place.admin1
            existing.category = place.category
            existing.notes = place.notes
            existing.source = place.source
            existing.created_at = _dt_to_str(place.created_at)
            existing.updated_at = _dt_to_str(place.updated_at)
        else:
            model = PlaceModel(
                id=str(place.id),
                name=place.name,
                latitude=place.latitude,
                longitude=place.longitude,
                country=place.country,
                admin1=place.admin1,
                category=place.category,
                notes=place.notes,
                source=place.source,
                created_at=_dt_to_str(place.created_at),
                updated_at=_dt_to_str(place.updated_at),
            )
            self._session.add(model)
        self._session.commit()
        return place

    def delete(self, place_id: UUID) -> None:
        model = self._session.get(PlaceModel, str(place_id))
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: PlaceModel) -> Place:
        return Place(
            id=UUID(str(model.id)),
            name=str(model.name),
            latitude=float(model.latitude),  # type: ignore[arg-type]
            longitude=float(model.longitude),  # type: ignore[arg-type]
            source=str(model.source),
            country=str(model.country) if model.country else None,
            admin1=str(model.admin1) if model.admin1 else None,
            category=str(model.category) if model.category else None,
            notes=str(model.notes) if model.notes else None,
            created_at=_str_to_dt(str(model.created_at) if model.created_at else None),
            updated_at=_str_to_dt(str(model.updated_at) if model.updated_at else None),
        )


class SqlTripRepository:
    """SQLAlchemy-backed TripRepository implementation."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, trip_id: UUID) -> Trip | None:
        model = self._session.get(TripModel, str(trip_id))
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self) -> list[Trip]:
        models = self._session.query(TripModel).all()
        return [self._to_entity(m) for m in models]

    def save(self, trip: Trip) -> Trip:
        existing = self._session.get(TripModel, str(trip.id))
        if existing is not None:
            existing.name = trip.name
            existing.description = trip.description
            existing.start_date = _date_to_str(trip.start_date)
            existing.end_date = _date_to_str(trip.end_date)
            # Replace all stops
            for stop in list(existing.stops):
                self._session.delete(stop)
            self._session.flush()
            for stop in trip.stops:
                stop_model = TripStopModel(
                    trip_id=str(trip.id),
                    place_id=str(stop.place_id),
                    position=stop.position,
                    arrived_at=_dt_to_str(stop.arrived_at),
                    departed_at=_dt_to_str(stop.departed_at),
                )
                self._session.add(stop_model)
        else:
            model = TripModel(
                id=str(trip.id),
                name=trip.name,
                description=trip.description,
                start_date=_date_to_str(trip.start_date),
                end_date=_date_to_str(trip.end_date),
            )
            self._session.add(model)
            self._session.flush()
            for stop in trip.stops:
                stop_model = TripStopModel(
                    trip_id=str(trip.id),
                    place_id=str(stop.place_id),
                    position=stop.position,
                    arrived_at=_dt_to_str(stop.arrived_at),
                    departed_at=_dt_to_str(stop.departed_at),
                )
                self._session.add(stop_model)
        self._session.commit()
        return trip

    def delete(self, trip_id: UUID) -> None:
        model = self._session.get(TripModel, str(trip_id))
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: TripModel) -> Trip:
        stops = [
            TripStop(
                place_id=UUID(str(s.place_id)),
                position=int(s.position),  # type: ignore[arg-type]
                arrived_at=_str_to_dt(str(s.arrived_at) if s.arrived_at else None),
                departed_at=_str_to_dt(str(s.departed_at) if s.departed_at else None),
            )
            for s in model.stops
        ]
        return Trip(
            id=UUID(str(model.id)),
            name=str(model.name),
            description=str(model.description) if model.description else None,
            start_date=_str_to_date(str(model.start_date) if model.start_date else None),
            end_date=_str_to_date(str(model.end_date) if model.end_date else None),
            stops=stops,
        )


class SqlRegionRepository:
    """SQLAlchemy-backed RegionRepository implementation."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, region_id: UUID) -> Region | None:
        model = self._session.get(RegionModel, str(region_id))
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self) -> list[Region]:
        models = self._session.query(RegionModel).all()
        return [self._to_entity(m) for m in models]

    def save(self, region: Region) -> Region:
        existing = self._session.get(RegionModel, str(region.id))
        if existing is not None:
            existing.name = region.name
            existing.region_type = region.region_type
            existing.region_code = region.region_code
        else:
            model = RegionModel(
                id=str(region.id),
                name=region.name,
                region_type=region.region_type,
                region_code=region.region_code,
            )
            self._session.add(model)
        self._session.commit()
        return region

    def delete(self, region_id: UUID) -> None:
        model = self._session.get(RegionModel, str(region_id))
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: RegionModel) -> Region:
        return Region(
            id=UUID(str(model.id)),
            name=str(model.name),
            region_type=str(model.region_type),
            region_code=str(model.region_code) if model.region_code else None,
        )


class SqlProjectRepository:
    """SQLAlchemy-backed ProjectRepository implementation."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, project_id: UUID) -> Project | None:
        model = self._session.get(ProjectModel, str(project_id))
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_name(self, name: str) -> Project | None:
        model = (
            self._session.query(ProjectModel)
            .filter(ProjectModel.name == name)
            .first()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self) -> list[Project]:
        models = self._session.query(ProjectModel).all()
        return [self._to_entity(m) for m in models]

    def save(self, project: Project) -> Project:
        config_json = json.dumps(project.config) if project.config else None
        existing = self._session.get(ProjectModel, str(project.id))
        if existing is not None:
            existing.name = project.name
            existing.description = project.description
            existing.map_type = project.map_type.value
            existing.config = config_json
        else:
            model = ProjectModel(
                id=str(project.id),
                name=project.name,
                description=project.description,
                map_type=project.map_type.value,
                config=config_json,
            )
            self._session.add(model)

        # Sync junction tables: delete all, re-insert
        pid = str(project.id)
        self._session.query(ProjectPlaceModel).filter(
            ProjectPlaceModel.project_id == pid
        ).delete()
        self._session.query(ProjectTripModel).filter(
            ProjectTripModel.project_id == pid
        ).delete()
        self._session.query(ProjectRegionModel).filter(
            ProjectRegionModel.project_id == pid
        ).delete()

        for place_id in project.place_ids:
            self._session.add(
                ProjectPlaceModel(project_id=pid, place_id=str(place_id))
            )
        for trip_id in project.trip_ids:
            self._session.add(
                ProjectTripModel(project_id=pid, trip_id=str(trip_id))
            )
        for region_id in project.region_ids:
            self._session.add(
                ProjectRegionModel(project_id=pid, region_id=str(region_id))
            )
        self._session.commit()
        return project

    def delete(self, project_id: UUID) -> None:
        pid = str(project_id)
        self._session.query(ProjectPlaceModel).filter(
            ProjectPlaceModel.project_id == pid
        ).delete()
        self._session.query(ProjectTripModel).filter(
            ProjectTripModel.project_id == pid
        ).delete()
        self._session.query(ProjectRegionModel).filter(
            ProjectRegionModel.project_id == pid
        ).delete()
        model = self._session.get(ProjectModel, pid)
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: ProjectModel) -> Project:
        pid = str(model.id)
        place_ids = [
            UUID(str(row.place_id))
            for row in self._session.query(ProjectPlaceModel).filter(
                ProjectPlaceModel.project_id == pid
            ).all()
        ]
        trip_ids = [
            UUID(str(row.trip_id))
            for row in self._session.query(ProjectTripModel).filter(
                ProjectTripModel.project_id == pid
            ).all()
        ]
        region_ids = [
            UUID(str(row.region_id))
            for row in self._session.query(ProjectRegionModel).filter(
                ProjectRegionModel.project_id == pid
            ).all()
        ]
        config_str = str(model.config) if model.config else None
        config: dict[str, object] = json.loads(config_str) if config_str else {}
        return Project(
            id=UUID(str(model.id)),
            name=str(model.name),
            map_type=MapType(str(model.map_type)),
            description=str(model.description) if model.description else None,
            config=config,
            place_ids=place_ids,
            trip_ids=trip_ids,
            region_ids=region_ids,
        )


class SqlPhotoRepository:
    """SQLAlchemy-backed PhotoRepository implementation."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, photo_id: UUID) -> Photo | None:
        model = self._session.get(PhotoModel, str(photo_id))
        if model is None:
            return None
        return self._to_entity(model)

    def list_by_trip(self, trip_id: UUID) -> list[Photo]:
        models = (
            self._session.query(PhotoModel)
            .filter(PhotoModel.trip_id == str(trip_id))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, photo: Photo) -> Photo:
        existing = self._session.get(PhotoModel, str(photo.id))
        if existing is not None:
            existing.file_path = photo.file_path
            existing.latitude = photo.latitude
            existing.longitude = photo.longitude
            existing.taken_at = _dt_to_str(photo.taken_at)
            existing.place_id = str(photo.place_id) if photo.place_id else None
            existing.trip_id = str(photo.trip_id) if photo.trip_id else None
        else:
            model = PhotoModel(
                id=str(photo.id),
                file_path=photo.file_path,
                latitude=photo.latitude,
                longitude=photo.longitude,
                taken_at=_dt_to_str(photo.taken_at),
                place_id=str(photo.place_id) if photo.place_id else None,
                trip_id=str(photo.trip_id) if photo.trip_id else None,
            )
            self._session.add(model)
        self._session.commit()
        return photo

    def delete(self, photo_id: UUID) -> None:
        model = self._session.get(PhotoModel, str(photo_id))
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: PhotoModel) -> Photo:
        return Photo(
            id=UUID(str(model.id)),
            file_path=str(model.file_path),
            latitude=float(model.latitude) if model.latitude is not None else None,
            longitude=float(model.longitude) if model.longitude is not None else None,
            taken_at=_str_to_dt(str(model.taken_at) if model.taken_at else None),
            place_id=UUID(str(model.place_id)) if model.place_id else None,
            trip_id=UUID(str(model.trip_id)) if model.trip_id else None,
        )
