"""Tests for CLI scaffold and serve command."""

from __future__ import annotations

from typer.testing import CliRunner

from voyages.cli import app

runner = CliRunner()


def test_help_shows_voyages_description() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "travel cartography" in result.output


def test_serve_help_shows_port_option() -> None:
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "--port" in result.output
    assert "--host" in result.output
