from __future__ import annotations

import uuid

import pytest

from idrisi.domain.errors import (
    BadRequestError,
    EntityNotFoundError,
    PhotoNotFoundError,
    PlaceNotFoundError,
    ProjectNotFoundError,
    RegionNotFoundError,
    RenderError,
    TripNotFoundError,
    VoyagesError,
)


class TestVoyagesError:
    def test_is_exception(self) -> None:
        assert issubclass(VoyagesError, Exception)

    def test_can_be_raised(self) -> None:
        with pytest.raises(VoyagesError):
            raise VoyagesError("something went wrong")

    def test_message(self) -> None:
        err = VoyagesError("test message")
        assert str(err) == "test message"


class TestEntityNotFoundError:
    def test_inherits_voyages_error(self) -> None:
        assert issubclass(EntityNotFoundError, VoyagesError)

    def test_message_contains_entity_type(self) -> None:
        entity_id = uuid.uuid4()
        err = EntityNotFoundError(entity_type="Place", entity_id=entity_id)
        assert "Place" in str(err)

    def test_message_contains_entity_id(self) -> None:
        entity_id = uuid.uuid4()
        err = EntityNotFoundError(entity_type="Trip", entity_id=entity_id)
        assert str(entity_id) in str(err)

    def test_entity_type_attribute(self) -> None:
        entity_id = uuid.uuid4()
        err = EntityNotFoundError(entity_type="Region", entity_id=entity_id)
        assert err.entity_type == "Region"

    def test_entity_id_attribute(self) -> None:
        entity_id = uuid.uuid4()
        err = EntityNotFoundError(entity_type="Place", entity_id=entity_id)
        assert err.entity_id == entity_id


class TestPlaceNotFoundError:
    def test_inherits_entity_not_found(self) -> None:
        assert issubclass(PlaceNotFoundError, EntityNotFoundError)

    def test_inherits_voyages_error(self) -> None:
        assert issubclass(PlaceNotFoundError, VoyagesError)

    def test_entity_type_is_place(self) -> None:
        entity_id = uuid.uuid4()
        err = PlaceNotFoundError(entity_id=entity_id)
        assert err.entity_type == "Place"

    def test_message_contains_place_and_id(self) -> None:
        entity_id = uuid.uuid4()
        err = PlaceNotFoundError(entity_id=entity_id)
        assert "Place" in str(err)
        assert str(entity_id) in str(err)

    def test_can_be_caught_as_entity_not_found(self) -> None:
        entity_id = uuid.uuid4()
        with pytest.raises(EntityNotFoundError):
            raise PlaceNotFoundError(entity_id=entity_id)

    def test_can_be_caught_as_voyages_error(self) -> None:
        entity_id = uuid.uuid4()
        with pytest.raises(VoyagesError):
            raise PlaceNotFoundError(entity_id=entity_id)


class TestTripNotFoundError:
    def test_inherits_entity_not_found(self) -> None:
        assert issubclass(TripNotFoundError, EntityNotFoundError)

    def test_entity_type_is_trip(self) -> None:
        entity_id = uuid.uuid4()
        err = TripNotFoundError(entity_id=entity_id)
        assert err.entity_type == "Trip"

    def test_message_contains_trip_and_id(self) -> None:
        entity_id = uuid.uuid4()
        err = TripNotFoundError(entity_id=entity_id)
        assert "Trip" in str(err)
        assert str(entity_id) in str(err)


class TestProjectNotFoundError:
    def test_inherits_entity_not_found(self) -> None:
        assert issubclass(ProjectNotFoundError, EntityNotFoundError)

    def test_entity_type_is_project(self) -> None:
        entity_id = uuid.uuid4()
        err = ProjectNotFoundError(entity_id=entity_id)
        assert err.entity_type == "Project"

    def test_message_contains_project_and_id(self) -> None:
        entity_id = uuid.uuid4()
        err = ProjectNotFoundError(entity_id=entity_id)
        assert "Project" in str(err)
        assert str(entity_id) in str(err)


class TestRegionNotFoundError:
    def test_inherits_entity_not_found(self) -> None:
        assert issubclass(RegionNotFoundError, EntityNotFoundError)

    def test_entity_type_is_region(self) -> None:
        entity_id = uuid.uuid4()
        err = RegionNotFoundError(entity_id=entity_id)
        assert err.entity_type == "Region"

    def test_message_contains_region_and_id(self) -> None:
        entity_id = uuid.uuid4()
        err = RegionNotFoundError(entity_id=entity_id)
        assert "Region" in str(err)
        assert str(entity_id) in str(err)


class TestBadRequestError:
    def test_inherits_voyages_error(self) -> None:
        assert issubclass(BadRequestError, VoyagesError)

    def test_message(self) -> None:
        err = BadRequestError("Invalid UUID: abc")
        assert "Invalid UUID" in str(err)


class TestPhotoNotFoundError:
    def test_inherits_entity_not_found(self) -> None:
        assert issubclass(PhotoNotFoundError, EntityNotFoundError)

    def test_entity_type_is_photo(self) -> None:
        entity_id = uuid.uuid4()
        err = PhotoNotFoundError(entity_id=entity_id)
        assert err.entity_type == "Photo"

    def test_message_contains_photo_and_id(self) -> None:
        entity_id = uuid.uuid4()
        err = PhotoNotFoundError(entity_id=entity_id)
        assert "Photo" in str(err)
        assert str(entity_id) in str(err)


class TestRenderError:
    def test_inherits_voyages_error(self) -> None:
        assert issubclass(RenderError, VoyagesError)

    def test_can_be_raised(self) -> None:
        with pytest.raises(RenderError):
            raise RenderError("render failed")

    def test_message(self) -> None:
        err = RenderError("render failed: out of memory")
        assert "render failed" in str(err)
