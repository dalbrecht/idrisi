from __future__ import annotations

from datetime import UTC, datetime

import pytest

from voyages.application.clustering import cluster_photos
from voyages.domain.value_objects import GeotaggedPhoto

TOKYO_LAT = 35.6762
TOKYO_LON = 139.6503
SHINJUKU_LAT = 35.6938
SHINJUKU_LON = 139.7034
OSAKA_LAT = 34.6937
OSAKA_LON = 135.5023
KYOTO_LAT = 35.0116
KYOTO_LON = 135.7681
EXPECTED_TWO = 2
EXPECTED_THREE = 3


def _photo(lat: float, lon: float, hour: int = 10, day: int = 15) -> GeotaggedPhoto:
    """Helper to create a GeotaggedPhoto with minimal boilerplate."""
    return GeotaggedPhoto(
        latitude=lat,
        longitude=lon,
        timestamp=datetime(2024, 3, day, hour, 0, 0, tzinfo=UTC),
        path=f"/photos/{lat}_{lon}.jpg",
    )


class TestClusterPhotos:
    def test_empty_input(self) -> None:
        result = cluster_photos([])
        assert result == []

    def test_single_photo(self) -> None:
        photos = [_photo(TOKYO_LAT, TOKYO_LON)]
        result = cluster_photos(photos)
        assert len(result) == 1
        assert result[0].photo_count == 1
        assert result[0].centroid_lat == pytest.approx(TOKYO_LAT)
        assert result[0].centroid_lon == pytest.approx(TOKYO_LON)

    def test_two_nearby_photos_cluster_together(self) -> None:
        photos = [
            _photo(TOKYO_LAT, TOKYO_LON, hour=10),
            _photo(SHINJUKU_LAT, SHINJUKU_LON, hour=14),
        ]
        # Shinjuku is ~5km from central Tokyo — with a 10km eps they should cluster
        result = cluster_photos(photos, eps_km=10.0)
        assert len(result) == 1
        assert result[0].photo_count == EXPECTED_TWO

    def test_two_distant_photos_separate(self) -> None:
        photos = [
            _photo(TOKYO_LAT, TOKYO_LON, hour=10),
            _photo(OSAKA_LAT, OSAKA_LON, hour=14),
        ]
        # Tokyo to Osaka is ~400km — with default eps=0.5km they should be separate
        result = cluster_photos(photos, eps_km=0.5)
        assert len(result) == EXPECTED_TWO

    def test_clusters_ordered_by_earliest_timestamp(self) -> None:
        photos = [
            _photo(OSAKA_LAT, OSAKA_LON, hour=8, day=16),
            _photo(TOKYO_LAT, TOKYO_LON, hour=10, day=15),
        ]
        result = cluster_photos(photos, eps_km=0.5)
        assert len(result) == EXPECTED_TWO
        # Tokyo (day=15) should come first chronologically
        assert result[0].centroid_lat == pytest.approx(TOKYO_LAT)
        assert result[1].centroid_lat == pytest.approx(OSAKA_LAT)

    def test_centroid_is_mean_of_cluster(self) -> None:
        lat1, lon1 = 35.0, 139.0
        lat2, lon2 = 35.001, 139.001
        photos = [
            _photo(lat1, lon1, hour=10),
            _photo(lat2, lon2, hour=11),
        ]
        result = cluster_photos(photos, eps_km=1.0)
        assert len(result) == 1
        assert result[0].centroid_lat == pytest.approx((lat1 + lat2) / 2, abs=0.001)
        assert result[0].centroid_lon == pytest.approx((lon1 + lon2) / 2, abs=0.001)

    def test_earliest_and_latest_timestamps(self) -> None:
        early = datetime(2024, 3, 15, 8, 0, 0, tzinfo=UTC)
        late = datetime(2024, 3, 15, 18, 0, 0, tzinfo=UTC)
        photos = [
            GeotaggedPhoto(latitude=35.0, longitude=139.0, timestamp=early, path="/a.jpg"),
            GeotaggedPhoto(latitude=35.001, longitude=139.001, timestamp=late, path="/b.jpg"),
        ]
        result = cluster_photos(photos, eps_km=1.0)
        assert len(result) == 1
        assert result[0].earliest == early
        assert result[0].latest == late

    def test_representative_path_is_closest_to_centroid(self) -> None:
        photos = [
            _photo(35.0, 139.0, hour=10),
            _photo(35.0001, 139.0001, hour=11),  # closer to centroid
            _photo(35.002, 139.002, hour=12),
        ]
        result = cluster_photos(photos, eps_km=1.0)
        assert len(result) == 1
        # The middle photo is closest to the centroid
        assert result[0].representative_path == "/photos/35.0001_139.0001.jpg"

    def test_multiple_clusters_with_mixed_sizes(self) -> None:
        photos = [
            # Tokyo cluster (3 photos)
            _photo(TOKYO_LAT, TOKYO_LON, hour=9, day=15),
            _photo(TOKYO_LAT + 0.001, TOKYO_LON + 0.001, hour=10, day=15),
            _photo(TOKYO_LAT - 0.001, TOKYO_LON - 0.001, hour=11, day=15),
            # Osaka cluster (1 photo)
            _photo(OSAKA_LAT, OSAKA_LON, hour=15, day=16),
        ]
        result = cluster_photos(photos, eps_km=0.5)
        assert len(result) == EXPECTED_TWO
        assert result[0].photo_count == EXPECTED_THREE  # Tokyo
        assert result[1].photo_count == 1  # Osaka

    def test_min_samples_filters_noise_as_single_clusters(self) -> None:
        photos = [
            # Tight cluster (3 photos)
            _photo(35.0, 139.0, hour=10),
            _photo(35.0001, 139.0001, hour=11),
            _photo(35.0002, 139.0002, hour=12),
            # Isolated photo
            _photo(OSAKA_LAT, OSAKA_LON, hour=15),
        ]
        # With min_samples=1 (default), isolated photo becomes its own cluster
        result = cluster_photos(photos, eps_km=0.5, min_samples=1)
        assert len(result) == EXPECTED_TWO

    def test_custom_eps(self) -> None:
        photos = [
            _photo(TOKYO_LAT, TOKYO_LON, hour=10),
            _photo(SHINJUKU_LAT, SHINJUKU_LON, hour=14),
        ]
        # With small eps, they should be separate
        result_small = cluster_photos(photos, eps_km=0.1)
        assert len(result_small) == EXPECTED_TWO

        # With large eps, they should be together
        result_large = cluster_photos(photos, eps_km=10.0)
        assert len(result_large) == 1

    def test_negative_eps_raises(self) -> None:
        photos = [_photo(TOKYO_LAT, TOKYO_LON)]
        with pytest.raises(ValueError, match="eps_km must be positive"):
            cluster_photos(photos, eps_km=-1.0)

    def test_zero_eps_raises(self) -> None:
        photos = [_photo(TOKYO_LAT, TOKYO_LON)]
        with pytest.raises(ValueError, match="eps_km must be positive"):
            cluster_photos(photos, eps_km=0.0)

    def test_min_samples_zero_raises(self) -> None:
        photos = [_photo(TOKYO_LAT, TOKYO_LON)]
        with pytest.raises(ValueError, match="min_samples must be >= 1"):
            cluster_photos(photos, min_samples=0)
