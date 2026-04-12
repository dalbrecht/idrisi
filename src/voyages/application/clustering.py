"""Photo clustering using DBSCAN with haversine distance."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from sklearn.cluster import DBSCAN

from voyages.domain.value_objects import PhotoCluster

if TYPE_CHECKING:
    from collections.abc import Sequence

    from voyages.domain.value_objects import GeotaggedPhoto

_EARTH_RADIUS_KM = 6371.0


def cluster_photos(
    photos: Sequence[GeotaggedPhoto],
    eps_km: float = 0.5,
    min_samples: int = 1,
) -> list[PhotoCluster]:
    """Cluster geotagged photos by geographic proximity using DBSCAN.

    Photos are sorted chronologically first. Clusters are returned ordered
    by the earliest timestamp in each cluster. Noise points (if min_samples > 1)
    are treated as single-photo clusters.

    Args:
        photos: Sequence of geotagged photos to cluster.
        eps_km: Maximum distance in kilometers between photos in a cluster.
        min_samples: Minimum number of photos to form a dense cluster.

    Returns:
        List of PhotoCluster objects ordered by earliest timestamp.
    """
    if not photos:
        return []

    if eps_km <= 0:
        msg = f"eps_km must be positive, got {eps_km}"
        raise ValueError(msg)
    if min_samples < 1:
        msg = f"min_samples must be >= 1, got {min_samples}"
        raise ValueError(msg)

    sorted_photos = sorted(photos, key=lambda p: p.timestamp)

    coords_rad = np.array(
        [[math.radians(p.latitude), math.radians(p.longitude)] for p in sorted_photos]
    )

    eps_rad = eps_km / _EARTH_RADIUS_KM

    db = DBSCAN(eps=eps_rad, min_samples=min_samples, metric="haversine")
    labels: np.ndarray = db.fit_predict(coords_rad)

    clusters: dict[int, list[int]] = {}
    for idx, label in enumerate(labels):
        label_int = int(label)
        if label_int == -1:
            noise_key = -(idx + 2)
            clusters[noise_key] = [idx]
        else:
            clusters.setdefault(label_int, []).append(idx)

    result: list[PhotoCluster] = []
    for indices in clusters.values():
        cluster_photos_list = [sorted_photos[i] for i in indices]
        centroid_lat = sum(p.latitude for p in cluster_photos_list) / len(cluster_photos_list)
        centroid_lon = sum(p.longitude for p in cluster_photos_list) / len(cluster_photos_list)
        earliest = min(p.timestamp for p in cluster_photos_list)
        latest = max(p.timestamp for p in cluster_photos_list)

        closest_idx = min(
            range(len(cluster_photos_list)),
            key=lambda i: (
                (cluster_photos_list[i].latitude - centroid_lat) ** 2
                + (cluster_photos_list[i].longitude - centroid_lon) ** 2
            ),
        )
        representative_path = cluster_photos_list[closest_idx].path

        result.append(
            PhotoCluster(
                centroid_lat=centroid_lat,
                centroid_lon=centroid_lon,
                photo_count=len(cluster_photos_list),
                earliest=earliest,
                latest=latest,
                representative_path=representative_path,
            )
        )

    result.sort(key=lambda c: c.earliest)
    return result
