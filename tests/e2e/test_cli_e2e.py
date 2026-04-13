"""End-to-end CLI tests that invoke idrisi as a subprocess."""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/places")
            with urllib.request.urlopen(req, timeout=2):  # noqa: S310
                return
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            time.sleep(0.3)
    msg = f"Server did not start on port {port} within {timeout}s"
    raise TimeoutError(msg)


@pytest.mark.e2e
class TestCliE2E:
    """Subprocess-level E2E tests for the Idrisi CLI."""

    def test_trip_create_and_list(self, tmp_path: Path) -> None:
        base_cmd = [sys.executable, "-m", "idrisi"]
        create = subprocess.run(  # noqa: S603
            [*base_cmd, "trip", "create", "Summer 2025"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        assert create.returncode == 0
        assert "Created trip" in create.stdout

        lst = subprocess.run(  # noqa: S603
            [*base_cmd, "trip", "list"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        assert lst.returncode == 0
        assert "Summer 2025" in lst.stdout

    def test_project_create_list_show(self, tmp_path: Path) -> None:
        base_cmd = [sys.executable, "-m", "idrisi"]
        create = subprocess.run(  # noqa: S603
            [*base_cmd, "project", "create", "My Map"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        assert create.returncode == 0

        lst = subprocess.run(  # noqa: S603
            [*base_cmd, "project", "list"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        assert lst.returncode == 0
        assert "My Map" in lst.stdout

        show = subprocess.run(  # noqa: S603
            [*base_cmd, "project", "show", "My Map"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        assert show.returncode == 0
        assert "My Map" in show.stdout

    def test_render_travel_map(self, tmp_path: Path) -> None:
        base_cmd = [sys.executable, "-m", "idrisi"]
        subprocess.run(  # noqa: S603
            [*base_cmd, "place", "add", "--name", "Paris", "--lat", "48.85", "--lon", "2.35"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        subprocess.run(  # noqa: S603
            [*base_cmd, "project", "create", "Travel Map", "--map-type", "travel"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=30,
            check=False,
        )
        render = subprocess.run(  # noqa: S603
            [*base_cmd, "render", "Travel Map", "--format", "png", "--output", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            timeout=60,
            check=False,
        )
        assert render.returncode == 0
        assert "Rendered" in render.stdout

    def test_serve_starts_and_responds(self, tmp_path: Path) -> None:
        port = _find_free_port()
        proc = subprocess.Popen(  # noqa: S603
            [sys.executable, "-m", "idrisi", "serve", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=tmp_path,
        )
        try:
            _wait_for_server(port)
            assert proc.poll() is None, "Server exited prematurely"
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/places")
            with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
                assert resp.status == 200
        finally:
            proc.terminate()
            proc.wait(timeout=5)
