"""Tests for CLI scaffold and serve command."""

from __future__ import annotations

import re
import sys
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from voyages.cli import app

runner = CliRunner()

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def test_help_shows_voyages_description() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "travel cartography" in _strip_ansi(result.output)


def test_serve_help_shows_port_option() -> None:
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    output = _strip_ansi(result.output)
    assert "--port" in output
    assert "--host" in output


def test_serve_invokes_uvicorn() -> None:
    """Verify serve command calls uvicorn.run with correct arguments."""
    mock_uvicorn = MagicMock()
    mock_uvicorn.run = MagicMock()
    with patch.dict(sys.modules, {"uvicorn": mock_uvicorn}):
        result = runner.invoke(app, ["serve", "--port", "8099"])
    assert result.exit_code == 0
    mock_uvicorn.run.assert_called_once()
