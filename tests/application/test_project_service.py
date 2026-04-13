from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest

from idrisi.application.project_service import ProjectService
from idrisi.domain.errors import ProjectNotFoundError
from idrisi.domain.value_objects import MapType

if TYPE_CHECKING:
    from idrisi.domain.entities import Project

PLACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TRIP_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
REGION_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
EXPECTED_TWO = 2


class FakeProjectRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Project] = {}

    def get(self, project_id: uuid.UUID) -> Project | None:
        return self._store.get(project_id)

    def get_by_name(self, name: str) -> Project | None:
        for project in self._store.values():
            if project.name == name:
                return project
        return None

    def list_all(self) -> list[Project]:
        return list(self._store.values())

    def save(self, project: Project) -> Project:
        self._store[project.id] = project
        return project

    def delete(self, project_id: uuid.UUID) -> None:
        self._store.pop(project_id, None)


class TestProjectService:
    def setup_method(self) -> None:
        self.repo = FakeProjectRepository()
        self.service = ProjectService(project_repo=self.repo)

    def test_create_returns_project(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        assert project.name == "My Map"
        assert project.map_type is MapType.TRAVEL
        assert project.id is not None
        assert project.place_ids == []
        assert project.trip_ids == []
        assert project.region_ids == []
        assert project.config == {}

    def test_create_with_optional_fields(self) -> None:
        project = self.service.create(
            name="My Map",
            map_type=MapType.REGION,
            description="A detailed map",
            config={"zoom": 5},
        )
        assert project.description == "A detailed map"
        assert project.config == {"zoom": 5}

    def test_create_saves_to_repo(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        assert self.repo.get(project.id) is not None

    def test_get_existing(self) -> None:
        created = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        fetched = self.service.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_nonexistent_returns_none(self) -> None:
        result = self.service.get(uuid.uuid4())
        assert result is None

    def test_get_by_name_existing(self) -> None:
        self.service.create(name="My Map", map_type=MapType.TRAVEL)
        fetched = self.service.get_by_name("My Map")
        assert fetched is not None
        assert fetched.name == "My Map"

    def test_get_by_name_nonexistent_returns_none(self) -> None:
        result = self.service.get_by_name("Nonexistent Map")
        assert result is None

    def test_list_all_empty(self) -> None:
        assert self.service.list_all() == []

    def test_list_all_returns_all_projects(self) -> None:
        self.service.create(name="Map 1", map_type=MapType.TRAVEL)
        self.service.create(name="Map 2", map_type=MapType.ROUTE)
        assert len(self.service.list_all()) == EXPECTED_TWO

    def test_add_place_to_project(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        updated = self.service.add_place(project.id, PLACE_ID)
        assert PLACE_ID in updated.place_ids

    def test_add_place_avoids_duplicates(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        self.service.add_place(project.id, PLACE_ID)
        updated = self.service.add_place(project.id, PLACE_ID)
        assert updated.place_ids.count(PLACE_ID) == 1

    def test_add_place_project_not_found_raises(self) -> None:
        with pytest.raises(ProjectNotFoundError):
            self.service.add_place(uuid.uuid4(), PLACE_ID)

    def test_add_trip_to_project(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        updated = self.service.add_trip(project.id, TRIP_ID)
        assert TRIP_ID in updated.trip_ids

    def test_add_trip_avoids_duplicates(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        self.service.add_trip(project.id, TRIP_ID)
        updated = self.service.add_trip(project.id, TRIP_ID)
        assert updated.trip_ids.count(TRIP_ID) == 1

    def test_add_trip_project_not_found_raises(self) -> None:
        with pytest.raises(ProjectNotFoundError):
            self.service.add_trip(uuid.uuid4(), TRIP_ID)

    def test_add_region_to_project(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        updated = self.service.add_region(project.id, REGION_ID)
        assert REGION_ID in updated.region_ids

    def test_add_region_avoids_duplicates(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        self.service.add_region(project.id, REGION_ID)
        updated = self.service.add_region(project.id, REGION_ID)
        assert updated.region_ids.count(REGION_ID) == 1

    def test_add_region_project_not_found_raises(self) -> None:
        with pytest.raises(ProjectNotFoundError):
            self.service.add_region(uuid.uuid4(), REGION_ID)

    def test_update_config(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        updated = self.service.update_config(project.id, {"zoom": 8, "style": "dark"})
        assert updated.config == {"zoom": 8, "style": "dark"}

    def test_update_config_persists(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        self.service.update_config(project.id, {"zoom": 8})
        fetched = self.repo.get(project.id)
        assert fetched is not None
        assert fetched.config == {"zoom": 8}

    def test_update_config_project_not_found_raises(self) -> None:
        with pytest.raises(ProjectNotFoundError):
            self.service.update_config(uuid.uuid4(), {"zoom": 5})

    def test_delete_removes_project(self) -> None:
        project = self.service.create(name="My Map", map_type=MapType.TRAVEL)
        self.service.delete(project.id)
        assert self.repo.get(project.id) is None

    def test_delete_nonexistent_does_not_raise(self) -> None:
        self.service.delete(uuid.uuid4())  # should not raise
