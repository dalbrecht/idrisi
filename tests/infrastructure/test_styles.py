from __future__ import annotations

import tempfile
from typing import TYPE_CHECKING

import pytest
import yaml

if TYPE_CHECKING:
    from pathlib import Path

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

    def test_missing_yaml_field_raises(self, tmp_path: Path) -> None:
        """Style YAML missing a required field should raise an error."""
        style_file = tmp_path / "incomplete.yml"
        style_file.write_text("name: incomplete\nocean: '#000'\n")
        with pytest.raises((KeyError, TypeError)):
            load_style(str(style_file))

    def test_invalid_yaml_syntax_raises(self, tmp_path: Path) -> None:
        """Malformed YAML should raise an error."""
        style_file = tmp_path / "bad.yml"
        style_file.write_text("name: bad\nocean: [invalid\n")
        with pytest.raises(yaml.YAMLError):
            load_style(str(style_file))

    def test_all_builtin_styles_have_all_fields(self) -> None:
        """Every built-in style should have all MapStyle fields populated."""
        for style in get_builtin_styles():
            assert style.name is not None
            assert style.ocean is not None
            assert style.land is not None
            assert style.visited is not None
            assert style.visited_light is not None
            assert style.route is not None
            assert style.font is not None
            assert style.borders is not None
            assert style.marker is not None
            assert style.marker_size > 0
            assert style.title_size > 0
            assert style.label_size > 0


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
