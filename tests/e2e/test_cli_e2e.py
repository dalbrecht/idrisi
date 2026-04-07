"""End-to-end CLI tests that invoke voyages as a subprocess."""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.e2e
class TestCliE2E:
    """Subprocess-level E2E tests for the Voyages CLI."""

    def test_trip_create_and_list(self, tmp_path: Path) -> None:
        base_cmd = [sys.executable, "-m", "voyages"]
        create = subprocess.run(  # noqa: S603
            [*base_cmd, "trip", "create", "Summer 2025"],
            capture_output=True, text=True, cwd=tmp_path, timeout=30, check=False,
        )
        assert create.returncode == 0
        assert "Created trip" in create.stdout

        lst = subprocess.run(  # noqa: S603
            [*base_cmd, "trip", "list"],
            capture_output=True, text=True, cwd=tmp_path, timeout=30, check=False,
        )
        assert lst.returncode == 0
        assert "Summer 2025" in lst.stdout

    def test_project_create_list_show(self, tmp_path: Path) -> None:
        base_cmd = [sys.executable, "-m", "voyages"]
        create = subprocess.run(  # noqa: S603
            [*base_cmd, "project", "create", "My Map"],
            capture_output=True, text=True, cwd=tmp_path, timeout=30, check=False,
        )
        assert create.returncode == 0

        lst = subprocess.run(  # noqa: S603
            [*base_cmd, "project", "list"],
            capture_output=True, text=True, cwd=tmp_path, timeout=30, check=False,
        )
        assert lst.returncode == 0
        assert "My Map" in lst.stdout

        show = subprocess.run(  # noqa: S603
            [*base_cmd, "project", "show", "My Map"],
            capture_output=True, text=True, cwd=tmp_path, timeout=30, check=False,
        )
        assert show.returncode == 0
        assert "My Map" in show.stdout

    def test_render_travel_map(self, tmp_path: Path) -> None:
        base_cmd = [sys.executable, "-m", "voyages"]
        subprocess.run(  # noqa: S603
            [*base_cmd, "place", "add", "--name", "Paris", "--lat", "48.85", "--lon", "2.35"],
            capture_output=True, text=True, cwd=tmp_path, timeout=30, check=False,
        )
        subprocess.run(  # noqa: S603
            [*base_cmd, "project", "create", "Travel Map", "--map-type", "travel"],
            capture_output=True, text=True, cwd=tmp_path, timeout=30, check=False,
        )
        render = subprocess.run(  # noqa: S603
            [*base_cmd, "render", "Travel Map", "--format", "png", "--output", str(tmp_path)],
            capture_output=True, text=True, cwd=tmp_path, timeout=60, check=False,
        )
        assert render.returncode == 0
        assert "Rendered" in render.stdout

    def test_serve_starts_and_responds(self, tmp_path: Path) -> None:
        proc = subprocess.Popen(
            [sys.executable, "-m", "voyages", "serve", "--port", "18765"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=tmp_path,
        )
        try:
            time.sleep(3)
            assert proc.poll() is None, "Server exited prematurely"
            req = urllib.request.Request("http://127.0.0.1:18765/api/places")
            with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
                assert resp.status == 200
        finally:
            proc.terminate()
            proc.wait(timeout=5)
