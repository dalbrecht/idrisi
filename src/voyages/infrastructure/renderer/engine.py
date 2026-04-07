from __future__ import annotations

from typing import TYPE_CHECKING, Any

import matplotlib

matplotlib.use("Agg")

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from voyages.domain.value_objects import OutputFormat

if TYPE_CHECKING:
    from voyages.domain.entities import Place, Region, Trip
    from voyages.infrastructure.renderer.styles import MapStyle

FORMAT_MAP: dict[OutputFormat, str] = {
    OutputFormat.SVG: "svg",
    OutputFormat.PDF: "pdf",
    OutputFormat.PNG: "png",
    OutputFormat.EPS: "eps",
    OutputFormat.WEBP: "png",
}


class RenderEngine:
    """Cartopy-based map rendering engine."""

    def __init__(self, style: MapStyle) -> None:
        self._style = style

    # ------------------------------------------------------------------
    # Public render methods
    # ------------------------------------------------------------------

    def render_travel_map(  # pragma: no cover
        self,
        places: list[Place],
        regions: list[Region],  # noqa: ARG002
        output_path: str,
        output_format: OutputFormat,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Render a global travel map using EqualEarth projection."""
        cfg = _merge_config(config)
        dpi = int(cfg.get("dpi", 200))
        width_px = int(cfg.get("width", 1200))
        width_in = width_px / dpi
        height_in = width_in * 0.55

        fig = plt.figure(figsize=(width_in, height_in), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.EqualEarth())

        self._draw_base(ax)

        # Plot place markers
        if places:
            lons = [p.longitude for p in places]
            lats = [p.latitude for p in places]
            ax.plot(
                lons,
                lats,
                marker="o",
                color=self._style.marker,
                markersize=self._style.marker_size,
                linestyle="none",
                transform=ccrs.PlateCarree(),
            )

        self._save(fig, output_path, output_format, dpi)
        return output_path

    def render_region_map(  # pragma: no cover
        self,
        places: list[Place],
        regions: list[Region],  # noqa: ARG002
        output_path: str,
        output_format: OutputFormat,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Render a regional map with state/province boundaries."""
        cfg = _merge_config(config)
        dpi = int(cfg.get("dpi", 200))
        width_px = int(cfg.get("width", 1200))
        center_lat = float(cfg.get("center_lat", 0.0))
        center_lon = float(cfg.get("center_lon", 0.0))
        extent_deg = float(cfg.get("extent", 20))
        width_in = width_px / dpi
        height_in = width_in * 0.75

        fig = plt.figure(figsize=(width_in, height_in), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        ax.set_extent(
            [
                center_lon - extent_deg,
                center_lon + extent_deg,
                center_lat - extent_deg,
                center_lat + extent_deg,
            ],
            crs=ccrs.PlateCarree(),
        )

        self._draw_base(ax)

        # State / province boundaries
        states = cfeature.NaturalEarthFeature(
            "cultural",
            "admin_1_states_provinces_lines",
            "50m",
            edgecolor=self._style.borders,
            facecolor="none",
        )
        ax.add_feature(states, linewidth=0.5)

        # Plot place markers with labels
        if places:
            lons = [p.longitude for p in places]
            lats = [p.latitude for p in places]
            ax.plot(
                lons,
                lats,
                marker="o",
                color=self._style.marker,
                markersize=self._style.marker_size,
                linestyle="none",
                transform=ccrs.PlateCarree(),
            )
            for place in places:
                ax.text(
                    place.longitude,
                    place.latitude,
                    f" {place.name}",
                    fontsize=self._style.label_size,
                    fontfamily=self._style.font,
                    color=self._style.visited,
                    transform=ccrs.PlateCarree(),
                )

        self._save(fig, output_path, output_format, dpi)
        return output_path

    def render_route_map(  # pragma: no cover
        self,
        trip: Trip,
        places: list[Place],
        output_path: str,
        output_format: OutputFormat,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Render a route map connecting trip stops in order."""
        cfg = _merge_config(config)
        dpi = int(cfg.get("dpi", 200))
        width_px = int(cfg.get("width", 1200))
        width_in = width_px / dpi
        height_in = width_in * 0.75

        # Build ordered place list from trip stops
        place_lookup = {p.id: p for p in places}
        ordered: list[Place] = []
        for stop in sorted(trip.stops, key=lambda s: s.position):
            if stop.place_id in place_lookup:
                ordered.append(place_lookup[stop.place_id])

        fig = plt.figure(figsize=(width_in, height_in), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # Auto-calculate extent from places
        if ordered:
            lons = [p.longitude for p in ordered]
            lats = [p.latitude for p in ordered]
            pad = 2.0
            ax.set_extent(
                [
                    min(lons) - pad,
                    max(lons) + pad,
                    min(lats) - pad,
                    max(lats) + pad,
                ],
                crs=ccrs.PlateCarree(),
            )

        self._draw_base(ax)

        # Draw route polyline
        _min_stops_for_route = 2
        if len(ordered) >= _min_stops_for_route:
            route_lons = [p.longitude for p in ordered]
            route_lats = [p.latitude for p in ordered]
            ax.plot(
                route_lons,
                route_lats,
                color=self._style.route,
                linewidth=2,
                transform=ccrs.PlateCarree(),
                zorder=5,
            )

        # Numbered stop markers
        for i, place in enumerate(ordered, start=1):
            ax.plot(
                place.longitude,
                place.latitude,
                marker="o",
                color=self._style.marker,
                markersize=self._style.marker_size + 2,
                transform=ccrs.PlateCarree(),
                zorder=6,
            )
            ax.text(
                place.longitude,
                place.latitude,
                f" {i}",
                fontsize=self._style.label_size,
                fontfamily=self._style.font,
                fontweight="bold",
                color=self._style.visited,
                transform=ccrs.PlateCarree(),
                zorder=7,
            )

        self._save(fig, output_path, output_format, dpi)
        return output_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _draw_base(self, ax: Any) -> None:  # pragma: no cover
        """Add ocean, land, borders, coastlines, and lakes to an axes."""
        ax.set_facecolor(self._style.ocean)
        ax.add_feature(
            cfeature.LAND,
            facecolor=self._style.land,
            edgecolor="none",
        )
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor=self._style.borders)
        ax.add_feature(
            cfeature.BORDERS,
            linewidth=0.3,
            edgecolor=self._style.borders,
        )
        ax.add_feature(cfeature.LAKES, facecolor=self._style.ocean, edgecolor=self._style.borders)

    @staticmethod
    def _save(  # pragma: no cover
        fig: Any,
        output_path: str,
        output_format: OutputFormat,
        dpi: int,
    ) -> None:
        """Save figure to disk and close it."""
        fmt = FORMAT_MAP.get(output_format, "png")
        fig.savefig(output_path, format=fmt, dpi=dpi, bbox_inches="tight")
        plt.close(fig)


def _merge_config(config: dict[str, Any] | None) -> dict[str, Any]:
    """Return config with sensible defaults filled in."""
    defaults: dict[str, Any] = {
        "dpi": 200,
        "width": 1200,
        "center_lat": 0.0,
        "center_lon": 0.0,
        "extent": 20,
    }
    if config:
        defaults.update(config)
    return defaults
