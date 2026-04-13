from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from idrisi.domain.entities import Project
from idrisi.domain.errors import ProjectNotFoundError

if TYPE_CHECKING:
    from idrisi.application.interfaces import ProjectRepository
    from idrisi.domain.value_objects import MapType


class ProjectService:
    """Application service for managing Projects."""

    def __init__(self, project_repo: ProjectRepository) -> None:
        self._project_repo = project_repo

    def create(
        self,
        name: str,
        map_type: MapType,
        description: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> Project:
        """Create a new Project and persist it."""
        project = Project(
            id=uuid.uuid4(),
            name=name,
            map_type=map_type,
            description=description,
            config=config if config is not None else {},
        )
        return self._project_repo.save(project)

    def get(self, project_id: uuid.UUID) -> Project | None:
        """Return the Project with the given ID, or None if not found."""
        return self._project_repo.get(project_id)

    def get_by_name(self, name: str) -> Project | None:
        """Return the Project with the given name, or None if not found."""
        return self._project_repo.get_by_name(name)

    def list_all(self) -> list[Project]:
        """Return all stored Projects."""
        return self._project_repo.list_all()

    def add_place(self, project_id: uuid.UUID, place_id: uuid.UUID) -> Project:
        """Add a place to the project, avoiding duplicates."""
        project = self._project_repo.get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        if place_id not in project.place_ids:
            project.place_ids.append(place_id)
        return self._project_repo.save(project)

    def add_trip(self, project_id: uuid.UUID, trip_id: uuid.UUID) -> Project:
        """Add a trip to the project, avoiding duplicates."""
        project = self._project_repo.get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        if trip_id not in project.trip_ids:
            project.trip_ids.append(trip_id)
        return self._project_repo.save(project)

    def add_region(self, project_id: uuid.UUID, region_id: uuid.UUID) -> Project:
        """Add a region to the project, avoiding duplicates."""
        project = self._project_repo.get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        if region_id not in project.region_ids:
            project.region_ids.append(region_id)
        return self._project_repo.save(project)

    def update_config(self, project_id: uuid.UUID, config: dict[str, Any]) -> Project:
        """Replace the project's config dict and persist it."""
        project = self._project_repo.get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        project.config = config
        return self._project_repo.save(project)

    def delete(self, project_id: uuid.UUID) -> None:
        """Delete the Project with the given ID."""
        self._project_repo.delete(project_id)
