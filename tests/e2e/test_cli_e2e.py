"""End-to-end tests that invoke the voyages CLI as a subprocess."""
from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest


@pytest.mark.e2e
class TestCliE2E:
    """Test CLI commands via subprocess with real SQLite database."""

    def test_place_add_and_list(self, tmp_path: Path) -> None:
        base_cmd = [sys.executable, "-m", "voyages"]

        add_result = subprocess.run(  # noqa: S603
            [*base_cmd, "place", "add", "--name", "Paris", "--lat", "48.8566", "--lon", "2.3522"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        assert add_result.returncode == 0
        assert "Created place" in add_result.stdout

        list_result = subprocess.run(  # noqa: S603
            [*base_cmd, "place", "list"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        assert list_result.returncode == 0
        assert "Paris" in list_result.stdout

    def test_render_nonexistent_project(self, tmp_path: Path) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "voyages", "render", "nonexistent"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        assert result.returncode != 0

    def test_help_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "voyages", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        assert result.returncode == 0
        assert "voyages" in result.stdout.lower() or "usage" in result.stdout.lower()
