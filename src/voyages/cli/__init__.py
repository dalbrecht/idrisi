"""Voyages CLI — Typer-based command-line interface."""

from __future__ import annotations

import typer

from voyages.cli.serve_command import serve

app = typer.Typer(
    name="voyages",
    help="A Python map generation toolbox for travel cartography.",
    no_args_is_help=True,
)

# Register top-level commands
app.command()(serve)
