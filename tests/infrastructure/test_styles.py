from __future__ import annotations

import tempfile

import pytest

from voyages.infrastructure.renderer.styles import MapStyle, get_builtin_styles, load_style


class TestLoadStyle:
    """Tests for loading built-in and custom styles."""

    def test_load_default(self) -> None:
        style = load_style("default")
        assert isinstance(style, MapStyle)
        assert style.name == "default"
        assert style.ocean == "#ACBEBE"
        assert style.marker_size == 4

    def test_load_vintage(self) -> None:
        style = load_style("vintage")
        assert style.name == "vintage"
        assert style.ocean == "#D4E4ED"
        assert style.font == "Playfair Display"

    def test_load_minimal(self) -> None:
        style = load_style("minimal")
        assert style.name == "minimal"
        assert style.ocean == "#FFFFFF"
        assert style.marker_size == 3

    def test_load_dark(self) -> None:
        style = load_style("dark")
        assert style.name == "dark"
        assert style.ocean == "#1A1A2E"
        assert style.visited == "#E94560"

    def test_load_custom_yaml(self) -> None:
        custom_yaml = """\
name: custom
ocean: "#000000"
land: "#111111"
visited: "#222222"
visited_light: "#333333"
route: "#444444"
font: "Arial"
borders: "#555555"
marker: "#666666"
marker_size: 10
title_size: 20
label_size: 12
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(custom_yaml)
            f.flush()
            style = load_style(f.name)

        assert style.name == "custom"
        assert style.ocean == "#000000"
        assert style.marker_size == 10

    def test_missing_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_style("/nonexistent/path/to/style.yml")

    def test_style_is_frozen(self) -> None:
        style = load_style("default")
        with pytest.raises(AttributeError):
            style.name = "changed"  # type: ignore[misc]


class TestGetBuiltinStyles:
    """Tests for get_builtin_styles."""

    def test_returns_four_styles(self) -> None:
        styles = get_builtin_styles()
        assert len(styles) == 4

    def test_all_are_mapstyle(self) -> None:
        styles = get_builtin_styles()
        for s in styles:
            assert isinstance(s, MapStyle)

    def test_names_match(self) -> None:
        styles = get_builtin_styles()
        names = {s.name for s in styles}
        assert names == {"default", "vintage", "minimal", "dark"}
