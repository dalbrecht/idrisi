"""Integration tests for OsxPhotosAdapter.

These tests require macOS with a Photos library and are marked with the macos marker.
"""

from __future__ import annotations

import sys

import pytest

pytestmark = [
    pytest.mark.skipif(sys.platform != "darwin", reason="macOS Photos.app required"),
    pytest.mark.macos,
]

if sys.platform == "darwin":
    from idrisi.infrastructure.photos.osxphotos_adapter import OsxPhotosAdapter


class TestOsxPhotosAdapter:
    def setup_method(self) -> None:
        self.adapter = OsxPhotosAdapter()

    def test_list_albums_returns_list(self) -> None:
        albums = self.adapter.list_albums()
        assert isinstance(albums, list)

    def test_list_albums_entries_have_required_fields(self) -> None:
        albums = self.adapter.list_albums()
        if not albums:
            pytest.skip("No albums in Photos library")
        album = albums[0]
        assert isinstance(album.id, str)
        assert isinstance(album.title, str)
        assert isinstance(album.photo_count, int)

    def test_get_album_photos_nonexistent_returns_empty(self) -> None:
        photos = self.adapter.get_album_photos("nonexistent-album-id-xyz")
        assert photos == []

    def test_get_album_photos_returns_geotagged_only(self) -> None:
        albums = self.adapter.list_albums()
        if not albums:
            pytest.skip("No albums in Photos library")
        photos = self.adapter.get_album_photos(albums[0].id)
        for photo in photos:
            assert photo.latitude is not None
            assert photo.longitude is not None
            assert photo.timestamp is not None
