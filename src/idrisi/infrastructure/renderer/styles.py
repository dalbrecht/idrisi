from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_STYLES_DIR = Path(__file__).resolve().parents[4] / "styles"

_BUILTIN_NAMES: tuple[str, ...] = ("default", "vintage", "minimal", "dark")


@dataclass(frozen=True)
class MapStyle:
    """Visual style configuration for map rendering."""

    name: str
    ocean: str
    land: str
    visited: str
    visited_light: str
    route: str
    font: str
    borders: str
    marker: str
    marker_size: int
    title_size: int
    label_size: int


def _parse_style(data: dict[str, Any]) -> MapStyle:
    """Create a MapStyle from a parsed YAML dictionary."""
    return MapStyle(
        name=str(data["name"]),
        ocean=str(data["ocean"]),
        land=str(data["land"]),
        visited=str(data["visited"]),
        visited_light=str(data["visited_light"]),
        route=str(data["route"]),
        font=str(data["font"]),
        borders=str(data["borders"]),
        marker=str(data["marker"]),
        marker_size=int(data["marker_size"]),
        title_size=int(data["title_size"]),
        label_size=int(data["label_size"]),
    )


def load_style(name_or_path: str) -> MapStyle:
    """Load a map style by built-in name or file path.

    If *name_or_path* matches a built-in style name (``default``,
    ``vintage``, ``minimal``, ``dark``), the corresponding YAML file
    is loaded from the ``styles/`` directory at the project root.
    Otherwise *name_or_path* is treated as a filesystem path to a
    custom YAML style file.
    """
    if name_or_path in _BUILTIN_NAMES:
        path = _STYLES_DIR / f"{name_or_path}.yml"
    else:
        path = Path(name_or_path)

    if not path.exists():
        msg = f"Style file not found: {path}"
        raise FileNotFoundError(msg)

    raw = yaml.safe_load(path.read_text())
    if not isinstance(raw, dict):
        msg = f"Expected a YAML mapping in {path}, got {type(raw).__name__}"
        raise TypeError(msg)
    return _parse_style(raw)


def get_builtin_styles() -> list[MapStyle]:
    """Return all four built-in map styles."""
    return [load_style(name) for name in _BUILTIN_NAMES]
